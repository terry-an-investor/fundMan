import io
import os
from pathlib import Path
from datetime import date
from unittest.mock import patch, MagicMock

import pandas as pd
import pytest

from fundman.data_processor import import_data_file, export_data_file


class TestImportDataFile:
    @pytest.fixture
    def tmp_csv(self, tmp_path: Path):
        df = pd.DataFrame(
            [
                {
                    "产品名称": "产品A",
                    "银登编码": "Y001",
                    "金数编码": "J001",
                    "托管编码": "T001",
                    "起息日": "2025-08-01",
                    "到期日": "2025-08-10",
                    "业绩基准": "5.5%",
                    "募集目标": "1,000,000",
                    "募集金额": "900000",
                    "机构募集": "700000",
                    "个人募集": "200000",
                },
                {
                    # 缺失到期日，days_total 应为 0
                    "产品名称": "产品B",
                    "银登编码": "Y002",
                    "起息日": "2025-08-01",
                    "到期日": None,
                    "业绩基准": "0.055",
                    "募集目标": None,
                    "募集金额": "1,234",
                    "机构募集": None,
                    "个人募集": "null",
                },
            ]
        )
        p = tmp_path / "import.csv"
        df.to_csv(p, index=False, encoding="utf-8")
        return p

    def test_import_csv_happy_path(self, tmp_csv: Path):
        mock_db = MagicMock()
        # 让 get_db() 返回一个可迭代，next() 获取到 mock_db
        with patch("fundman.data_processor.get_db", return_value=iter([mock_db])), patch(
            "fundman.data_processor.upsert_product_by_yindeng_code"
        ) as mock_upsert:
            import_data_file(str(tmp_csv), query_date="2025-08-01")
            # 两行数据各调用一次 upsert
            assert mock_upsert.call_count == 2
            # 提交一次
            mock_db.commit.assert_called_once()
            mock_db.close.assert_called_once()

    def test_import_missing_name_raises(self, tmp_path: Path):
        df = pd.DataFrame(
            [
                {
                    # 缺失产品名称，应该抛出 ValueError
                    "银登编码": "Y003",
                    "起息日": "2025-08-01",
                    "到期日": "2025-09-01",
                }
            ]
        )
        p = tmp_path / "bad.csv"
        df.to_csv(p, index=False, encoding="utf-8")

        mock_db = MagicMock()
        with patch("fundman.data_processor.get_db", return_value=iter([mock_db])):
            with pytest.raises(ValueError):
                import_data_file(str(p), query_date="2025-08-01")
            # 即使抛错也应关闭
            mock_db.close.assert_called_once()

    def test_import_percent_and_numbers(self, tmp_path: Path):
        df = pd.DataFrame(
            [
                {
                    "产品名称": "产品C",
                    "起息日": "2025-08-01",
                    "到期日": "2025-08-31",
                    "业绩基准": "10%",
                    "募集目标": "1,000",
                    "募集金额": "2,000.50",
                    "机构募集": "nan",
                    "个人募集": "None",
                }
            ]
        )
        p = tmp_path / "num.csv"
        df.to_csv(p, index=False, encoding="utf-8")

        mock_db = MagicMock()
        with patch("fundman.data_processor.get_db", return_value=iter([mock_db])), patch(
            "fundman.data_processor.upsert_product_by_yindeng_code"
        ) as mock_upsert:
            import_data_file(str(p), query_date="2025-08-15")
            assert mock_upsert.call_count == 1
            mock_db.commit.assert_called_once()
            mock_db.close.assert_called_once()

    def test_import_xlsx_happy_path(self, tmp_path: Path, monkeypatch):
        # 跳过 openpyxl 真实写文件，直接构造 xlsx 文件
        # 这里直接通过 Pandas 写入，需要 openpyxl 存在环境，如无则跳过该用例
        try:
            import openpyxl  # noqa: F401
        except Exception:
            pytest.skip("openpyxl 不可用，跳过 xlsx 测试")

        df = pd.DataFrame(
            [
                {
                    "产品名称": "产品D",
                    "起息日": "2025-08-01",
                    "到期日": "2025-08-05",
                }
            ]
        )
        p = tmp_path / "import.xlsx"
        df.to_excel(p, index=False, engine="openpyxl")

        mock_db = MagicMock()
        with patch("fundman.data_processor.get_db", return_value=iter([mock_db])), patch(
            "fundman.data_processor.upsert_product_by_yindeng_code"
        ) as mock_upsert:
            import_data_file(str(p))
            assert mock_upsert.call_count == 1
            mock_db.commit.assert_called_once()
            mock_db.close.assert_called_once()


