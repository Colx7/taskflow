from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.tag import Tag
from app.schemas.tag import TagCreate, TagOut

router = APIRouter(
    prefix="/api/tags",
    tags=["🏷️ 标签管理"],
    responses={404: {"description": "标签未找到"}},
)


@router.get("", response_model=list[TagOut], summary="获取所有标签", description="获取系统中所有标签")
async def list_tags(db: AsyncSession = Depends(get_db)):
    """获取所有标签"""
    result = await db.execute(select(Tag).order_by(Tag.created_at.desc()))
    return result.scalars().all()


@router.post("", response_model=TagOut, status_code=status.HTTP_201_CREATED, summary="创建标签", description="新建一个标签")
async def create_tag(data: TagCreate, db: AsyncSession = Depends(get_db)):
    """创建标签"""
    existing = await db.execute(select(Tag).where(Tag.name == data.name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="标签名称已存在")

    tag = Tag(**data.model_dump())
    db.add(tag)
    await db.flush()
    await db.refresh(tag)
    return tag


@router.delete("/{tag_id}", summary="删除标签", description="删除指定标签")
async def delete_tag(tag_id: int, db: AsyncSession = Depends(get_db)):
    """删除标签"""
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalar_one_or_none()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")

    await db.delete(tag)
    await db.flush()
    return {"message": "标签已删除"}
