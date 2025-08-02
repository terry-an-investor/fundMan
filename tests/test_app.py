"""测试app.py模块的功能"""
import pytest
import sys
from unittest.mock import patch, MagicMock
from datetime import date

# 添加项目根目录到 Python 路径
sys.path.insert(0, '.')

from fundman.app import init_database, import_data, export_data, query_data


def test_init_database():
    """测试数据库初始化功能"""
    with patch('fundman.app.init_db') as mock_init_db:
        init_database()
        mock_init_db.assert_called_once()


def test_import_data():
    """测试数据导入功能"""
    with patch('fundman.app.import_data_file') as mock_import:
        import_data('test.csv', '2025-08-01')
        mock_import.assert_called_once_with('test.csv', '2025-08-01')


def test_export_data():
    """测试数据导出功能"""
    with patch('fundman.app.export_data_file') as mock_export:
        export_data('output.csv', '2025-08-01')
        mock_export.assert_called_once_with('output.csv', '2025-08-01')


@patch('fundman.app.query_dynamic')
@patch('fundman.app.get_db')
def test_query_data(mock_get_db, mock_query_dynamic):
    """测试数据查询功能"""
    # 创建模拟数据库会话
    mock_db = MagicMock()
    mock_get_db.return_value = iter([mock_db])
    
    # 创建模拟查询结果
    mock_result = MagicMock()
    mock_result.product_name = "测试产品"
    mock_result.product_days_remaining = 30
    mock_query_dynamic.return_value = [mock_result]
    
    # 执行查询
    query_data('2025-08-01')
    
    # 验证调用
    mock_get_db.assert_called_once()
    mock_query_dynamic.assert_called_once_with(mock_db, '2025-08-01')
    mock_db.close.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])