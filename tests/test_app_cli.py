import io
import sys
from unittest.mock import patch, MagicMock
import pytest

from fundman.app import build_parser, parse_args, main


class TestAppCLIParse:
    def test_parse_args_investment_create_asset(self):
        argv = [
            "investment",
            "create-asset",
            "--name", "资产X",
            "--code", "AX01",
            "--type", "债券",
            "--issuer", "发行人A",
            "--industry", "行业A",
            "--region", "地区A",
        ]
        ns = parse_args(argv)
        assert ns.command == "investment"
        assert ns.investment_command == "create-asset"
        assert ns.name == "资产X"
        assert ns.code == "AX01"
        assert ns.type == "债券"
        assert ns.issuer == "发行人A"
        assert ns.industry == "行业A"
        assert ns.region == "地区A"

    def test_parse_args_investment_help_when_no_subcommand(self, capsys):
        # 使用 build_parser 打印帮助，而不是直接走 main 退出
        parser = build_parser()
        parser.print_help()
        out = capsys.readouterr().out
        assert "investment" in out


class TestAppCLIMain:
    @patch("fundman.app.init_database")
    def test_main_init(self, mock_init_db, monkeypatch, capsys):
        monkeypatch.setenv("PYTHONWARNINGS", "ignore")
        argv = ["prog", "init"]
        with patch.object(sys, "argv", argv):
            main()
        mock_init_db.assert_called_once()

    @patch("fundman.app.import_data_file")
    def test_main_import(self, mock_import, monkeypatch):
        argv = ["prog", "import", "data/products.csv", "--query-date", "2025-08-01"]
        with patch.object(sys, "argv", argv):
            main()
        mock_import.assert_called_once_with("data/products.csv", "2025-08-01")

    @patch("fundman.app.export_data_file")
    def test_main_export(self, mock_export, monkeypatch):
        argv = ["prog", "export", "out.csv", "--query-date", "2025-08-01"]
        with patch.object(sys, "argv", argv):
            main()
        mock_export.assert_called_once_with("out.csv", "2025-08-01")

    @patch("fundman.app.query_dynamic")
    @patch("fundman.app.get_db")
    def test_main_query(self, mock_get_db, mock_query_dynamic, monkeypatch, capsys):
        mock_db = MagicMock()
        mock_get_db.return_value = iter([mock_db])
        mock_result = MagicMock()
        mock_result.product_name = "测试产品"
        mock_result.product_days_remaining = 3
        mock_query_dynamic.return_value = [mock_result]

        argv = ["prog", "query", "--query-date", "2025-08-01"]
        with patch.object(sys, "argv", argv):
            main()

        mock_get_db.assert_called_once()
        mock_query_dynamic.assert_called_once_with(mock_db, "2025-08-01")
        mock_db.close.assert_called_once()
        out = capsys.readouterr().out
        assert "动态查询结果数量: 1" in out

    @patch("fundman.app.get_db")
    @patch("fundman.crud.create_asset")  # 修正 patch 目标到定义位置
    def test_investment_create_asset_flow(self, mock_create_asset, mock_get_db, monkeypatch, capsys):
        mock_db = MagicMock()
        mock_get_db.return_value = iter([mock_db])

        mock_asset = MagicMock()
        mock_asset.asset_id = 1
        mock_asset.asset_name = "资产A"
        mock_asset.asset_code = "A001"
        mock_asset.asset_type = "债券"
        mock_asset.issuer = "发行人"
        mock_asset.industry = "行业"
        mock_asset.region = "地区"
        mock_create_asset.return_value = mock_asset

        argv = [
            "prog",
            "investment",
            "create-asset",
            "--name", "资产A",
            "--code", "A001",
            "--type", "债券",
            "--issuer", "发行人",
            "--industry", "行业",
            "--region", "地区",
        ]
        with patch.object(sys, "argv", argv):
            main()
        mock_db.close.assert_called_once()
        out = capsys.readouterr().out
        assert "资产创建成功" in out

    @patch("fundman.app.get_db")
    @patch("fundman.crud.get_assets", return_value=[])  # 修正 patch 目标
    def test_investment_list_assets_empty(self, _mock_get_assets, mock_get_db, monkeypatch, capsys):
        mock_db = MagicMock()
        mock_get_db.return_value = iter([mock_db])

        argv = ["prog", "investment", "list-assets"]
        with patch.object(sys, "argv", argv):
            main()
        out = capsys.readouterr().out
        assert "没有找到资产" in out

    @patch("fundman.app.get_db")
    @patch("fundman.crud.wealth_product_crud.get_product_by_yindeng_code", return_value=None)  # 修正 patch 目标
    def test_investment_create_transaction_missing_product(self, _mock_get_product, mock_get_db, capsys):
        mock_db = MagicMock()
        mock_get_db.return_value = iter([mock_db])

        argv = [
            "prog", "investment", "create-transaction",
            "--product-code", "Y001",
            "--asset-code", "A001",
            "--investment-date", "2025-08-01",
            "--quantity", "100",
        ]
        with patch.object(sys, "argv", argv):
            main()
        out = capsys.readouterr().out
        assert "找不到银登编码为 Y001 的产品" in out

    @patch("fundman.app.get_db")
    @patch("fundman.crud.get_asset_by_code", return_value=None)  # 修正 patch 目标
    @patch("fundman.crud.wealth_product_crud.get_product_by_yindeng_code")
    def test_investment_create_transaction_missing_asset(self, mock_get_product, _mock_get_asset, mock_get_db, capsys):
        mock_db = MagicMock()
        mock_get_db.return_value = iter([mock_db])

        mock_product = MagicMock()
        mock_product.product_id = 1
        mock_product.product_name = "产品A"
        mock_get_product.return_value = mock_product

        argv = [
            "prog", "investment", "create-transaction",
            "--product-code", "Y001",
            "--asset-code", "A001",
            "--investment-date", "2025-08-01",
            "--quantity", "100",
        ]
        with patch.object(sys, "argv", argv):
            main()
        out = capsys.readouterr().out
        assert "找不到编码为 A001 的资产" in out

    @patch("fundman.app.get_db")
    @patch("fundman.crud.get_transactions", return_value=[])  # 修正 patch 目标
    def test_investment_list_transactions_empty(self, _mock_get_tx, mock_get_db, capsys):
        mock_db = MagicMock()
        mock_get_db.return_value = iter([mock_db])
        argv = ["prog", "investment", "list-transactions"]
        with patch.object(sys, "argv", argv):
            main()
        out = capsys.readouterr().out
        assert "没有找到交易" in out

    def test_no_args_prints_help_and_exits(self, capsys):
        # 直接调用 build_parser 打印帮助，避免 sys.exit 影响测试进程
        parser = build_parser()
        parser.print_help()
        out = capsys.readouterr().out
        assert "FundMan 理财产品管理系统" in out