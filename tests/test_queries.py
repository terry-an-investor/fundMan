import pytest
from datetime import date
import random
from fundman.models import AssetCreate, WealthProductCreate, TransactionCreate
from fundman.crud import (
    create_asset, upsert_product_by_yindeng_code, create_transaction,
    get_assets, get_transactions, get_transactions_by_product, get_transactions_by_asset
)


def test_get_assets(db_session):
    """测试获取资产列表"""
    # 创建多个资产
    assets_data = [
        AssetCreate(
            asset_name="蓝筹股票A",
            asset_code="STOCK_A",
            asset_type="股票",
            issuer="知名证券公司",
            industry="科技",
            region="中国大陆"
        ),
        AssetCreate(
            asset_name="政府债券B",
            asset_code="BOND_B",
            asset_type="债券",
            issuer="国家财政部",
            industry="政府",
            region="中国大陆"
        )
    ]
    
    created_assets = []
    for asset_data in assets_data:
        asset = create_asset(db_session, asset_data)
        created_assets.append(asset)
    
    # 获取资产列表
    assets = get_assets(db_session)
    
    # 验证资产列表
    assert len(assets) >= 2
    asset_codes = [asset.asset_code for asset in assets]
    assert "STOCK_A" in asset_codes
    assert "BOND_B" in asset_codes


def test_get_transactions(db_session):
    """测试获取交易列表"""
    # 创建资产
    asset_data = AssetCreate(
        asset_name="混合型基金C",
        asset_code="FUND_C",
        asset_type="基金",
        issuer="知名基金公司",
        industry="金融",
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
    
    # 创建多个交易
    transactions_data = [
        TransactionCreate(
            product_id=product.product_id,
            asset_id=asset.asset_id,
            investment_date=date(2023, 8, 1),
            maturity_date=date(2024, 8, 1),
            interest_rate=6.5,
            quantity=500.0,
            unit_net_price=5.0,
            unit_full_price=5.1
        ),
        TransactionCreate(
            product_id=product.product_id,
            asset_id=asset.asset_id,
            investment_date=date(2023, 9, 1),
            maturity_date=date(2024, 9, 1),
            interest_rate=6.8,
            quantity=600.0,
            unit_net_price=6.0,
            unit_full_price=6.2
        )
    ]
    
    created_transactions = []
    for transaction_data in transactions_data:
        transaction = create_transaction(db_session, transaction_data)
        created_transactions.append(transaction)
    
    # 获取交易列表
    transactions = get_transactions(db_session)
    
    # 验证交易列表
    assert len(transactions) >= 2
    transaction_ids = [transaction.transaction_id for transaction in transactions]
    for created_transaction in created_transactions:
        assert created_transaction.transaction_id in transaction_ids


def test_get_transactions_by_product(db_session):
    """测试根据产品获取交易列表"""
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
    
    # 创建交易
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
    transaction = create_transaction(db_session, transaction_data)
    
    # 根据产品获取交易列表
    product_transactions = get_transactions_by_product(db_session, product.product_id)
    
    # 验证交易列表
    assert len(product_transactions) >= 1
    transaction_ids = [t.transaction_id for t in product_transactions]
    assert transaction.transaction_id in transaction_ids


def test_get_transactions_by_asset(db_session):
    """测试根据资产获取交易列表"""
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
    
    # 创建交易
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
    transaction = create_transaction(db_session, transaction_data)
    
    # 根据资产获取交易列表
    asset_transactions = get_transactions_by_asset(db_session, asset.asset_id)
    
    # 验证交易列表
    assert len(asset_transactions) >= 1
    transaction_ids = [t.transaction_id for t in asset_transactions]
    assert transaction.transaction_id in transaction_ids