from pydantic import BaseModel
from typing import Optional
from datetime import date

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