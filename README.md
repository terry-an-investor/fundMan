# FundMan - 理财产品数据管理工具

## 项目结构

```
fundman/
├── __init__.py
├── app.py          # 主应用模块
├── db.py           # 数据库操作模块
├── date_utils.py   # 日期处理模块
├── data_processor.py # 数据处理模块
└── main.py         # 程序入口点

data/
├── fund_report.db  # SQLite数据库文件
├── schema.sql      # 数据库模式定义
└── products.csv    # 示例数据文件

├── pyproject.toml  # 项目配置文件
└── README.md       # 项目说明文档
```

## 功能介绍

1. **数据库初始化** - 创建SQLite数据库和表结构
2. **数据导入** - 从CSV/XLS/XLSX文件导入理财产品数据
3. **数据导出** - 导出数据为CSV/XLSX格式
4. **动态查询** - 按指定日期查询产品信息和剩余天数

## 使用方法

```bash
# 导入数据
python main.py import data/products.csv

# 导出数据
python main.py export data/export.csv
python main.py export data/export.xlsx
```

## 数据格式

支持以下文件格式：
- CSV (UTF-8编码)
- XLS (Excel 97-2003格式)
- XLSX (Excel 2007+格式)

文件应包含以下列：
- 产品名称
- 银登编码
- 金数编码
- 托管编码
- 起息日
- 到期日
- 业绩基准
- 募集目标
- 募集金额
- 机构募集
- 个人募集

## 开发说明

项目采用模块化设计，各模块职责如下：
- `db.py` - 负责数据库连接和操作
- `date_utils.py` - 处理日期相关的函数
- `data_processor.py` - 处理数据文件导入导出(CSV/XLS/XLSX)
- `app.py` - 主应用程序逻辑