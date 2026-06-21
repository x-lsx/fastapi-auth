from fastapi import APIRouter, Depends, status
from fastapi.param_functions import Body
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.dependencies import get_current_user

router = APIRouter(
    prefix="/user",
    tags=["user"]
)

@router.get("/profile")
async def get_profile(user = Depends(get_current_user)):
    return user

# @router.patch("/profile")
# async def update_profile(
#     user = Depends(get_current_user),
#     user_data: Body()):
    