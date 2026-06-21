from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status, HTTPException

from ..db.redis import Redis
from ..core.config import settings

class TokenService:
    def __init__(self, redis: Redis):
        self.redis: Redis = redis
        
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