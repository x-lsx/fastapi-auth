from fastapi import APIRouter, Depends, status
from fastapi.param_functions import Body, Query
from sqlalchemy.ext.asyncio import AsyncSession


from ..db.redis import get_redis
from ..db.postgres import get_db
from ..core.dependencies import get_current_user
from ..services.user import UserService
router = APIRouter(
    prefix="/user",
    tags=["user"]
)


@router.get("/profile")
async def get_profile(user=Depends(get_current_user)):
    return user


# @router.post("/forgot-password")
# async def forgot_password(user=Depends(get_current_user),
#                           token: str = Query(...),
#                           db: AsyncSession = Depends(get_db),
#                           redis=Depends(get_redis)
#                           ):
#     user = 