"""AI 服务：通义千问 DashScope API 调用 + 降级策略"""

import json
import re
import os
import asyncio
from typing import Optional

import httpx
from app.config import get_settings

settings = get_settings()

CLASSIFY_SYSTEM_PROMPT = """你是一个智能任务管理助手。根据用户提供的任务标题和描述，
自动判断任务的分类、优先级，并给出理由。

可用分类:
- 工作: 与职业相关的任务
- 学习: 与知识提升相关的任务
- 生活: 日常生活中的事务
- 健身: 运动和健康相关
- 其他: 无法归入以上分类的任务

优先级标准:
- urgent(紧急): 当天或24小时内需要完成
- high(高): 3天内需要完成
- medium(中): 一周内完成即可
- low(低): 没有紧迫性

你必须严格按照以下 JSON 格式返回（不要添加任何其他内容）:
{"category": "分类名称", "priority": "优先级枚举值", "reason": "理由(50字以内)"}"""


async def call_dashscope(messages: list[dict]) -> str | None:
    """调用 DashScope API，带重试和降级"""
    api_key = settings.DASHSCOPE_API_KEY
    if not api_key or api_key == "sk-your-api-key-here":
        raise ValueError("DASHSCOPE_API_KEY 未配置")

    timeout = int(os.getenv("AI_TIMEOUT", "30"))
    model = os.getenv("AI_MODEL", "qwen-plus")
    temperature = float(os.getenv("AI_TEMPERATURE", "0.3"))
    max_tokens = int(os.getenv("AI_MAX_TOKENS", "2048"))

    for attempt in range(3):
        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                resp = await client.post(
                    "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        "response_format": {"type": "json_object"},
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"]
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise
            except (httpx.TimeoutException, httpx.ConnectError):
                if attempt < 2:
                    await asyncio.sleep(1)
                    continue
                raise
    return None


def parse_json_response(text: str) -> Optional[dict]:
    """从 LLM 返回中提取 JSON"""
    if not text:
        return None
    # 尝试直接解析
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # 尝试提取 JSON 块
    match = re.search(r"\{[^{}]*\"category\"[^{}]*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return None


def fallback_classify(title: str, description: str) -> dict:
    """降级策略：基于关键词的规则匹配"""
    keywords = {
        "工作": ["会议", "汇报", "文档", "代码", "项目", "bug", "上线", "评审", "周报", "PPT", "周会", "例会", "晨会", "站会", "开会", "面试", "出差"],
        "学习": ["阅读", "课程", "考试", "证书", "教程", "笔记", "复习", "论文", "调研"],
        "生活": ["购物", "买菜", "打扫", "缴费", "预约", "聚餐", "快递", "搬家", "日用品", "超市", "洗衣", "租房", "水电", "话费", "理发"],
        "健身": ["跑步", "健身", "锻炼", "游泳", "瑜伽", "举铁", "减肥", "运动"],
    }
    urgent_keywords = ["bug", "上线", "紧急", "故障", "报错", "crash", "宕机"]
    text = (title + " " + (description or "")).lower()
    for category, kws in keywords.items():
        for kw in kws:
            if kw in text:
                # 根据关键词推断优先级
                priority = "medium"
                if any(u in text for u in urgent_keywords):
                    priority = "urgent" if "bug" in kw or "上线" in kw else "high"
                return {
                    "category": category,
                    "priority": priority,
                    "reason": f"[降级] 基于关键词 '{kw}' 匹配到 {category}",
                    "suggested_tags": [],
                }
    return {
        "category": "其他",
        "priority": "medium",
        "reason": "[降级] 未匹配到关键词，使用默认分类",
        "suggested_tags": [],
    }


class AIService:
    """AI 服务"""

    async def classify_task(self, title: str, description: str = "") -> dict:
        """AI 分类与优先级推荐"""
        messages = [
            {"role": "system", "content": CLASSIFY_SYSTEM_PROMPT},
            {"role": "user", "content": f"任务标题: {title}\n任务描述: {description}"},
        ]

        try:
            response_text = await call_dashscope(messages)
            parsed = parse_json_response(response_text)
            if parsed and "category" in parsed:
                return parsed
        except (ValueError, Exception):
            pass

        # 降级
        return fallback_classify(title, description)
