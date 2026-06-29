"""所有 SQLAlchemy 模型的统一导入，确保 Base.metadata 包含全部表定义"""

from app.models.user import User       # noqa: F401
from app.models.category import Category  # noqa: F401
from app.models.tag import Tag          # noqa: F401
from app.models.task import Task        # noqa: F401
from app.models.task_tag import task_tags  # noqa: F401
