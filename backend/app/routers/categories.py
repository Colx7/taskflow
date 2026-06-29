from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryOut

router = APIRouter(
    prefix="/api/categories",
    tags=["📂 分类管理"],
    responses={404: {"description": "分类未找到"}},
)


@router.get("", response_model=list[CategoryOut], summary="获取所有分类", description="获取系统中所有分类，按排序字段排列")
async def list_categories(db: AsyncSession = Depends(get_db)):
    """获取所有分类"""
    result = await db.execute(select(Category).order_by(Category.sort_order))
    return result.scalars().all()


@router.post("", response_model=CategoryOut, status_code=status.HTTP_201_CREATED, summary="创建分类", description="新建一个任务分类")
async def create_category(data: CategoryCreate, db: AsyncSession = Depends(get_db)):
    """创建分类"""
    existing = await db.execute(select(Category).where(Category.name == data.name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="分类名称已存在")

    category = Category(**data.model_dump())
    db.add(category)
    await db.flush()
    await db.refresh(category)
    return category


@router.put("/{category_id}", response_model=CategoryOut, summary="更新分类", description="更新指定分类的信息")
async def update_category(category_id: int, data: CategoryUpdate, db: AsyncSession = Depends(get_db)):
    """更新分类"""
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(category, key, value)

    await db.flush()
    await db.refresh(category)
    return category


@router.delete("/{category_id}", summary="删除分类", description="删除指定分类")
async def delete_category(category_id: int, db: AsyncSession = Depends(get_db)):
    """删除分类"""
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")

    await db.delete(category)
    await db.flush()
    return {"message": "分类已删除"}
