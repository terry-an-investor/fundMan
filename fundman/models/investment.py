from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date
from .wealth_product import Base


# SQLAlchemy models
class AssetDB(Base):
    """资产数据库模型（静态信息）"""
    __tablename__ = "assets"
    
    asset_id = Column(Integer, primary_key=True, index=True)
    asset_name = Column(String, nullable=False)
    asset_code = Column(String, unique=True, index=True)  # 资产编码
    asset_type = Column(String, nullable=False)  # 资产类型：股票、债券、存款等
    issuer = Column(String)  # 资产发行人
    industry = Column(String)  # 资产所属行业
    region = Column(String)  # 资产所属地区
    created_date = Column(Date, default=date.today)
    
    # 关系
    transactions = relationship("TransactionDB", back_populates="asset")


class TransactionDB(Base):
    """交易数据库模型（动态投资信息）"""
    __tablename__ = "transactions"
    
    transaction_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("wealth_products.product_id"), nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.asset_id"), nullable=False)
    investment_date = Column(Date, nullable=False)  # 投资日期
    maturity_date = Column(Date)  # 到期日期
    interest_rate = Column(Float)  # 收益率
    quantity = Column(Float, nullable=False)  # 投资数量
    unit_net_price = Column(Float)  # 单位净价
    unit_full_price = Column(Float)  # 单位全价
    settlement_amount = Column(Float)  # 清算金额（数量*全价）
    
    # 关系
    product = relationship("WealthProductDB", back_populates="transactions")
    asset = relationship("AssetDB", back_populates="transactions")


# Pydantic models
class AssetBase(BaseModel):
    """资产基础模型"""
    asset_name: str
    asset_code: Optional[str] = None
    asset_type: str
    issuer: Optional[str] = None
    industry: Optional[str] = None
    region: Optional[str] = None
    created_date: Optional[date] = None


class AssetCreate(AssetBase):
    """创建资产模型"""
    pass


class AssetUpdate(AssetBase):
    """更新资产模型"""
    pass


class AssetInDB(AssetBase):
    """数据库中的资产模型"""
    asset_id: int
    
    model_config = ConfigDict(from_attributes=True)


class TransactionBase(BaseModel):
    """交易基础模型"""
    product_id: int
    asset_id: int
    investment_date: date
    maturity_date: Optional[date] = None
    interest_rate: Optional[float] = None
    quantity: float
    unit_net_price: Optional[float] = None
    unit_full_price: Optional[float] = None
    settlement_amount: Optional[float] = None


class TransactionCreate(TransactionBase):
    """创建交易模型"""
    pass


class TransactionUpdate(TransactionBase):
    """更新交易模型"""
    pass


class TransactionInDB(TransactionBase):
    """数据库中的交易模型"""
    transaction_id: int
    
    model_config = ConfigDict(from_attributes=True)