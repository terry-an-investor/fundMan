PRAGMA foreign_keys=OFF;
CREATE TABLE IF NOT EXISTS report_products (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  yindeng_code TEXT,
  jinshu_code TEXT,
  custody_code TEXT,
  start_date TEXT NOT NULL,   -- YYYY-MM-DD
  end_date TEXT NOT NULL,     -- YYYY-MM-DD
  days_total INTEGER NOT NULL,
  query_date TEXT,            -- 快照查询日（可空）
  days_remaining INTEGER,     -- 剩余天数快照（可空）
  performance_benchmark REAL, -- 建议存小数：5.2% 存 0.052
  raise_target REAL,
  raise_amount REAL,
  raise_institutional REAL,
  raise_retail REAL
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_report_products_yindeng ON report_products(yindeng_code);
-- 可选索引
-- CREATE UNIQUE INDEX IF NOT EXISTS ux_report_products_jinshu ON report_products(jinshu_code);
-- CREATE INDEX IF NOT EXISTS ix_report_products_end_date ON report_products(end_date);