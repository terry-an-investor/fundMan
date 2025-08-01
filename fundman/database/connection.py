from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path
from ..models import Base

# 数据库配置
DB_PATH = "data/fund_report.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{Path(DB_PATH).absolute()}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """初始化数据库"""
    Base.metadata.create_all(bind=engine)