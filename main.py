import csv
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

DB_PATH = "report.db"
SCHEMA_FILE = "schema.sql"

def parse_date(s: str) -> str:
    s = (s or "").strip()
    if not s:
        raise ValueError("日期为空")
    # 常见格式：YYYY-MM-DD / YYYY/MM/DD / YYYY.MM.DD
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d"):
        try:
            return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    # 兜底：去除中文/其他分隔符
    s2 = s.replace("年", "-").replace("月", "-").replace("日", "").replace(".", "-").replace("/", "-")
    try:
        return datetime.strptime(s2, "%Y-%m-%d").strftime("%Y-%m-%d")
    except Exception:
        pass
    raise ValueError(f"无法解析日期: {s}")

def parse_float(s: Optional[str]) -> Optional[float]:
    if s is None:
        return None
    s = str(s).strip()
    if s == "" or s.lower() in {"null", "none", "nan"}:
        return None
    if s.endswith("%"):
        # 百分比转小数
        body = s[:-1].replace(",", "")
        return float(body) / 100.0
    return float(s.replace(",", ""))

def ensure_schema(conn: sqlite3.Connection) -> None:
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
    CREATE TABLE IF NOT EXISTS report_products (
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
    CREATE UNIQUE INDEX IF NOT EXISTS ux_report_products_yindeng ON report_products(product_yindeng_code);
    CREATE INDEX IF NOT EXISTS ix_report_products_name ON report_products(product_name);
    """)
    conn.commit()

def days_between(start_date: str, end_date: str) -> int:
    d1 = datetime.strptime(start_date, "%Y-%m-%d")
    d2 = datetime.strptime(end_date, "%Y-%m-%d")
    return (d2 - d1).days

def days_remaining_on(end_date: str, query_date: str) -> int:
    d_end = datetime.strptime(end_date, "%Y-%m-%d")
    d_q = datetime.strptime(query_date, "%Y-%m-%d")
    return max(0, (d_end - d_q).days)

def upsert_by_yindeng(conn: sqlite3.Connection, row: dict) -> None:
    # 以 product_yindeng_code 为唯一键；为空则直接插入
    ycode = row.get("product_yindeng_code")
    if ycode:
        cur = conn.execute("SELECT product_id FROM report_products WHERE product_yindeng_code = ?", (ycode,))
        hit = cur.fetchone()
        if hit:
            conn.execute("""
            UPDATE report_products
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
                hit[0],
            ))
            return
    conn.execute("""
    INSERT INTO report_products(
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

def import_csv(csv_path: str, query_date: Optional[str] = None) -> None:
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"CSV 未找到: {csv_path}")
    qd_norm = parse_date(query_date) if query_date else None

    conn = sqlite3.connect(DB_PATH)
    try:
        ensure_schema(conn)
        with path.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            count = 0
            for i, r in enumerate(reader, start=1):
                name = (r.get("产品名称") or r.get("product_name") or "").strip()
                if not name:
                    raise ValueError(f"第{i}行缺少 产品名称")

                start_date = parse_date(r.get("起息日") or r.get("product_start_date") or "")
                end_date = parse_date(r.get("到期日") or r.get("product_end_date") or "")
                days_total_val = days_between(start_date, end_date)

                perf = parse_float(r.get("业绩基准") or r.get("product_performance_benchmark"))
                raise_target = parse_float(r.get("募集目标") or r.get("product_raise_target"))
                raise_amount = parse_float(r.get("募集金额") or r.get("product_raise_amount"))
                raise_inst = parse_float(r.get("机构募集") or r.get("product_raise_institutional"))
                raise_retail = parse_float(r.get("个人募集") or r.get("product_raise_retail"))

                row = {
                    "product_name": name,
                    "product_yindeng_code": (r.get("银登编码") or r.get("yindeng_code") or "").strip() or None,
                    "product_jinshu_code": (r.get("金数编码") or r.get("jinshu_code") or "").strip() or None,
                    "product_custody_code": (r.get("托管编码") or r.get("custody_code") or "").strip() or None,
                    "product_start_date": start_date,
                    "product_end_date": end_date,
                    "product_days_total": days_total_val,
                    "product_query_date": qd_norm,
                    "product_days_remaining": days_remaining_on(end_date, qd_norm) if qd_norm else None,
                    "product_performance_benchmark": perf,
                    "product_raise_target": raise_target,
                    "product_raise_amount": raise_amount,
                    "product_raise_institutional": raise_inst,
                    "product_raise_retail": raise_retail,
                }
                upsert_by_yindeng(conn, row)
                count += 1
            conn.commit()
        print(f"导入完成：{count} 条")
    finally:
        conn.close()

def query_dynamic(query_date: str):
    qd = parse_date(query_date)
    conn = sqlite3.connect(DB_PATH)
    try:
        sql = """
        SELECT
          product_id, product_name, product_yindeng_code, product_start_date, product_end_date,
          product_days_total,
          MAX(0, CAST(julianday(product_end_date) - julianday(?) AS INT)) AS days_remaining_calc,
          product_performance_benchmark, product_raise_target, product_raise_amount
        FROM report_products
        ORDER BY product_end_date ASC, product_id ASC
        """
        cur = conn.execute(sql, (qd,))
        rows = cur.fetchall()
        for row in rows:
            print(row)
    finally:
        conn.close()

def init_db():
    conn = sqlite3.connect(DB_PATH)
    try:
        ensure_schema(conn)
        print("数据库初始化完成")
    finally:
        conn.close()

if __name__ == "__main__":
    # 使用指南：
    # 1) 首次初始化（可选）：
    #    init_db()
    #
    # 2) 从 CSV 导入并按查询日计算剩余期限快照（可选）：
    #    import_csv("products.csv", query_date="2025-08-01")
    #
    # 3) 按给定查询日动态计算（不依赖快照列）：
    #    query_dynamic("2025-08-01")
    pass
