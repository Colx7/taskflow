from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置，从 .env 文件读取环境变量"""

    # 应用
    APP_NAME: str = "TaskFlow"
    DEBUG: bool = True

    # 数据库驱动: mysql 或 sqlite
    DB_DRIVER: str = "sqlite"  # 改为 "sqlite" 即可零依赖启动

    # MySQL 配置（DB_DRIVER=mysql 时生效）
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "123456"
    MYSQL_DATABASE: str = "taskflow"

    # SQLite 配置（DB_DRIVER=sqlite 时生效）
    SQLITE_PATH: str = "taskflow.db"

    # JWT
    JWT_SECRET_KEY: str = "change-this-to-a-random-secret-key-in-production"
    JWT_EXPIRE_DAYS: int = 7

    # AI (通义千问/DashScope)
    DASHSCOPE_API_KEY: str = ""
    AI_MODEL: str = "qwen-plus"
    AI_TEMPERATURE: float = 0.3
    AI_MAX_TOKENS: int = 2048
    AI_TIMEOUT: int = 30

    @property
    def DATABASE_URL(self) -> str:
        if self.DB_DRIVER == "sqlite":
            import os
            abs_path = os.path.abspath(self.SQLITE_PATH)
            # 使用 file:// URI 格式，Windows 盘符需要 4 个斜杠
            # file:///D:/path/to/db.db
            normalized = abs_path.replace("\\", "/")
            return f"sqlite+aiosqlite:///{normalized}"
        return (
            f"mysql+aiomysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
            f"?charset=utf8mb4"
        )

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


def get_settings() -> Settings:
    return Settings()
