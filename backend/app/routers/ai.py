from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.models.category import Category
from app.schemas.ai import TaskClassifyRequest, TaskClassifyResponse
from app.services.ai_service import AIService

router = APIRouter(
    prefix="/api/ai",
    tags=["🤖 AI 智能"],
    responses={404: {"description": "未找到"}},
)


@router.post(
    "/classify",
    response_model=TaskClassifyResponse,
    summary="AI 智能分类",
    description="输入任务标题和描述，AI 自动判断分类和优先级。如果 AI 服务不可用，会自动使用关键词匹配降级。",
)
async def classify_task(
    data: TaskClassifyRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """AI 智能分类与优先级推荐"""
    ai_service = AIService()
    result = await ai_service.classify_task(data.title, data.description or "")

    # 验证分类名称是否存在
    existing = await db.execute(select(Category).where(Category.name == result.get("category")))
    category = existing.scalar_one_or_none()
    if not category:
        raise HTTPException(
            status_code=400,
            detail=f"分类 '{result.get('category')}' 不存在，请先创建该分类",
        )

    return TaskClassifyResponse(
        category=result.get("category", "其他"),
        priority=result.get("priority", "medium"),
        reason=result.get("reason", ""),
        suggested_tags=result.get("suggested_tags", []),
    )
