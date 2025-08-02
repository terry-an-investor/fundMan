import pytest
from datetime import date
from sqlalchemy.orm import Session

from fundman.models import (
    AssetCreate,
    TransactionCreate,
    WealthProductCreate,
)
from fundman.crud import (
    create_asset,
    get_asset_by_code,
    create_transaction,
    get_transactions,
)
from fundman.crud.wealth_product_crud import (
    upsert_product_by_yindeng_code,
    get_product_by_yindeng_code,
)


@pytest.fixture
def db_session(db_session: Session):
    # 复用 tests/conftest.py 中定义的 db_session fixture（作用域 function）
    return db_session


class TestWealthProductCrudMore:
    def test_get_product_by_yindeng_code_empty_or_none(self, db_session: Session):
        # 空字符串 / None 的行为（按当前实现：多数情况下返回 None）
        p1 = get_product_by_yindeng_code(db_session, "")
        p2 = get_product_by_yindeng_code(db_session, None)  # type: ignore[arg-type]
        assert p1 is None
        assert p2 is None

    def test_upsert_with_none_optional_fields_and_verify(self, db_session: Session):
        # 各可选字段为 None，确保保存后依然为 None
        p = WealthProductCreate(
            product_name="产品N",
            product_yindeng_code="Y-NONE",
            product_jinshu_code=None,
            product_custody_code=None,
            product_start_date=date(2025, 8, 1),
            product_end_date=date(2025, 8, 10),
            product_days_total=9,
            product_query_date=None,
            product_days_remaining=None,
            product_performance_benchmark=None,
            product_raise_target=None,
            product_raise_amount=None,
            product_raise_institutional=None,
            product_raise_retail=None,
        )
        upsert_product_by_yindeng_code(db_session, p)
        got = get_product_by_yindeng_code(db_session, "Y-NONE")
        assert got is not None
        # 断言可选字段保持 None
        assert getattr(got, "product_jinshu_code") is None
        assert getattr(got, "product_custody_code") is None
        assert getattr(got, "product_performance_benchmark") is None
        assert getattr(got, "product_raise_target") is None
        assert getattr(got, "product_raise_amount") is None
        assert getattr(got, "product_raise_institutional") is None
        assert getattr(got, "product_raise_retail") is None

    def test_upsert_partial_update_specific_field(self, db_session: Session):
        # 先插入
        base = WealthProductCreate(
            product_name="产品U",
            product_yindeng_code="Y-UP1",
            product_jinshu_code="J-A",
            product_custody_code="T-A",
            product_start_date=date(2025, 8, 1),
            product_end_date=date(2025, 8, 10),
            product_days_total=9,
            product_query_date=date(2025, 8, 1),
            product_days_remaining=9,
            product_performance_benchmark=0.05,
            product_raise_target=1000.0,
            product_raise_amount=800.0,
            product_raise_institutional=600.0,
            product_raise_retail=200.0,
        )
        upsert_product_by_yindeng_code(db_session, base)

        # 仅更新一个数值字段（例如基准），其他不变
        updated = WealthProductCreate(
            product_name="产品U",  # 名称不变
            product_yindeng_code="Y-UP1",
            product_jinshu_code="J-A",
            product_custody_code="T-A",
            product_start_date=date(2025, 8, 1),
            product_end_date=date(2025, 8, 10),
            product_days_total=9,
            product_query_date=date(2025, 8, 1),
            product_days_remaining=9,
            product_performance_benchmark=0.055,  # 仅变更此字段
            product_raise_target=1000.0,
            product_raise_amount=800.0,
            product_raise_institutional=600.0,
            product_raise_retail=200.0,
        )
        upsert_product_by_yindeng_code(db_session, updated)

        got = get_product_by_yindeng_code(db_session, "Y-UP1")
        assert got is not None
        assert getattr(got, "product_performance_benchmark") == 0.055
        assert getattr(got, "product_raise_amount") == 800.0  # 其他保持原值

    # 新增：更多局部字段更新，覆盖更多赋值分支
    def test_upsert_partial_update_raise_fields(self, db_session: Session):
        base = WealthProductCreate(
            product_name="产品U2",
            product_yindeng_code="Y-UP2",
            product_jinshu_code="J-B",
            product_custody_code="T-B",
            product_start_date=date(2025, 8, 1),
            product_end_date=date(2025, 8, 10),
            product_days_total=9,
            product_query_date=date(2025, 8, 1),
            product_days_remaining=9,
            product_performance_benchmark=0.03,
            product_raise_target=1000.0,
            product_raise_amount=500.0,
            product_raise_institutional=300.0,
            product_raise_retail=200.0,
        )
        upsert_product_by_yindeng_code(db_session, base)

        # 只变更募集相关字段
        updated = WealthProductCreate(
            product_name="产品U2",
            product_yindeng_code="Y-UP2",
            product_jinshu_code="J-B",
            product_custody_code="T-B",
            product_start_date=date(2025, 8, 1),
            product_end_date=date(2025, 8, 10),
            product_days_total=9,
            product_query_date=date(2025, 8, 1),
            product_days_remaining=9,
            product_performance_benchmark=0.03,
            product_raise_target=1200.0,
            product_raise_amount=800.0,
            product_raise_institutional=600.0,
            product_raise_retail=200.0,
        )
        upsert_product_by_yindeng_code(db_session, updated)

        got = get_product_by_yindeng_code(db_session, "Y-UP2")
        assert got is not None
        assert getattr(got, "product_raise_target") == 1200.0
        assert getattr(got, "product_raise_amount") == 800.0
        assert getattr(got, "product_raise_institutional") == 600.0
        assert getattr(got, "product_raise_retail") == 200.0


