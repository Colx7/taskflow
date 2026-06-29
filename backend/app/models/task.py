from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, Enum, DATE, JSON, ForeignKey, DateTime as SADateTime, func
from sqlalchemy.orm import relationship

from app.database import Base

import enum


class TaskStatus(enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


class TaskPriority(enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


class Task(Base):
    """任务表 ORM 模型"""

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True, default=None)
    status = Column(Enum(TaskStatus), nullable=False, default=TaskStatus.pending)
    priority = Column(Enum(TaskPriority), nullable=False, default=TaskPriority.medium)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    due_date = Column(DATE, nullable=True, default=None)
    tags = Column(JSON, nullable=True, default=None)
    ai_suggestion = Column(JSON, nullable=True, default=None)
    created_at = Column(SADateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        SADateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # 关系
    category = relationship("Category", backref="tasks")
    user = relationship("User", backref="tasks")

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, title={self.title}, status={self.status.value})>"
