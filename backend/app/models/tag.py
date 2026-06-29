from sqlalchemy import Column, Integer, String, DateTime, func


from app.database import Base


class Tag(Base):
    """标签表 ORM 模型"""

    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(30), unique=True, nullable=False)
    color = Column(String(20), nullable=True, default=None)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<Tag(id={self.id}, name={self.name})>"
