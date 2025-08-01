import csv
from pathlib import Path
from typing import Optional
import pandas as pd
from .date_utils import parse_date, days_between, days_remaining_on
from .db import get_db_connection, ensure_schema, upsert_by_yindeng


def parse_float(s: Optional[str]) -> Optional[float]:
    """解析浮点数，支持百分比格式"""
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


def import_data_file(file_path: str, query_date: Optional[str] = None) -> None:
    """从数据文件（CSV/XLS/XLSX）导入数据"""
    # 如果路径不是绝对路径，尝试在data目录中查找
    path = Path(file_path)
    if not path.exists() and not path.is_absolute():
        path = Path("data") / file_path
    if not path.exists():
        raise FileNotFoundError(f"文件未找到: {file_path}")
    
    # 检测文件扩展名并选择适当的读取方法
    file_extension = path.suffix.lower()
    
    if file_extension == '.csv':
        df = pd.read_csv(path, encoding='utf-8')
    elif file_extension in ['.xls', '.xlsx']:
        df = pd.read_excel(path)
    else:
        raise ValueError(f"不支持的文件格式: {file_extension}")
    
    qd_norm = parse_date(query_date) if query_date else None

    conn = get_db_connection()
    try:
        ensure_schema(conn)
        count = 0
        # 将DataFrame转换为字典列表并逐行处理
        for row_num, (index, row) in enumerate(df.iterrows(), start=1):
            # 将pandas的NaN值转换为None，以便数据库处理
            r = {k: v if pd.notna(v) else None for k, v in row.to_dict().items()}
            
            name = (r.get("产品名称") or r.get("product_name") or "").strip()
            if not name:
                raise ValueError(f"第{row_num}行缺少 产品名称")

            start_date = parse_date(r.get("起息日") or r.get("product_start_date") or "")
            end_date = parse_date(r.get("到期日") or r.get("product_end_date") or "")
            days_total_val = days_between(start_date, end_date)

            perf = parse_float(r.get("业绩基准") or r.get("product_performance_benchmark"))
            raise_target = parse_float(r.get("募集目标") or r.get("product_raise_target"))
            raise_amount = parse_float(r.get("募集金额") or r.get("product_raise_amount"))
            raise_inst = parse_float(r.get("机构募集") or r.get("product_raise_institutional"))
            raise_retail = parse_float(r.get("个人募集") or r.get("product_raise_retail"))

            row_data = {
                "product_name": name,
                "product_yindeng_code": (r.get("银登编码") or r.get("product_yindeng_code") or "").strip() or None,
                "product_jinshu_code": (r.get("金数编码") or r.get("product_jinshu_code") or "").strip() or None,
                "product_custody_code": (r.get("托管编码") or r.get("product_custody_code") or "").strip() or None,
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
            upsert_by_yindeng(conn, row_data)
            count += 1
        conn.commit()
        print(f"导入完成：{count} 条")
    finally:
        conn.close()