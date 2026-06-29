import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

settings = get_settings()

# 处理 SQLite URL：Windows 路径需要特殊处理
db_url = settings.DATABASE_URL
if settings.DB_DRIVER == "sqlite":
    # 确保是 file:// URI 格式
    abs_path = os.path.abspath(settings.SQLITE_PATH)
    normalized = abs_path.replace("\\", "/")
    db_url = f"sqlite+aiosqlite:///{normalized}"

engine = create_async_engine(
    db_url,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    """所有 SQLAlchemy 模型的基类"""
    pass


async def get_db() -> AsyncSession:
    """FastAPI 依赖注入：获取数据库会话"""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
