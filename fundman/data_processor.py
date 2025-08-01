import csv
from pathlib import Path
from typing import Optional
import pandas as pd
from .utils.date_utils import parse_date, days_between, days_remaining_on
from .database import get_db, get_all_products, upsert_product_by_yindeng_code
from .models import WealthProductCreate, WealthProductInDB
from datetime import date


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

    # 获取数据库会话
    db_gen = get_db()
    db = next(db_gen)
    try:
        count = 0
        # 将DataFrame转换为字典列表并逐行处理
        for row_num, (index, row) in enumerate(df.iterrows(), start=1):
            # 将pandas的NaN值转换为None，以便数据库处理
            r = {k: v if pd.notna(v) else None for k, v in row.to_dict().items()}
            
            name = (r.get("产品名称") or r.get("product_name") or "").strip()
            if not name:
                raise ValueError(f"第{row_num}行缺少 产品名称")

            start_date_str = r.get("起息日") or r.get("product_start_date") or ""
            end_date_str = r.get("到期日") or r.get("product_end_date") or ""
            
            start_date = parse_date(start_date_str) if start_date_str else None
            end_date = parse_date(end_date_str) if end_date_str else None
            
            # 只有当起息日和到期日都存在时才计算总天数
            days_total_val = days_between(start_date, end_date) if start_date and end_date else 0

            perf = parse_float(r.get("业绩基准") or r.get("product_performance_benchmark"))
            raise_target = parse_float(r.get("募集目标") or r.get("product_raise_target"))
            raise_amount = parse_float(r.get("募集金额") or r.get("product_raise_amount"))
            raise_inst = parse_float(r.get("机构募集") or r.get("product_raise_institutional"))
            raise_retail = parse_float(r.get("个人募集") or r.get("product_raise_retail"))

            # 创建Pydantic模型实例
            # 确保日期字段有默认值，不能为None
            start_date_obj = date.fromisoformat(start_date) if start_date and isinstance(start_date, str) and start_date.strip() else date.today()
            end_date_obj = date.fromisoformat(end_date) if end_date and isinstance(end_date, str) and end_date.strip() else date.today()
            query_date_obj = date.fromisoformat(qd_norm) if qd_norm and isinstance(qd_norm, str) and qd_norm.strip() else None
            
            product_create = WealthProductCreate(
                product_name=name,
                product_yindeng_code=(r.get("银登编码") or r.get("product_yindeng_code") or "").strip() or None,
                product_jinshu_code=(r.get("金数编码") or r.get("product_jinshu_code") or "").strip() or None,
                product_custody_code=(r.get("托管编码") or r.get("product_custody_code") or "").strip() or None,
                product_start_date=start_date_obj,
                product_end_date=end_date_obj,
                product_days_total=days_total_val,
                product_query_date=query_date_obj,
                product_days_remaining=days_remaining_on(end_date, qd_norm) if end_date and qd_norm else None,
                product_performance_benchmark=perf,
                product_raise_target=raise_target,
                product_raise_amount=raise_amount,
                product_raise_institutional=raise_inst,
                product_raise_retail=raise_retail,
            )
            
            # 使用CRUD操作插入或更新产品
            upsert_product_by_yindeng_code(db, product_create)
            count += 1
        db.commit()
        print(f"导入完成：{count} 条")
    finally:
        db.close()

def export_data_file(output_path: str, query_date: Optional[str] = None) -> None:
    """导出数据到文件(CSV/XLS/XLSX)"""
    path = Path(output_path)
    file_extension = path.suffix.lower()
    
    # 支持 .csv / .xls / .xlsx
    if file_extension not in ['.csv', '.xls', '.xlsx']:
        raise ValueError(f"不支持的文件格式: {file_extension}")

    # 获取数据库会话
    db_gen = get_db()
    db = next(db_gen)
    try:
        # 使用CRUD操作获取产品数据
        if query_date:
            qd_norm = parse_date(query_date)
            # 这里我们需要实现一个根据查询日期获取产品的CRUD操作
            # 由于我们没有直接的CRUD操作来根据查询日期筛选，我们先获取所有产品然后筛选
            all_products = get_all_products(db)
            # 筛选符合查询日期的产品
            products = []
            for p in all_products:
                # 将SQLAlchemy模型转换为Pydantic模型，再进行比较
                product_in_db = WealthProductInDB.model_validate(p)
                if product_in_db.product_query_date and product_in_db.product_query_date.isoformat() == qd_norm:
                    products.append(p)
        else:
            products = get_all_products(db)
        
        # 将产品数据转换为字典列表
        products_data = []
        for product in products:
            # 将SQLAlchemy模型转换为Pydantic模型，再转换为字典
            product_in_db = WealthProductInDB.model_validate(product)
            product_dict = product_in_db.model_dump()
            # 处理日期字段，将其转换为字符串格式
            for key, value in product_dict.items():
                if isinstance(value, date):
                    product_dict[key] = value.isoformat()
            products_data.append(product_dict)
        
        # 创建DataFrame
        df = pd.DataFrame(products_data)
        
        if file_extension == '.csv':
            df.to_csv(path, index=False, encoding='utf-8')
        elif file_extension == '.xlsx':
            # 默认使用openpyxl写入xlsx
            df.to_excel(path, index=False, engine='openpyxl')
        else:  # '.xls'
            # 尝试使用xlwt写入xls格式
            try:
                df.to_excel(path, index=False, engine='xlwt')
            except Exception as e:
                # 如果xlwt不可用，提供友好的错误信息
                error_msg = f"无法使用xlwt引擎导出XLS格式: {e}"
                suggestion = "提示: 您可以尝试导出为XLSX格式以获得更好的兼容性"
                print(f"警告: {error_msg}")
                print(suggestion)
                # 重新抛出异常，让调用者决定如何处理
                raise Exception(f"{error_msg}. {suggestion}") from e
            
        print(f"导出完成: {len(df)} 条")
    finally:
        db.close()