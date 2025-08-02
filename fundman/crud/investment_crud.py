"""
投资组合相关CRUD操作模块
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import date

from ..models import (
    AssetDB, AssetCreate, AssetUpdate, AssetInDB,
    TransactionDB, TransactionCreate, TransactionUpdate, TransactionInDB
)


def create_asset(db: Session, asset: AssetCreate) -> AssetInDB:
    """创建新资产"""
    db_asset = AssetDB(**asset.model_dump())
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    return AssetInDB.model_validate(db_asset)


def get_asset(db: Session, asset_id: int) -> Optional[AssetInDB]:
    """根据ID获取资产"""
    db_asset = db.query(AssetDB).filter(AssetDB.asset_id == asset_id).first()
    if db_asset:
        return AssetInDB.model_validate(db_asset)
    return None


def get_asset_by_code(db: Session, asset_code: str) -> Optional[AssetInDB]:
    """根据资产代码获取资产"""
    db_asset = db.query(AssetDB).filter(AssetDB.asset_code == asset_code).first()
    if db_asset:
        return AssetInDB.model_validate(db_asset)
    return None


def get_assets(db: Session, skip: int = 0, limit: int = 100) -> List[AssetInDB]:
    """获取资产列表"""
    db_assets = db.query(AssetDB).offset(skip).limit(limit).all()
    return [AssetInDB.model_validate(asset) for asset in db_assets]


def update_asset(db: Session, asset_id: int, asset: AssetUpdate) -> Optional[AssetInDB]:
    """更新资产信息"""
    db_asset = db.query(AssetDB).filter(AssetDB.asset_id == asset_id).first()
    if db_asset:
        for key, value in asset.model_dump(exclude_unset=True).items():
            setattr(db_asset, key, value)
        db.commit()
        db.refresh(db_asset)
        return AssetInDB.model_validate(db_asset)
    return None


def delete_asset(db: Session, asset_id: int) -> bool:
    """删除资产"""
    db_asset = db.query(AssetDB).filter(AssetDB.asset_id == asset_id).first()
    if db_asset:
        db.delete(db_asset)
        db.commit()
        return True
    return False


def create_transaction(db: Session, transaction: TransactionCreate) -> TransactionInDB:
    """创建新交易"""
    # 如果没有提供清算金额，根据数量和单位全价计算
    transaction_data = transaction.model_dump()
    if transaction_data.get('settlement_amount') is None and transaction_data.get('quantity') is not None and transaction_data.get('unit_full_price') is not None:
        transaction_data['settlement_amount'] = transaction_data['quantity'] * transaction_data['unit_full_price']
    
    db_transaction = TransactionDB(**transaction_data)
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return TransactionInDB.model_validate(db_transaction)


def get_transaction(db: Session, transaction_id: int) -> Optional[TransactionInDB]:
    """根据ID获取交易"""
    db_transaction = db.query(TransactionDB).filter(TransactionDB.transaction_id == transaction_id).first()
    if db_transaction:
        return TransactionInDB.model_validate(db_transaction)
    return None


def get_transactions(db: Session, skip: int = 0, limit: int = 100) -> List[TransactionInDB]:
    """获取交易列表"""
    db_transactions = db.query(TransactionDB).offset(skip).limit(limit).all()
    return [TransactionInDB.model_validate(transaction) for transaction in db_transactions]


def get_transactions_by_product(db: Session, product_id: int) -> List[TransactionInDB]:
    """根据产品ID获取交易列表"""
    db_transactions = db.query(TransactionDB).filter(TransactionDB.product_id == product_id).all()
    return [TransactionInDB.model_validate(transaction) for transaction in db_transactions]


def get_transactions_by_asset(db: Session, asset_id: int) -> List[TransactionInDB]:
    """根据资产ID获取交易列表"""
    db_transactions = db.query(TransactionDB).filter(TransactionDB.asset_id == asset_id).all()
    return [TransactionInDB.model_validate(transaction) for transaction in db_transactions]


def get_transactions_by_date_range(db: Session, start_date: date, end_date: date) -> List[TransactionInDB]:
    """根据日期范围获取交易列表"""
    db_transactions = db.query(TransactionDB).filter(
        and_(
            TransactionDB.investment_date >= start_date,
            TransactionDB.investment_date <= end_date
        )
    ).all()
    return [TransactionInDB.model_validate(transaction) for transaction in db_transactions]


def update_transaction(db: Session, transaction_id: int, transaction: TransactionUpdate) -> Optional[TransactionInDB]:
    """更新交易信息"""
    db_transaction = db.query(TransactionDB).filter(TransactionDB.transaction_id == transaction_id).first()
    if db_transaction:
        transaction_data = transaction.model_dump(exclude_unset=True)
        # 如果更新了数量或单位全价，重新计算清算金额
        if ('quantity' in transaction_data or 'unit_full_price' in transaction_data) and 'settlement_amount' not in transaction_data:
            quantity = transaction_data.get('quantity', db_transaction.quantity)
            unit_full_price = transaction_data.get('unit_full_price', db_transaction.unit_full_price)
            if quantity is not None and unit_full_price is not None:
                transaction_data['settlement_amount'] = quantity * unit_full_price
        
        for key, value in transaction_data.items():
            setattr(db_transaction, key, value)
        db.commit()
        db.refresh(db_transaction)
        return TransactionInDB.model_validate(db_transaction)
    return None


def delete_transaction(db: Session, transaction_id: int) -> bool:
    """删除交易"""
    db_transaction = db.query(TransactionDB).filter(TransactionDB.transaction_id == transaction_id).first()
    if db_transaction:
        db.delete(db_transaction)
        db.commit()
        return True
    return False