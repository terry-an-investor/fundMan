from typing import Optional
from .db import init_db, query_dynamic, get_db_connection
from .data_processor import import_csv
from .date_utils import parse_date


def main() -> None:
    """主函数"""
    # 使用指南：
    # 1) 首次初始化（可选）：
    # init_db()
    #
    # 2) 从 CSV 导入并按查询日计算剩余期限快照（可选）：
    # import_csv("products.csv", query_date="2025-08-01")
    #
    # 3) 按给定查询日动态计算（不依赖快照列）：
    # conn = get_db_connection()
    # try:
    #     query_dynamic(conn, "2025-08-01")
    # finally:
    #     conn.close()
    
    # 默认执行示例功能
    # 1) 初始化数据库
    init_db()
    
    # 2) 从 CSV 导入数据
    import_csv("products.csv", query_date="2025-08-01")
    
    # 3) 动态查询
    conn = get_db_connection()
    try:
        query_dynamic(conn, "2025-08-01")
    finally:
        conn.close()


if __name__ == "__main__":
    main()