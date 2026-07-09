import jwt
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import settings
from ..core.jwt_utils import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)

from ..core.security import hashed_password, verify_password
from ..db.redis import Redis
from ..repositories.user import UserRepository
from ..schemas.token import TokenResponse
from ..schemas.user import UserCreate, UserChangePassword
from ..services.token import TokenService
from ..tasks.test import login_debug_task
from ..tasks.send_confirmation_email import send_confirmation_email


def build_token_response(
    access_token: str,
    refresh_token: str,
) -> TokenResponse:
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        refresh_expires_in=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
    )


class AuthService:
    def __init__(self, db: AsyncSession, redis: Redis):
        self.user_repository = UserRepository(db)
        self.token_service = TokenService(redis)

    async def register_user(self, user_create: UserCreate) -> TokenResponse:
        existing_user = await self.user_repository.get_by_email(user_create.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        user_data = user_create.model_dump(exclude={"password"})
        user_data["hashed_password"] = hashed_password(user_create.password)

        new_user = await self.user_repository.create(user_data)
        await self.user_repository.db.commit()

        access_token = create_access_token(new_user.id)
        refresh_token, jti = create_refresh_token(new_user.id)

        await self.token_service.save_refresh_token(new_user.id, jti)

        token = await self.token_service.generate_verification_token(new_user.id)
        send_confirmation_email.delay(to_email=new_user.email,
                                      verify_url=f"{
                                          settings.API_URL}/auth/verify?token={token}",
                                      )

        return build_token_response(access_token, refresh_token)

    async def authenticate_user(self, email: str, password: str) -> TokenResponse:
        user = await self.user_repository.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        access_token = create_access_token(user.id)
        refresh_token, jti = create_refresh_token(user.id)

        await self.token_service.save_refresh_token(user.id, jti)

        login_debug_task(user.id, user.email)

        return build_token_response(access_token, refresh_token)

    async def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        try:
            token_data = decode_refresh_token(refresh_token)
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )
        exists = await self.token_service.validate_refresh_token(token_data.jti)
        if not exists:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has been revoked",
            )
        user = await self.user_repository.get_by_id(int(token_data.sub))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        await self.token_service.revoke_refresh_token(token_data.jti)

        new_access_token = create_access_token(user.id)
        new_refresh_token, new_jti = create_refresh_token(user.id)

        await self.token_service.save_refresh_token(user.id, new_jti)

        return build_token_response(new_access_token, new_refresh_token)

    async def logout(self, refresh_token: str):
        try:
            token_data = decode_refresh_token(refresh_token)
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )
        await self.token_service.revoke_refresh_token(token_data.jti)

    async def verify_user(self, verification_token: str):
        user_id = await self.token_service.get_user_id_by_verification_token(verification_token)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token",
            )
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        user.is_verified = True
        await self.user_repository.db.commit()
        await self.token_service.revoke_verification_token(verification_token)

    async def change_password(self, user_id: int, data: UserChangePassword):
        user = await self.user_repository.get_by_id(user_id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        if not verify_password(data.old_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid old password"
            )

        if verify_password(data.new_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be different from the old one"
            )
        hashed_new_password = hashed_password(data.new_password)
        await self.user_repository.update(
            user_id,
            {"hashed_password": hashed_new_password}
        )
        await self.user_repository.db.commit()

        await self.token_service.revoke_all_refresh_tokens(user_id)