class TestExportDataFile:
    @pytest.fixture
    def fake_products(self):
        # 模拟 SQLAlchemy 实体，通过 Pydantic 验证时要有同名属性
        class Obj:
            def __init__(self, **kw):
                for k, v in kw.items():
                    setattr(self, k, v)

        return [
            Obj(
                product_id=1,
                product_name="产品A",
                product_yindeng_code="Y001",
                product_jinshu_code="J001",
                product_custody_code="T001",
                product_start_date=date(2025, 8, 1),
                product_end_date=date(2025, 8, 10),
                product_days_total=9,
                product_query_date=date(2025, 8, 1),
                product_days_remaining=9,
                product_performance_benchmark=0.055,
                product_raise_target=1_000_000,
                product_raise_amount=900_000,
                product_raise_institutional=700_000,
                product_raise_retail=200_000,
            ),
            Obj(
                product_id=2,
                product_name="产品B",
                product_yindeng_code=None,
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
        ]

    def test_export_csv_by_all(self, tmp_path: Path, fake_products):
        out = tmp_path / "out.csv"
        mock_db = MagicMock()
        with patch("fundman.data_processor.get_db", return_value=iter([mock_db])), patch(
            "fundman.data_processor.get_all_products", return_value=fake_products
        ):
            export_data_file(str(out))
            assert out.exists()
            content = out.read_text(encoding="utf-8")
            # 简单检查关键字段与日期序列化
            assert "product_name" in content
            assert "2025-08-01" in content
            mock_db.close.assert_called_once()

    def test_export_csv_with_query_date_filter(self, tmp_path: Path, fake_products):
        out = tmp_path / "out2.csv"
        mock_db = MagicMock()
        with patch("fundman.data_processor.get_db", return_value=iter([mock_db])), patch(
            "fundman.data_processor.get_all_products", return_value=fake_products
        ):
            export_data_file(str(out), query_date="2025-08-01")
            content = out.read_text(encoding="utf-8")
            # 仅应包含 query_date == 2025-08-01 的第一条
            assert "产品A" in content
            assert "产品B" not in content

    def test_export_xlsx(self, tmp_path: Path, fake_products):
        try:
            import openpyxl  # noqa: F401
        except Exception:
            pytest.skip("openpyxl 不可用，跳过 xlsx 测试")

        out = tmp_path / "out.xlsx"
        mock_db = MagicMock()
        with patch("fundman.data_processor.get_db", return_value=iter([mock_db])), patch(
            "fundman.data_processor.get_all_products", return_value=fake_products
        ):
            export_data_file(str(out))
            assert out.exists()

    def test_export_xls_engine_failure(self, tmp_path: Path, fake_products, capsys):
        out = tmp_path / "out.xls"
        mock_db = MagicMock()
        with patch("fundman.data_processor.get_db", return_value=iter([mock_db])), patch(
            "fundman.data_processor.get_all_products", return_value=fake_products
        ), patch("pandas.DataFrame.to_excel", side_effect=Exception("xlwt engine missing")):
            with pytest.raises(Exception) as ei:
                export_data_file(str(out))
            captured = capsys.readouterr()
            assert "无法使用xlwt引擎导出XLS格式" in captured.out
            assert "提示: 您可以尝试导出为XLSX格式以获得更好的兼容性" in captured.out
            assert "xlwt engine missing" in str(ei.value)

    def test_export_unsupported_extension_raises(self, tmp_path: Path):
        out = tmp_path / "out.txt"
        with pytest.raises(ValueError):
            export_data_file(str(out))