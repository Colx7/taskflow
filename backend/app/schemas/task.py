from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category_id: int = Field(..., gt=0)
    due_date: Optional[date] = None
    tags: Optional[list[str]] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    category_id: Optional[int] = None
    due_date: Optional[date] = None
    tags: Optional[list[str]] = None


class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    category_id: int
    user_id: int
    due_date: Optional[date] = None
    tags: Optional[list[str]] = None
    ai_suggestion: Optional[dict] = None
    category: Optional["CategoryOut"] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    model_config = {"from_attributes": True}


# 前向引用修正
from app.schemas.category import CategoryOut
TaskOut.model_rebuild()
