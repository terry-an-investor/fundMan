import pytest
from fundman.database.connection import init_db, get_db


def test_init_db():
    """测试数据库初始化"""
    # 初始化数据库
    init_db()
    
    # 尝试获取数据库会话
    db_gen = get_db()
    db = next(db_gen)
    
    # 确保数据库会话有效
    assert db is not None
    
    # 关闭数据库会话
    db_gen.close()