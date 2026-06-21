from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.postgres import get_db
from ..db.redis import get_redis
from ..services.auth import AuthService
from ..schemas.token import TokenResponse, RefreshTokenRequest
from ..schemas.user import UserCreate, UserLogin

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