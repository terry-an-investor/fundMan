PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS wealth_products (
  product_id INTEGER PRIMARY KEY AUTOINCREMENT,
  product_name TEXT NOT NULL,
  product_yindeng_code TEXT,
  product_jinshu_code TEXT,
  product_custody_code TEXT,
  product_start_date TEXT NOT NULL,   -- YYYY-MM-DD
  product_end_date TEXT NOT NULL,     -- YYYY-MM-DD
  product_days_total INTEGER NOT NULL,
  product_query_date TEXT,            -- 快照查询日（可空）
  product_days_remaining INTEGER,     -- 剩余天数快照（可空）
  product_performance_benchmark REAL, -- 建议存小数：5.2% 存 0.052
  product_raise_target REAL,
  product_raise_amount REAL,
  product_raise_institutional REAL,
  product_raise_retail REAL
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_wealth_products_yindeng ON wealth_products(yindeng_code);
CREATE INDEX IF NOT EXISTS ix_wealth_products_name ON wealth_products(product_name);
-- 可选索引
-- CREATE UNIQUE INDEX IF NOT EXISTS ux_wealth_products_jinshu ON wealth_products(jinshu_code);
-- CREATE INDEX IF NOT EXISTS ix_wealth_products_end_date ON wealth_products(end_date);