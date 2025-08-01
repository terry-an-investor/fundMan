from pydantic import BaseModel
from typing import Optional
from datetime import date
from sqlalchemy import Column, Integer, String, Date, Float
from sqlalchemy.orm import DeclarativeBase

# Pydantic models
class WealthProductBase(BaseModel):
    """理财产品基础模型"""
    product_name: str
    product_yindeng_code: Optional[str] = None
    product_jinshu_code: Optional[str] = None
    product_custody_code: Optional[str] = None
    product_start_date: date
    product_end_date: date
    product_days_total: int
    product_query_date: Optional[date] = None
    product_days_remaining: Optional[int] = None
    product_performance_benchmark: Optional[float] = None
    product_raise_target: Optional[float] = None
    product_raise_amount: Optional[float] = None
    product_raise_institutional: Optional[float] = None
    product_raise_retail: Optional[float] = None

class WealthProductCreate(WealthProductBase):
    """创建理财产品模型"""
    pass

class WealthProductUpdate(WealthProductBase):
    """更新理财产品模型"""
    pass

class WealthProductInDB(WealthProductBase):
    """数据库中的理财产品模型"""
    product_id: int
    
    class Config:
        from_attributes = True

# SQLAlchemy models
class Base(DeclarativeBase):
    pass

class WealthProductDB(Base):
    """理财产品数据库模型"""
    __tablename__ = "wealth_products"
    
    product_id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, nullable=False)
    product_yindeng_code = Column(String, unique=True, index=True)
    product_jinshu_code = Column(String)
    product_custody_code = Column(String)
    product_start_date = Column(Date, nullable=False)
    product_end_date = Column(Date, nullable=False)
    product_days_total = Column(Integer, nullable=False)
    product_query_date = Column(Date)
    product_days_remaining = Column(Integer)
    product_performance_benchmark = Column(Float)
    product_raise_target = Column(Float)
    product_raise_amount = Column(Float)
    product_raise_institutional = Column(Float)
    product_raise_retail = Column(Float)