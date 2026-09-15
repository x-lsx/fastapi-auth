from fastapi import APIRouter, Body, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.postgres import get_db
from ..db.redis import get_redis
from ..services.auth import AuthService
from ..schemas.token import TokenResponse, RefreshTokenRequest
from ..schemas.user import UserCreate, UserLogin, UserChangePassword, UserResetPasswordRequest, UserForgotPasswordRequest
from ..core.dependencies import get_current_user
router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db), redis=Depends(get_redis)):
    auth_service = AuthService(db, redis)
    return await auth_service.register_user(user_data)


@router.post("/login", response_model=TokenResponse)
async def login(user_login: UserLogin, db: AsyncSession = Depends(get_db), redis=Depends(get_redis)):
    auth_service = AuthService(db, redis)
    return await auth_service.authenticate_user(user_login.email, user_login.password)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest, db: AsyncSession = Depends(get_db), redis=Depends(get_redis)):
    auth_service = AuthService(db, redis)
    return await auth_service.refresh_tokens(request.refresh_token)


@router.post("/logout")
async def logout(request: RefreshTokenRequest, db: AsyncSession = Depends(get_db), redis=Depends(get_redis)):
    auth_service = AuthService(db, redis)
    await auth_service.logout(request.refresh_token)
    return {"detail": "Logged out successfully"}


@router.get("/verify")
async def verify_email(token: str = Query(...),
                       db: AsyncSession = Depends(get_db),
                       redis=Depends(get_redis)):
    auth_service = AuthService(db, redis)
    await auth_service.verify_user(token)
    return {"detail": "Email verified successfully"}


@router.patch("/change-password")
async def change_password(
    data: UserChangePassword = Body(...),
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis)
):
    auth_service = AuthService(db, redis)

    await auth_service.change_password(user.id, data)
    return {"detail": "Password changed successfully"}


@router.post("/request-password-reset")
async def request_password_reset(
    data: UserForgotPasswordRequest = Body(...),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis)
):
    auth_service = AuthService(db, redis)
    await auth_service.request_password_reset(data.email)
    return {"detail": "Password reset email sent"}

@router.post("/reset-password")
async def reset_password(
    data: UserResetPasswordRequest = Body(...),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis)
):
    auth_service = AuthService(db, redis)
    await auth_service.confirm_reset_password(data.email, data.new_password)
    return {"detail": "Password reset email sent"}