class TestInvestmentCrudMore:
    def test_settlement_amount_calculation_and_none(self, db_session: Session):
        # 创建产品与资产
        upsert_product_by_yindeng_code(
            db_session,
            WealthProductCreate(
                product_name="产品C",
                product_yindeng_code="Y-CALC",
                product_jinshu_code=None,
                product_custody_code=None,
                product_start_date=date(2025, 8, 1),
                product_end_date=date(2025, 8, 31),
                product_days_total=30,
                product_query_date=None,
                product_days_remaining=None,
                product_performance_benchmark=None,
                product_raise_target=None,
                product_raise_amount=None,
                product_raise_institutional=None,
                product_raise_retail=None,
            ),
        )
        product = get_product_by_yindeng_code(db_session, "Y-CALC")
        assert product is not None
        product_id_value = int(getattr(product, "product_id"))

        asset = create_asset(
            db_session,
            AssetCreate(
                asset_name="资产C",
                asset_code="AC01",
                asset_type="债券",
                issuer=None,
                industry=None,
                region=None,
            ),
        )

        # 1) 有全价时 settlement_amount = quantity * unit_full_price
        tx1 = TransactionCreate(
            product_id=product_id_value,
            asset_id=asset.asset_id,
            investment_date=date(2025, 8, 1),
            maturity_date=None,
            interest_rate=0.05,
            quantity=10.0,
            unit_net_price=None,
            unit_full_price=100.0,
        )
        created1 = create_transaction(db_session, tx1)
        assert created1.settlement_amount == 1000.0

        # 2) 无全价时 settlement_amount 为 None
        tx2 = TransactionCreate(
            product_id=product_id_value,
            asset_id=asset.asset_id,
            investment_date=date(2025, 8, 2),
            maturity_date=None,
            interest_rate=0.05,
            quantity=10.0,
            unit_net_price=None,
            unit_full_price=None,
        )
        created2 = create_transaction(db_session, tx2)
        assert created2.settlement_amount is None

    def test_get_transactions_empty_and_multiple(self, db_session: Session):
        # 初始应为空
        txs0 = get_transactions(db_session)
        assert isinstance(txs0, list)

        # 准备产品/资产
        upsert_product_by_yindeng_code(
            db_session,
            WealthProductCreate(
                product_name="产品T",
                product_yindeng_code="Y-TX",
                product_jinshu_code=None,
                product_custody_code=None,
                product_start_date=date(2025, 8, 1),
                product_end_date=date(2025, 8, 31),
                product_days_total=30,
                product_query_date=None,
                product_days_remaining=None,
                product_performance_benchmark=None,
                product_raise_target=None,
                product_raise_amount=None,
                product_raise_institutional=None,
                product_raise_retail=None,
            ),
        )
        product = get_product_by_yindeng_code(db_session, "Y-TX")
        assert product is not None
        product_id_value = int(getattr(product, "product_id"))

        asset = create_asset(
            db_session,
            AssetCreate(
                asset_name="资产T",
                asset_code="AT01",
                asset_type="债券",
                issuer=None,
                industry=None,
                region=None,
            ),
        )

        # 插入两条交易
        tx1 = TransactionCreate(
            product_id=product_id_value,
            asset_id=asset.asset_id,
            investment_date=date(2025, 8, 3),
            maturity_date=None,
            interest_rate=None,
            quantity=1.0,
            unit_net_price=None,
            unit_full_price=10.0,
        )
        tx2 = TransactionCreate(
            product_id=product_id_value,
            asset_id=asset.asset_id,
            investment_date=date(2025, 8, 4),
            maturity_date=None,
            interest_rate=None,
            quantity=2.0,
            unit_net_price=None,
            unit_full_price=20.0,
        )
        create_transaction(db_session, tx1)
        create_transaction(db_session, tx2)

        txs = get_transactions(db_session)
        assert len(txs) >= 2
        # 简单断言包含我们插入的数量
        quantities = sorted([float(getattr(t, "quantity")) for t in txs])
        assert 1.0 in quantities and 2.0 in quantities

    def test_negative_values_behavior_current_impl(self, db_session: Session):
        # 当前实现未对负值做显式校验；此用例记录现状（若后续加校验需改为断言异常）
        upsert_product_by_yindeng_code(
            db_session,
            WealthProductCreate(
                product_name="产品N2",
                product_yindeng_code="Y-N2",
                product_jinshu_code=None,
                product_custody_code=None,
                product_start_date=date(2025, 8, 1),
                product_end_date=date(2025, 8, 31),
                product_days_total=30,
                product_query_date=None,
                product_days_remaining=None,
                product_performance_benchmark=None,
                product_raise_target=None,
                product_raise_amount=None,
                product_raise_institutional=None,
                product_raise_retail=None,
            ),
        )
        product = get_product_by_yindeng_code(db_session, "Y-N2")
        assert product is not None
        product_id_value = int(getattr(product, "product_id"))

        asset = create_asset(
            db_session,
            AssetCreate(
                asset_name="资产N2",
                asset_code="AN02",
                asset_type="债券",
                issuer=None,
                industry=None,
                region=None,
            ),
        )

        tx = TransactionCreate(
            product_id=product_id_value,
            asset_id=asset.asset_id,
            investment_date=date(2025, 8, 5),
            maturity_date=None,
            interest_rate=-0.01,  # 负值
            quantity=-10.0,       # 负值
            unit_net_price=None,
            unit_full_price=-5.0, # 负值
        )
        created = create_transaction(db_session, tx)
        # 记录现状：若未抛错则直接断言已创建
        assert created is not None