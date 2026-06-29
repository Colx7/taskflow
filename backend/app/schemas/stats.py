"""统计模块 Pydantic schemas"""

from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_tasks: int
    pending_count: int
    in_progress_count: int
    completed_count: int
    cancelled_count: int
    overdue_count: int
    today_completed: int
    this_week_completed: int
    by_priority: dict[str, int]
    recent_activity: list[dict]


class TrendData(BaseModel):
    labels: list[str]
    values: list[int]


class CategoryDistribution(BaseModel):
    name: str
    completed: int
    pending: int
    in_progress: int


class StatsCategoryDistribution(BaseModel):
    items: list[CategoryDistribution]
