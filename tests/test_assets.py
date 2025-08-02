import pytest
from fundman.models import AssetCreate
from fundman.crud import create_asset, get_asset_by_code, update_asset, get_asset


def test_create_asset(db_session):
    """测试创建资产"""
    # 创建资产数据
    asset_data = AssetCreate(
        asset_name="蓝筹股票A",
        asset_code="STOCK_A",
        asset_type="股票",
        issuer="知名证券公司",
        industry="科技",
        region="中国大陆"
    )
    
    # 创建资产
    asset = create_asset(db_session, asset_data)
    
    # 验证资产已创建
    assert asset is not None
    assert asset.asset_name == asset_data.asset_name
    assert asset.asset_code == asset_data.asset_code


def test_get_asset_by_code(db_session):
    """测试根据资产代码获取资产"""
    # 创建资产数据
    asset_data = AssetCreate(
        asset_name="政府债券B",
        asset_code="BOND_B",
        asset_type="债券",
        issuer="国家财政部",
        industry="政府",
        region="中国大陆"
    )
    
    # 创建资产
    created_asset = create_asset(db_session, asset_data)
    
    # 根据资产代码获取资产
    retrieved_asset = get_asset_by_code(db_session, "BOND_B")
    
    # 验证获取的资产与创建的资产一致
    assert retrieved_asset is not None
    assert retrieved_asset.asset_id == created_asset.asset_id
    assert retrieved_asset.asset_name == created_asset.asset_name
    assert retrieved_asset.asset_code == created_asset.asset_code


def test_update_asset(db_session):
    """测试更新资产"""
    # 创建资产数据
    asset_data = AssetCreate(
        asset_name="混合型基金C",
        asset_code="FUND_C",
        asset_type="基金",
        issuer="知名基金公司",
        industry="金融",
        region="中国大陆"
    )
    
    # 创建资产
    created_asset = create_asset(db_session, asset_data)
    
    # 更新资产信息
    from fundman.models import AssetUpdate
    asset_update = AssetUpdate(
        asset_name="混合型基金C-更新",
        asset_type="基金",
        issuer="更新后的知名基金公司",
        industry="金融科技"
    )
    
    updated_asset = update_asset(db_session, created_asset.asset_id, asset_update)
    
    # 验证资产已更新
    assert updated_asset is not None
    assert updated_asset.asset_name == "混合型基金C-更新"
    assert updated_asset.issuer == "更新后的知名基金公司"
    assert updated_asset.industry == "金融科技"