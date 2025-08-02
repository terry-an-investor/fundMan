from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from ..models import WealthProductDB, WealthProductCreate, WealthProductUpdate, WealthProductInDB
from ..utils.date_utils import parse_date, days_remaining_on


def get_product_by_yindeng_code(db: Session, yindeng_code: str) -> Optional[WealthProductDB]:
    """根据银登编码获取产品"""
    return db.query(WealthProductDB).filter(WealthProductDB.product_yindeng_code == yindeng_code).first()


def get_products(db: Session, skip: int = 0, limit: int = 100) -> List[WealthProductDB]:
    """获取产品列表"""
    return db.query(WealthProductDB).offset(skip).limit(limit).all()


def create_product(db: Session, product: WealthProductCreate) -> WealthProductDB:
    """创建产品"""
    db_product = WealthProductDB(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update_product(db: Session, product_id: int, product: WealthProductUpdate) -> Optional[WealthProductDB]:
    """更新产品"""
    db_product = db.query(WealthProductDB).filter(WealthProductDB.product_id == product_id).first()
    if db_product:
        update_data = product.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_product, key, value)
        db.commit()
        db.refresh(db_product)
    return db_product


def upsert_product_by_yindeng_code(db: Session, product: WealthProductCreate) -> WealthProductDB:
    """根据银登编码插入或更新产品"""
    # 检查银登编码是否为空
    if not product.product_yindeng_code:
        # 如果银登编码为空，直接创建新产品
        return create_product(db, product)
        
    db_product = get_product_by_yindeng_code(db, product.product_yindeng_code)
    if db_product:
        # 更新现有产品
        update_data = product.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_product, key, value)
        db.commit()
        db.refresh(db_product)
        return db_product
    else:
        # 创建新产品
        return create_product(db, product)


def get_all_products(db: Session) -> List[WealthProductDB]:
    """获取所有产品"""
    return db.query(WealthProductDB).all()


def get_products_by_query_date(db: Session, query_date: date) -> List[WealthProductDB]:
    """根据查询日期获取产品"""
    return db.query(WealthProductDB).filter(WealthProductDB.product_query_date == query_date).all()


def query_dynamic(db: Session, query_date_str: str) -> List[WealthProductDB]:
    """动态查询产品（根据查询日期计算剩余期限）
    
    Args:
        db: 数据库会话
        query_date_str: 查询日期字符串
        
    Returns:
        List[WealthProductDB]: 产品列表，包含动态计算的剩余天数
    """
    query_date = parse_date(query_date_str)
    
    # 获取所有产品
    all_products = get_all_products(db)
    
    # 筛选符合查询日期的产品
    results = []
    for product in all_products:
        # 检查产品是否有结束日期
        if product.product_end_date is not None:
            days_remaining = days_remaining_on(
                product.product_end_date.isoformat(),
                query_date
            )
            # 创建一个新的产品对象，更新剩余天数
            # 将SQLAlchemy模型转换为Pydantic模型，更新剩余天数
            product_data = WealthProductInDB.model_validate(product)
            product_data.product_days_remaining = days_remaining
            results.append(product_data)
    
    return results