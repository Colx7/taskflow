"""周报 API 路由"""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_current_user
from app.models.task import Task, TaskStatus, TaskPriority
from app.models.category import Category
from app.models.user import User
from app.schemas.weekly_report import WeeklyReportRequest, WeeklyReportResponse
from app.services.weekly_report_service import WeeklyReportService

router = APIRouter(
    prefix="/api/ai",
    tags=["🤖 AI 智能"],
    responses={404: {"description": "未找到"}},
)


@router.post("/weekly-report", response_model=WeeklyReportResponse, summary="生成 AI 周报", description="根据日期范围生成任务周报。AI 服务不可用时自动降级为纯文本格式。")
async def generate_weekly_report(
    data: WeeklyReportRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """生成 AI 周报"""
    uid = user.id
    start_dt = datetime.strptime(data.start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(data.end_date, "%Y-%m-%d") + timedelta(days=1, microseconds=-1)

    # 获取该时间段内的所有任务
    tasks_result = await db.execute(
        select(
            Task.id, Task.title, Task.description, Task.status, Task.priority,
            Task.category_id, Task.due_date, Task.created_at, Task.updated_at,
            Category.name.label("category_name"),
        )
        .outerjoin(Category, Task.category_id == Category.id)
        .where(
            Task.user_id == uid,
            Task.created_at >= start_dt,
            Task.created_at <= end_dt,
        )
        .order_by(Task.created_at.desc())
    )
    tasks = tasks_result.all()

    # 构建任务摘要文本
    status_map = {
        TaskStatus.pending.value: "待办",
        TaskStatus.in_progress.value: "进行中",
        TaskStatus.completed.value: "已完成",
        TaskStatus.cancelled.value: "已取消",
    }
    priority_map = {
        TaskPriority.urgent.value: "紧急",
        TaskPriority.high.value: "高",
        TaskPriority.medium.value: "中",
        TaskPriority.low.value: "低",
    }
    summary_lines = []
    for row in tasks:
        s = status_map.get(row[3].value, str(row[3]))
        p = priority_map.get(row[4].value, str(row[4]))
        cat = row[9] or "未分类"
        line = f"- [{s}] [{p}] [{cat}] {row[1]}"
        if row[2]:
            line += f" (描述: {row[2]})"
        summary_lines.append(line)
    tasks_summary = "\n".join(summary_lines) if summary_lines else "本周无任务记录。"

    # 统计摘要
    total = len(tasks)
    completed = sum(1 for t in tasks if t[3].value == "completed")
    in_progress = sum(1 for t in tasks if t[3].value == "in_progress")
    pending = sum(1 for t in tasks if t[3].value == "pending")
    cancelled = sum(1 for t in tasks if t[3].value == "cancelled")

    summary = {
        "total": total, "completed": completed, "in_progress": in_progress,
        "pending": pending, "cancelled": cancelled,
    }

    # 生成周报
    service = WeeklyReportService()
    result = await service.generate_report(data.start_date, data.end_date, tasks_summary)

    return WeeklyReportResponse(report=result["report"], summary=summary)
