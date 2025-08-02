from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import os
from contextlib import contextmanager
from ..models import Base

# 数据库配置（可配置化）
# 优先读取环境变量 FUNDMAN_DB_URL 或 DATABASE_URL；否则回退到项目 data/fund_report.db
PROJECT_ROOT = Path(__file__).parent.parent.parent
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "fund_report.db"
DEFAULT_SQLITE_URL = f"sqlite:///{DEFAULT_DB_PATH}"
SQLALCHEMY_DATABASE_URL = os.getenv("FUNDMAN_DB_URL") or os.getenv("DATABASE_URL") or DEFAULT_SQLITE_URL

# 若使用本地 sqlite，确保目录存在
if SQLALCHEMY_DATABASE_URL.startswith("sqlite:///"):
    Path(SQLALCHEMY_DATABASE_URL.replace("sqlite:///", "")).parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """获取数据库会话（生成器形式，兼容现有调用）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_ctx():
    """获取数据库会话（上下文管理形式，推荐在新代码中使用）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """初始化数据库（基于当前配置的 engine）"""
    # 如果是默认 sqlite，确保目录存在
    if SQLALCHEMY_DATABASE_URL.startswith("sqlite:///"):
        Path(SQLALCHEMY_DATABASE_URL.replace("sqlite:///", "")).parent.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)