from sqlalchemy import Column, Integer, ForeignKey, Table

from app.database import Base


# 多对多关联表：任务 <-> 标签
task_tags = Table(
    "task_tags",
    Base.metadata,
    Column("task_id", Integer, ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)
