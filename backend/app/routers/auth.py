from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.auth import UserLogin, UserOut, UserRegister, TokenOut
from app.utils.jwt_utils import create_access_token
from app.utils.password_utils import hash_password, verify_password

router = APIRouter(
    prefix="/api/auth",
    tags=["🔐 认证"],
    responses={404: {"description": "未找到"}},
)


@router.post(
    "/register",
    response_model=TokenOut,
    status_code=status.HTTP_201_CREATED,
    summary="用户注册",
    description="注册新账号，返回用户信息和 JWT Token",
    openapi_extra={
        "examples": {
            "注册示例": {
                "summary": "注册新用户",
                "value": {
                    "username": "新用户",
                    "password": "SecurePass123!",
                    "email": "new@example.com",
                },
            },
        },
    },
)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    """用户注册"""
    # 检查用户名是否已存在
    result = await db.execute(select(User).where(User.username == data.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已被注册",
        )

    # 检查邮箱是否已存在
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册",
        )

    # 创建用户
    user = User(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    # 生成 token
    token = create_access_token(str(user.id))

    return TokenOut(
        user=UserOut(
            id=user.id,
            username=user.username,
            email=user.email,
            avatar_url=user.avatar_url,
            created_at=str(user.created_at) if user.created_at else None,
        ),
        token=token,
    )


@router.post(
    "/login",
    response_model=TokenOut,
    summary="用户登录",
    description="使用用户名和密码登录，返回 JWT Token",
    openapi_extra={
        "examples": {
            "登录示例": {
                "summary": "登录账号",
                "value": {
                    "username": "zhangsan",
                    "password": "SecurePass123!",
                },
            },
        },
    },
)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    """用户登录"""
    # 查找用户
    result = await db.execute(select(User).where(User.username == data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    # 生成 token
    token = create_access_token(str(user.id))

    return TokenOut(
        user=UserOut(
            id=user.id,
            username=user.username,
            email=user.email,
            avatar_url=user.avatar_url,
            created_at=str(user.created_at) if user.created_at else None,
        ),
        token=token,
    )


@router.get(
    "/me",
    response_model=UserOut,
    summary="获取当前用户信息",
    description="获取当前登录用户的信息（需要 Token 认证）",
)
async def get_me(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息"""
    return UserOut(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        avatar_url=current_user.avatar_url,
        created_at=str(current_user.created_at) if current_user.created_at else None,
    )
