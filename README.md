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
2. **CSV数据导入** - 从CSV文件导入理财产品数据
3. **动态查询** - 按指定日期查询产品信息和剩余天数

## 使用方法

```bash
python main.py
```

## 数据格式

CSV文件应包含以下列：
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
- `data_processor.py` - 处理CSV数据解析和导入
- `app.py` - 主应用程序逻辑