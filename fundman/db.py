import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional

DB_PATH = "fund_report.db"
SCHEMA_FILE = "schema.sql"


def get_db_connection() -> sqlite3.Connection:
    """获取数据库连接"""
    return sqlite3.connect(DB_PATH)


def ensure_schema(conn: sqlite3.Connection) -> None:
    """确保数据库模式已创建"""
    # 优先使用 schema.sql，如果存在
    schema_path = Path(SCHEMA_FILE)
    if schema_path.exists():
        sql = schema_path.read_text(encoding="utf-8")
        conn.executescript(sql)
        conn.commit()
        return
    # 兜底内置表结构（与 schema.sql 一致）
    conn.executescript("""
    PRAGMA foreign_keys=OFF;
    CREATE TABLE IF NOT EXISTS wealth_products (
      product_id INTEGER PRIMARY KEY AUTOINCREMENT,
      product_name TEXT NOT NULL,
      product_yindeng_code TEXT,
      product_jinshu_code TEXT,
      product_custody_code TEXT,
      product_start_date TEXT NOT NULL,
      product_end_date TEXT NOT NULL,
      product_days_total INTEGER NOT NULL,
      product_query_date TEXT,
      product_days_remaining INTEGER,
      product_performance_benchmark REAL,
      product_raise_target REAL,
      product_raise_amount REAL,
      product_raise_institutional REAL,
      product_raise_retail REAL
    );
    CREATE UNIQUE INDEX IF NOT EXISTS ux_wealth_products_yindeng ON wealth_products(product_yindeng_code);
    CREATE INDEX IF NOT EXISTS ix_wealth_products_name ON wealth_products(product_name);
    """)
    conn.commit()


def _update_product(conn: sqlite3.Connection, row: Dict[str, Any], product_id: int) -> None:
    """更新产品信息"""
    conn.execute("""
    UPDATE wealth_products
       SET product_name=?,
           product_jinshu_code=?,
           product_custody_code=?,
           product_start_date=?,
           product_end_date=?,
           product_days_total=?,
           product_query_date=?,
           product_days_remaining=?,
           product_performance_benchmark=?,
           product_raise_target=?,
           product_raise_amount=?,
           product_raise_institutional=?,
           product_raise_retail=?
      WHERE product_id=?
    """, (
        row["product_name"],
        row.get("product_jinshu_code"),
        row.get("product_custody_code"),
        row["product_start_date"],
        row["product_end_date"],
        row["product_days_total"],
        row.get("product_query_date"),
        row.get("product_days_remaining"),
        row.get("product_performance_benchmark"),
        row.get("product_raise_target"),
        row.get("product_raise_amount"),
        row.get("product_raise_institutional"),
        row.get("product_raise_retail"),
        product_id,
    ))


def _insert_product(conn: sqlite3.Connection, row: Dict[str, Any]) -> None:
    """插入新产品信息"""
    conn.execute("""
    INSERT INTO wealth_products(
      product_name, product_yindeng_code, product_jinshu_code, product_custody_code,
      product_start_date, product_end_date, product_days_total,
      product_query_date, product_days_remaining,
      product_performance_benchmark, product_raise_target, product_raise_amount,
      product_raise_institutional, product_raise_retail
    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        row["product_name"],
        row.get("product_yindeng_code"),
        row.get("product_jinshu_code"),
        row.get("product_custody_code"),
        row["product_start_date"],
        row["product_end_date"],
        row["product_days_total"],
        row.get("product_query_date"),
        row.get("product_days_remaining"),
        row.get("product_performance_benchmark"),
        row.get("product_raise_target"),
        row.get("product_raise_amount"),
        row.get("product_raise_institutional"),
        row.get("product_raise_retail"),
    ))


def upsert_by_yindeng(conn: sqlite3.Connection, row: Dict[str, Any]) -> None:
    """根据银登编码插入或更新产品信息"""
    # 以 product_yindeng_code 为唯一键；为空则直接插入
    ycode = row.get("product_yindeng_code")
    if ycode:
        cur = conn.execute("SELECT product_id FROM wealth_products WHERE product_yindeng_code = ?", (ycode,))
        hit = cur.fetchone()
        if hit:
            _update_product(conn, row, hit[0])
            return
    _insert_product(conn, row)


def query_dynamic(conn: sqlite3.Connection, query_date: str) -> None:
    """按给定查询日动态计算（不依赖快照列）"""
    sql = """
    SELECT
      product_id, product_name, product_yindeng_code, product_start_date, product_end_date,
      product_days_total,
      MAX(0, CAST(julianday(product_end_date) - julianday(?) AS INT)) AS days_remaining_calc,
      product_performance_benchmark, product_raise_target, product_raise_amount
    FROM wealth_products
    ORDER BY product_end_date ASC, product_id ASC
    """
    cur = conn.execute(sql, (query_date,))
    rows = cur.fetchall()
    for row in rows:
        print(row)


def init_db() -> None:
    """初始化数据库"""
    conn = get_db_connection()
    try:
        ensure_schema(conn)
        print("数据库初始化完成")
    finally:
        conn.close()