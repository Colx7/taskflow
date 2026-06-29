from sqlalchemy import Column, Integer, String, DateTime, func


from app.database import Base


class Category(Base):
    """分类表 ORM 模型"""

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    icon = Column(String(20), nullable=True, default=None)
    color = Column(String(20), nullable=True, default=None)
    sort_order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name={self.name})>"
