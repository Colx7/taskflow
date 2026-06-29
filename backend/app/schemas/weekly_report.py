"""AI 周报请求/响应 schemas"""

from pydantic import BaseModel, Field
from typing import Optional


class WeeklyReportRequest(BaseModel):
    """周报生成请求"""
    start_date: str = Field(alias="startDate", description="开始日期 YYYY-MM-DD")
    end_date: str = Field(alias="endDate", description="结束日期 YYYY-MM-DD")

    model_config = {"populate_by_name": True}


class WeeklyReportResponse(BaseModel):
    """周报生成响应"""
    report: str = Field(..., description="生成的周报内容")
    summary: dict = Field(default_factory=dict, description="统计数据摘要")
