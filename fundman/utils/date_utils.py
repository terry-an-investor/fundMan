from datetime import datetime


def parse_date(s: str) -> str:
    """解析日期字符串，支持多种格式"""
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


def days_between(start_date: str, end_date: str) -> int:
    """计算两个日期之间的天数"""
    d1 = datetime.strptime(start_date, "%Y-%m-%d")
    d2 = datetime.strptime(end_date, "%Y-%m-%d")
    return (d2 - d1).days


def days_remaining_on(end_date: str, query_date: str) -> int:
    """计算在查询日期时的剩余天数"""
    d_end = datetime.strptime(end_date, "%Y-%m-%d")
    d_q = datetime.strptime(query_date, "%Y-%m-%d")
    return max(0, (d_end - d_q).days)