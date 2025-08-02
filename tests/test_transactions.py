import pytest
from datetime import date
import random
from fundman.models import AssetCreate, WealthProductCreate, TransactionCreate
from fundman.crud import create_asset, upsert_product_by_yindeng_code, create_transaction, get_transaction


def test_create_transaction(db_session):
    """测试创建交易"""
    # 创建资产
    asset_data = AssetCreate(
        asset_name="蓝筹股票A",
        asset_code="STOCK_A",
        asset_type="股票",
        issuer="知名证券公司",
        industry="科技",
        region="中国大陆"
    )
    asset = create_asset(db_session, asset_data)
    
    # 创建理财产品
    product_data = WealthProductCreate(
        product_name="稳健收益理财产品A",
        product_yindeng_code=f"YD_WR_{random.randint(1000, 9999)}",
        product_jinshu_code=f"JS_WR_{random.randint(1000, 9999)}",
        product_custody_code=f"CUST_WR_{random.randint(1000, 9999)}",
        product_start_date=date(2023, 1, 1),
        product_end_date=date(2024, 1, 1),
        product_days_total=365,
        product_performance_benchmark=4.5,
        product_raise_target=10000000.0,
        product_raise_amount=8000000.0
    )
    product = upsert_product_by_yindeng_code(db_session, product_data)
    
    # 创建交易数据
    transaction_data = TransactionCreate(
        product_id=product.product_id,
        asset_id=asset.asset_id,
        investment_date=date(2023, 6, 1),
        maturity_date=date(2024, 6, 1),
        interest_rate=5.2,
        quantity=1000.0,
        unit_net_price=10.0,
        unit_full_price=10.2
    )
    
    # 创建交易
    transaction = create_transaction(db_session, transaction_data)
    
    # 验证交易已创建
    assert transaction is not None
    assert transaction.product_id == transaction_data.product_id
    assert transaction.asset_id == transaction_data.asset_id
    assert transaction.investment_date == transaction_data.investment_date
    assert transaction.quantity == transaction_data.quantity


def test_get_transaction(db_session):
    """测试获取交易"""
    # 创建资产
    asset_data = AssetCreate(
        asset_name="政府债券B",
        asset_code="BOND_B",
        asset_type="债券",
        issuer="国家财政部",
        industry="政府",
        region="中国大陆"
    )
    asset = create_asset(db_session, asset_data)
    
    # 创建理财产品
    product_data = WealthProductCreate(
        product_name="高收益理财产品B",
        product_yindeng_code=f"YD_HR_{random.randint(1000, 9999)}",
        product_jinshu_code=f"JS_HR_{random.randint(1000, 9999)}",
        product_custody_code=f"CUST_HR_{random.randint(1000, 9999)}",
        product_start_date=date(2023, 6, 1),
        product_end_date=date(2024, 6, 1),
        product_days_total=365,
        product_performance_benchmark=6.2,
        product_raise_target=5000000.0,
        product_raise_amount=4500000.0
    )
    product = upsert_product_by_yindeng_code(db_session, product_data)
    
    # 创建交易数据
    transaction_data = TransactionCreate(
        product_id=product.product_id,
        asset_id=asset.asset_id,
        investment_date=date(2023, 7, 1),
        maturity_date=date(2024, 7, 1),
        interest_rate=4.8,
        quantity=2000.0,
        unit_net_price=100.0,
        unit_full_price=100.5
    )
    
    # 创建交易
    created_transaction = create_transaction(db_session, transaction_data)
    
    # 获取交易
    retrieved_transaction = get_transaction(db_session, created_transaction.transaction_id)
    
    # 验证获取的交易与创建的交易一致
    assert retrieved_transaction is not None
    assert retrieved_transaction.transaction_id == created_transaction.transaction_id
    assert retrieved_transaction.product_id == created_transaction.product_id
    assert retrieved_transaction.asset_id == created_transaction.asset_id
    assert retrieved_transaction.investment_date == created_transaction.investment_date
    assert retrieved_transaction.quantity == created_transaction.quantity