from pydantic import BaseModel, EmailStr, Field

from typing import Optional


class UserRegister(BaseModel):
    """注册请求体"""

    username: str = Field(..., min_length=3, max_length=50, examples=["zhangsan"])
    email: EmailStr = Field(..., examples=["zhangsan@example.com"])
    password: str = Field(..., min_length=6, max_length=128, examples=["SecurePass123!"])


class UserLogin(BaseModel):
    """登录请求体"""

    username: str = Field(..., min_length=3, max_length=50, examples=["zhangsan"])
    password: str = Field(..., examples=["SecurePass123!"])


class UserOut(BaseModel):
    """用户响应体（不包含敏感信息）"""

    id: int
    username: str
    email: str
    avatar_url: Optional[str] = None
    created_at: Optional[str] = None

    model_config = {"from_attributes": True}


class TokenOut(BaseModel):
    """登录/注册成功后的 token 响应"""

    user: UserOut
    token: str
