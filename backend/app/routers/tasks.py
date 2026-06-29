from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.models.task import Task, TaskStatus, TaskPriority
from app.models.category import Category
from app.schemas.task import TaskCreate, TaskUpdate, TaskOut
from app.schemas.category import CategoryOut

router = APIRouter(
    prefix="/api/tasks",
    tags=["✅ 任务管理"],
    responses={404: {"description": "任务未找到"}},
)


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED, summary="创建任务", description="新建一个任务，自动关联分类和当前用户")
async def create_task(data: TaskCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """创建任务"""
    cat_result = await db.execute(select(Category).where(Category.id == data.category_id))
    if not cat_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="分类不存在")

    task = Task(
        title=data.title,
        description=data.description,
        category_id=data.category_id,
        user_id=current_user.id,
        due_date=data.due_date,
        tags=data.tags,
    )
    db.add(task)
    await db.flush()
    await db.refresh(task)

    cat_result = await db.execute(select(Category).where(Category.id == task.category_id))
    category = cat_result.scalar_one_or_none()
    return _build_task_out(task, category)


@router.get("", response_model=dict, summary="获取任务列表", description="分页获取任务列表，支持按状态/优先级/分类/关键词筛选和排序")
async def list_tasks(
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量，最大100"),
    status_filter: Optional[str] = Query(None, alias="status", description="按状态筛选: pending/in_progress/completed/cancelled"),
    priority: Optional[str] = Query(None, description="按优先级筛选: urgent/high/medium/low"),
    category_id: Optional[int] = Query(None, description="按分类ID筛选"),
    keyword: Optional[str] = Query(None, description="按标题/描述关键词搜索"),
    sort_by: str = Query("created_at", description="排序字段: created_at/due_date/priority"),
    sort_order: str = Query("desc", description="排序方向: asc/desc"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取任务列表（分页+筛选+排序）"""
    base_query = select(Task).where(Task.user_id == current_user.id)
    count_query = select(func.count(Task.id)).where(Task.user_id == current_user.id)

    if status_filter:
        try:
            base_query = base_query.where(Task.status == TaskStatus(status_filter))
            count_query = count_query.where(Task.status == TaskStatus(status_filter))
        except ValueError:
            pass

    if priority:
        try:
            base_query = base_query.where(Task.priority == TaskPriority(priority))
            count_query = count_query.where(Task.priority == TaskPriority(priority))
        except ValueError:
            pass

    if category_id:
        base_query = base_query.where(Task.category_id == category_id)
        count_query = count_query.where(Task.category_id == category_id)

    if keyword:
        like_pattern = f"%{keyword}%"
        base_query = base_query.where((Task.title.ilike(like_pattern)) | (Task.description.ilike(like_pattern)))
        count_query = count_query.where((Task.title.ilike(like_pattern)) | (Task.description.ilike(like_pattern)))

    sort_map = {"created_at": Task.created_at, "due_date": Task.due_date, "priority": Task.priority}
    sort_col = sort_map.get(sort_by, Task.created_at)
    sort_dir = sort_col.asc() if sort_order == "asc" else sort_col.desc()

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    base_query = base_query.order_by(sort_dir).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(base_query)
    tasks_list = result.scalars().all()

    categories = {}
    if tasks_list:
        cat_ids = list(set(t.category_id for t in tasks_list))
        cat_result = await db.execute(select(Category).where(Category.id.in_(cat_ids)))
        for c in cat_result.scalars().all():
            categories[c.id] = c

    items = [_build_task_out(t, categories.get(t.category_id)) for t in tasks_list]

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if total > 0 else 0,
    }


@router.get("/{task_id}", response_model=TaskOut, summary="获取任务详情", description="获取单个任务的详细信息")
async def get_task(task_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """获取任务详情"""
    result = await db.execute(select(Task).where(Task.id == task_id, Task.user_id == current_user.id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    cat_result = await db.execute(select(Category).where(Category.id == task.category_id))
    category = cat_result.scalar_one_or_none()
    return _build_task_out(task, category)


@router.put("/{task_id}", response_model=TaskOut, summary="更新任务", description="更新任务的信息（标题、描述、状态、优先级、分类、截止日、标签）")
async def update_task(task_id: int, data: TaskUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """更新任务"""
    result = await db.execute(select(Task).where(Task.id == task_id, Task.user_id == current_user.id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    update_data = data.model_dump(exclude_unset=True)
    if "status" in update_data:
        try:
            update_data["status"] = TaskStatus(update_data["status"])
        except ValueError:
            raise HTTPException(status_code=400, detail="无效的状态值，可选: pending/in_progress/completed/cancelled")
    if "priority" in update_data:
        try:
            update_data["priority"] = TaskPriority(update_data["priority"])
        except ValueError:
            raise HTTPException(status_code=400, detail="无效的优先级值，可选: urgent/high/medium/low")

    for key, value in update_data.items():
        setattr(task, key, value)

    await db.flush()
    await db.refresh(task)

    cat_result = await db.execute(select(Category).where(Category.id == task.category_id))
    category = cat_result.scalar_one_or_none()
    return _build_task_out(task, category)


@router.delete("/{task_id}", summary="删除任务", description="永久删除一个任务")
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """删除任务"""
    result = await db.execute(select(Task).where(Task.id == task_id, Task.user_id == current_user.id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    await db.delete(task)
    await db.flush()
    return {"message": "任务已删除"}


@router.patch("/batch-status", response_model=dict, summary="批量更新状态", description="一次性更新多个任务的状态")
async def batch_update_status(
    task_ids: list[int],
    status: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """批量更新任务状态"""
    try:
        status_enum = TaskStatus(status)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的状态值，可选: pending/in_progress/completed/cancelled")

    result = await db.execute(select(Task).where(Task.id.in_(task_ids), Task.user_id == current_user.id))
    tasks_list = result.scalars().all()
    for task in tasks_list:
        task.status = status_enum
    await db.flush()
    return {"message": f"已更新 {len(tasks_list)} 个任务状态"}


def _build_task_out(task: Task, category: Optional[Category] = None) -> dict:
    """构建任务响应字典"""
    cat_data = None
    if category:
        cat_data = CategoryOut(
            id=category.id, name=category.name, icon=category.icon,
            color=category.color, sort_order=category.sort_order,
        ).model_dump()

    return TaskOut(
        id=task.id, title=task.title, description=task.description,
        status=task.status.value, priority=task.priority.value,
        category_id=task.category_id, user_id=task.user_id,
        due_date=task.due_date, tags=task.tags,
        ai_suggestion=task.ai_suggestion, category=cat_data,
        created_at=str(task.created_at) if task.created_at else None,
        updated_at=str(task.updated_at) if task.updated_at else None,
    ).model_dump()
