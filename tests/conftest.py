import pytest
from fundman.database.connection import init_db, get_db
from fundman.models import Base, WealthProductDB, AssetDB, TransactionDB
import os
import tempfile
import shutil
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture(scope="session")
def db_engine():
    """创建测试数据库引擎"""
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_fund_report.db")
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"
    
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # 清理临时目录
    engine.dispose()
    shutil.rmtree(temp_dir)


@pytest.fixture(scope="function")
def db_session(db_engine):
    """创建测试数据库会话"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = SessionLocal()
    
    yield session
    
    # 清理数据库中的所有数据
    session.query(TransactionDB).delete()
    session.query(WealthProductDB).delete()
    session.query(AssetDB).delete()
    session.commit()
    
    # 关闭会话
    session.close()