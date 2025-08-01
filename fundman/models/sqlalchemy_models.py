from sqlalchemy import Column, Integer, String, Date, Float
from sqlalchemy.orm import DeclarativeBase

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