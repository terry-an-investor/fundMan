import pytest
from datetime import date
import random
from fundman.models import WealthProductCreate
from fundman.crud import upsert_product_by_yindeng_code, get_product_by_yindeng_code


def test_create_wealth_product(db_session):
    """测试创建理财产品"""
    # 创建理财产品数据
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
    
    # 创建理财产品
    product = upsert_product_by_yindeng_code(db_session, product_data)
    
    # 验证产品已创建
    assert product is not None
    assert product.product_name == product_data.product_name
    assert product.product_yindeng_code == product_data.product_yindeng_code


def test_get_wealth_product_by_yindeng_code(db_session):
    """测试根据银登编码获取理财产品"""
    # 创建理财产品数据
    yindeng_code = f"YD_WR_{random.randint(1000, 9999)}"
    product_data = WealthProductCreate(
        product_name="高收益理财产品B",
        product_yindeng_code=yindeng_code,
        product_jinshu_code=f"JS_HR_{random.randint(1000, 9999)}",
        product_custody_code=f"CUST_HR_{random.randint(1000, 9999)}",
        product_start_date=date(2023, 6, 1),
        product_end_date=date(2024, 6, 1),
        product_days_total=365,
        product_performance_benchmark=6.2,
        product_raise_target=5000000.0,
        product_raise_amount=4500000.0
    )
    
    # 创建理财产品
    created_product = upsert_product_by_yindeng_code(db_session, product_data)
    
    # 根据银登编码获取理财产品
    retrieved_product = get_product_by_yindeng_code(db_session, yindeng_code)
    
    # 验证获取的产品与创建的产品一致
    assert retrieved_product is not None
    assert retrieved_product.product_id == created_product.product_id
    assert retrieved_product.product_name == created_product.product_name
    assert retrieved_product.product_yindeng_code == created_product.product_yindeng_code