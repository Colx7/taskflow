"""快速初始化种子数据：分类、标签、第一个用户"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database import async_session
from app.models.user import User
from app.models.category import Category
from app.models.tag import Tag
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def seed():
    async with async_session() as session:
        from sqlalchemy import select

        # 1. 创建默认用户（密码 admin123）
        stmt = select(User).where(User.id == 1)
        user = (await session.execute(stmt)).scalar_one_or_none()
        if not user:
            user = User(
                username="admin",
                email="admin@taskflow.com",
                password_hash=pwd_context.hash("admin123"),
            )
            session.add(user)
            await session.flush()
            print(f"[+] 创建用户: admin / admin123 (id={user.id})")
        else:
            print(f"[~] 用户已存在: {user.username}")

        # 2. 创建默认分类
        default_categories = [
            ("工作", "💼", "#e6a23c"),
            ("学习", "📚", "#409eff"),
            ("健身", "💪", "#67c23a"),
            ("生活", "🏠", "#909399"),
        ]
        for name, icon, color in default_categories:
            stmt = select(Category).where(Category.name == name)
            cat = (await session.execute(stmt)).scalar_one_or_none()
            if not cat:
                session.add(Category(name=name, icon=icon, color=color))
                print(f"[+] 创建分类: {name}")
            else:
                print(f"[~] 分类已存在: {name}")

        # 3. 创建默认标签
        default_tags = [
            ("会议", "#e6a23c"),
            ("阅读", "#409eff"),
            ("编程", "#67c23a"),
            ("运动", "#f56c6c"),
            ("设计", "#909399"),
        ]
        for name, color in default_tags:
            stmt = select(Tag).where(Tag.name == name)
            tag = (await session.execute(stmt)).scalar_one_or_none()
            if not tag:
                session.add(Tag(name=name, color=color))
                print(f"[+] 创建标签: {name}")
            else:
                print(f"[~] 标签已存在: {name}")

        await session.commit()
        print("\n[✓] 种子数据写入完成")


if __name__ == "__main__":
    asyncio.run(seed())
