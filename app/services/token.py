from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status, HTTPException
import secrets

from ..db.redis import Redis
from ..core.config import settings


class TokenService:
    def __init__(self, redis: Redis):
        self.redis: Redis = redis
    # refresh token methods

    async def save_refresh_token(self, user_id: int, jti: str):
        await self.redis.set(
            f"refresh_token:{jti}",
            user_id,
            ex=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60)

    async def revoke_refresh_token(self, jti: str):
        await self.redis.delete(f"refresh_token:{jti}")

    async def validate_refresh_token(self, jti: str) -> bool:
        return bool(
            await self.redis.exists(
                f"refresh_token:{jti}"
            )
        )
        
    async def revoke_all_refresh_tokens(self, user_id: int):
        keys = await self.redis.keys(f"refresh_token:*")
        for key in keys:
            token_user_id = await self.redis.get(key)
            if token_user_id and int(token_user_id) == user_id:
                await self.redis.delete(key)
                
    # verification token methods

    async def generate_verification_token(self, user_id: int) -> str:
        token = secrets.token_urlsafe(32)

        await self.redis.set(
            f"verification_token:{token}",
            user_id,
            ex=settings.VERIFICATION_TOKEN_EXPIRE_HOURS * 60 * 60
        )
        return token

    async def revoke_verification_token(self, token: str):
        await self.redis.delete(f"verification_token:{token}")

    async def get_user_id_by_verification_token(self, token: str) -> int:
        user_id = await self.redis.get(f"verification_token:{token}")
        if user_id is None:
            return None
        return int(user_id)

    # reset password token methods
    
    async def generate_password_reset_token(self, user_id: int) -> str:
        token = secrets.token_urlsafe(32)
        await self.redis.set(
            f"password_reset_token:{token}",
            user_id,
            ex=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS * 60 * 60
        )
        return token

    async def revoke_password_reset_token(self, token: str):
        await self.redis.delete(f"password_reset_token:{token}")

    async def get_user_id_by_password_reset_token(self, token: str) -> int:
        user_id = await self.redis.get(f"password_reset_token:{token}")
        if user_id is None:
            return None
        return int(user_id)
