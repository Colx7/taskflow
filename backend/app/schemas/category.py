from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    icon: Optional[str] = Field(None, max_length=20)
    color: Optional[str] = Field(None, max_length=20)
    sort_order: int = Field(default=0, ge=0)


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    icon: Optional[str] = Field(None, max_length=20)
    color: Optional[str] = Field(None, max_length=20)
    sort_order: Optional[int] = Field(None, ge=0)


class CategoryOut(BaseModel):
    id: int
    name: str
    icon: Optional[str] = None
    color: Optional[str] = None
    sort_order: int = 0

    model_config = {"from_attributes": True}
