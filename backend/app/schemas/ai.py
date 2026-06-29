from pydantic import BaseModel, Field
from typing import Optional


class TaskClassifyRequest(BaseModel):
    """AI 分类请求"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None


class TaskClassifyResponse(BaseModel):
    """AI 分类响应"""
    category: str
    priority: str
    reason: str
    suggested_tags: list[str] = Field(default_factory=list)
