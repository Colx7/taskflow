from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.auth import UserOut
from app.utils.jwt_utils import create_access_token

router = APIRouter(prefix="/api/users", tags=["用户"])


@router.get("/profile", response_model=UserOut)
async def get_profile(current_user: User = Depends(get_current_user)):
    """获取用户个人资料（需要 JWT 认证）"""
    return UserOut(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        avatar_url=current_user.avatar_url,
        created_at=str(current_user.created_at) if current_user.created_at else None,
    )
