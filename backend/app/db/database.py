"""数据库连接和会话管理"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings
from app.models.models import Base

# 创建数据库引擎
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """初始化数据库（创建所有表）"""
    Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """获取数据库会话（依赖注入）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
