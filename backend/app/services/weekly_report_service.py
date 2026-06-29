"""AI 周报服务：生成每周任务总结报告"""

from datetime import datetime, timedelta
from typing import Optional


REPORT_SYSTEM_PROMPT = """你是一个专业的周报生成助手。根据用户提供的本周任务数据，
生成一份结构清晰的周报，包含以下部分：

1. 本周工作总结（概述）
2. 完成任务详情
3. 进行中的任务
4. 逾期/取消的任务
5. 下周建议

要求：
- 语言简洁专业
- 按分类归纳任务
- 突出重要和高优先级的任务
- 给出合理的下周建议"""


def build_report_prompt(start_date: str, end_date: str, tasks_summary: str) -> str:
    """构建周报生成 prompt"""
    return f"""请根据以下任务数据生成一份周报。

时间范围：{start_date} 至 {end_date}

任务数据：
{tasks_summary}

请按照以下格式生成周报：
1. 本周工作总结（一段话概述）
2. 已完成任务（按分类列出）
3. 进行中任务（按分类列出）
4. 逾期/取消任务（如有）
5. 下周建议（2-3条）

请直接输出周报内容，不要添加额外说明。"""


def build_fallback_report(start_date: str, end_date: str, tasks_summary: str) -> str:
    """降级策略：纯文本周报，不调用 AI"""
    lines = [
        f"# TaskFlow 周报 ({start_date} ~ {end_date})",
        "",
        "## 本周任务概览",
        "",
        tasks_summary,
        "",
        "## 说明",
        "",
        "AI 服务暂时不可用，以下为原始任务数据。",
    ]
    return "\n".join(lines)


class WeeklyReportService:
    """周报服务"""

    async def generate_report(
        self,
        start_date: str,
        end_date: str,
        tasks_summary: str,
    ) -> dict:
        """生成周报"""
        from app.services.ai_service import call_dashscope

        prompt = build_report_prompt(start_date, end_date, tasks_summary)
        messages = [
            {"role": "system", "content": REPORT_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]

        try:
            response_text = await call_dashscope(messages)
            if response_text:
                return {"report": response_text, "fallback": False}
        except (ValueError, Exception):
            pass

        # 降级
        return {"report": build_fallback_report(start_date, end_date, tasks_summary), "fallback": True}
