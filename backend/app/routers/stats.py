"""统计模块 API: 仪表盘概览、趋势、分类分布"""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.task import Task, TaskStatus
from app.models.category import Category
from app.models.user import User
from app.schemas.stats import (
    DashboardStats,
    TrendData,
    CategoryDistribution,
    StatsCategoryDistribution,
)
from app.utils.jwt_utils import decode_access_token

router = APIRouter(
    prefix="/api/stats",
    tags=["📊 数据统计"],
    responses={404: {"description": "未找到"}},
)


async def _get_user(request: Request, db: AsyncSession):
    """从 request 头手动解析 token"""
    auth = request.headers.get("authorization", "")
    if not auth.startswith("Bearer "):
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未提供认证凭证")
    token = auth[7:]
    user_id = decode_access_token(token)
    if not user_id:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的认证凭证")
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    if not user:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")
    return user


@router.get("/dashboard", response_model=DashboardStats, summary="仪表盘统计", description="获取仪表盘的完整统计数据：各状态任务数、逾期数、今日/本周完成数、优先级分布、最近活动")
async def dashboard_stats(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """仪表盘统计概览"""
    user = await _get_user(request, db)
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=7)
    uid = user.id

    total_q = await db.execute(select(func.count(Task.id)).where(Task.user_id == uid))
    total_tasks = total_q.scalar() or 0

    pending_q = await db.execute(select(func.count(Task.id)).where(Task.user_id == uid, Task.status == TaskStatus.pending))
    pending_count = pending_q.scalar() or 0

    in_progress_q = await db.execute(select(func.count(Task.id)).where(Task.user_id == uid, Task.status == TaskStatus.in_progress))
    in_progress_count = in_progress_q.scalar() or 0

    completed_q = await db.execute(select(func.count(Task.id)).where(Task.user_id == uid, Task.status == TaskStatus.completed))
    completed_count = completed_q.scalar() or 0

    cancelled_q = await db.execute(select(func.count(Task.id)).where(Task.user_id == uid, Task.status == TaskStatus.cancelled))
    cancelled_count = cancelled_q.scalar() or 0

    overdue_q = await db.execute(select(func.count(Task.id)).where(
        Task.user_id == uid, Task.status != TaskStatus.completed,
        Task.due_date.isnot(None), Task.due_date < today_start.date(),
    ))
    overdue_count = overdue_q.scalar() or 0

    today_q = await db.execute(select(func.count(Task.id)).where(
        Task.user_id == uid, Task.status == TaskStatus.completed, Task.updated_at >= today_start,
    ))
    today_completed_val = today_q.scalar() or 0

    week_q = await db.execute(select(func.count(Task.id)).where(
        Task.user_id == uid, Task.status == TaskStatus.completed, Task.updated_at >= week_start,
    ))
    this_week_completed_val = week_q.scalar() or 0

    pri_q = await db.execute(
        select(Task.priority, func.count(Task.id)).where(Task.user_id == uid).group_by(Task.priority)
    )
    by_priority = {row[0].value: row[1] for row in pri_q.all()}

    recent_q = await db.execute(
        select(Task.title, Task.status, Task.updated_at)
        .where(Task.user_id == uid).order_by(Task.updated_at.desc()).limit(10)
    )
    recent_activity = [
        {"task_title": row[0], "action": row[1].value, "time": row[2].isoformat() if row[2] else None}
        for row in recent_q.all()
    ]

    return DashboardStats(
        total_tasks=total_tasks, pending_count=pending_count,
        in_progress_count=in_progress_count, completed_count=completed_count,
        cancelled_count=cancelled_count, overdue_count=overdue_count,
        today_completed=today_completed_val, this_week_completed=this_week_completed_val,
        by_priority=by_priority, recent_activity=recent_activity,
    )


@router.get("/trend", response_model=TrendData, summary="趋势统计", description="获取任务完成/创建/逾期的趋势数据，支持按天/周/月查询")
async def trend_stats(
    request: Request,
    db: AsyncSession = Depends(get_db),
    period: str = Query(default="week", description="时间周期: day(7天) / week(7天) / month(30天)"),
    field: str = Query(default="completed", description="统计字段: completed(完成) / created(创建) / overdue(逾期)"),
):
    """趋势统计"""
    user = await _get_user(request, db)
    uid = user.id
    now = datetime.now()
    days = {"day": 7, "week": 7, "month": 30}[period]
    start_date = now - timedelta(days=days)
    conditions = [Task.user_id == uid, Task.created_at >= start_date]

    if field == "completed":
        conditions.append(Task.status == TaskStatus.completed)
        date_col = Task.updated_at
    elif field == "overdue":
        conditions.extend([Task.status != TaskStatus.completed, Task.due_date.isnot(None), Task.due_date < now.date()])
        date_col = Task.created_at
    else:
        date_col = Task.created_at

    result = await db.execute(
        select(func.date(date_col).label("day"), func.count(Task.id))
        .where(*conditions).group_by(func.date(date_col))
    )
    daily_counts = {str(row[0]): row[1] for row in result.all()}
    labels, values = [], []
    for i in range(days):
        d = start_date + timedelta(days=i)
        ds = d.strftime("%Y-%m-%d")
        labels.append(d.strftime("%m-%d"))
        values.append(daily_counts.get(ds, 0))
    return TrendData(labels=labels, values=values)


@router.get("/category-distribution", response_model=StatsCategoryDistribution, summary="分类分布", description="获取各分类的任务数量分布（已完成/待办/进行中）")
async def category_distribution(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """分类分布统计"""
    user = await _get_user(request, db)
    uid = user.id
    result = await db.execute(
        select(Category.name,
               func.count(case((Task.status == TaskStatus.completed, Task.id))).label("completed"),
               func.count(case((Task.status == TaskStatus.pending, Task.id))).label("pending"),
               func.count(case((Task.status == TaskStatus.in_progress, Task.id))).label("in_progress"),
        ).outerjoin(Task, (Category.id == Task.category_id) & (Task.user_id == uid))
        .group_by(Category.name)
    )
    items = [
        CategoryDistribution(name=row[0], completed=int(row[1] or 0), pending=int(row[2] or 0), in_progress=int(row[3] or 0))
        for row in result.all()
    ]
    return StatsCategoryDistribution(items=items)
