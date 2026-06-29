from pydantic import BaseModel, Field
from typing import Optional


class TagCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=30)
    color: Optional[str] = Field(None, max_length=20)


class TagOut(BaseModel):
    id: int
    name: str
    color: Optional[str] = None

    model_config = {"from_attributes": True}
