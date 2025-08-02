# FundMan - 理财产品数据管理工具

## 项目结构

```
fundMan/
├── main.py                 # 主程序入口
├── pyproject.toml          # 项目依赖管理
├── README.md               # 项目文档
├── data/                   # 数据文件目录
│   ├── products.csv        # 示例数据文件
│   └── fund_report.db      # SQLite数据库文件
├── fundman/                # 主应用包
│   ├── __init__.py
│   ├── app.py              # 主应用程序（CLI接口）
│   ├── data_processor.py   # 数据处理模块
│   ├── crud/               # CRUD操作模块
│   │   ├── __init__.py
│   │   ├── wealth_product_crud.py # 理财产品CRUD操作
│   │   └── investment_crud.py # 投资组合CRUD操作
│   ├── database/           # 数据库连接和初始化
│   │   ├── __init__.py
│   │   └── connection.py   # 数据库连接
│   ├── models/             # 数据模型模块
│   │   ├── __init__.py
│   │   ├── wealth_product.py # 理财产品数据模型（SQLAlchemy和Pydantic）
│   │   └── investment.py # 投资组合数据模型（SQLAlchemy和Pydantic）
│   └── utils/              # 工具模块
│       ├── __init__.py
│       └── date_utils.py   # 日期处理工具
└── tests/                  # 测试套件
    ├── __init__.py
    ├── conftest.py         # 测试配置和fixtures
    ├── test_database.py    # 数据库相关测试
    ├── test_wealth_products.py # 理财产品相关测试
    ├── test_assets.py      # 资产相关测试
    ├── test_transactions.py # 交易相关测试
    └── test_queries.py     # 查询功能测试
```

## 功能介绍

1. **数据库初始化** - 创建SQLite数据库和表结构
2. **数据导入** - 从CSV/XLS/XLSX文件导入理财产品数据
3. **数据导出** - 导出数据为CSV/XLSX格式
4. **动态查询** - 按指定日期查询产品信息和剩余天数
5. **投资组合管理** - 管理资产和交易信息

## 使用方法

### 查看帮助
```bash
python -m fundman.app --help
```

### 初始化数据库
```bash
python -m fundman.app init
```

### 导入数据
```bash
python -m fundman.app import data/products.csv --query-date 2025-08-01
```

### 导出数据
```bash
python -m fundman.app export data/export.csv
python -m fundman.app export data/export.xlsx
```

### 查询数据
```bash
python -m fundman.app query --query-date 2025-08-01
```

### 投资组合管理

#### 查看投资组合管理帮助
```bash
python -m fundman.app investment --help
```

#### 创建资产
```bash
python -m fundman.app investment create-asset --name "资产名称" --code "资产编码" --type "资产类型" --issuer "发行人" --industry "行业" --region "地区"
```

#### 列出所有资产
```bash
python -m fundman.app investment list-assets
```

#### 创建交易
```bash
python -m fundman.app investment create-transaction --product-code "产品银登编码" --asset-code "资产编码" --investment-date "2025-08-01" --quantity "1000" --unit-full-price "10.2"
```

#### 列出所有交易
```bash
python -m fundman.app investment list-transactions
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

### models/
包含Pydantic和SQLAlchemy数据模型：
- `wealth_product.py`: 理财产品数据模型，包含SQLAlchemy和Pydantic模型
- `investment.py`: 投资组合数据模型，包含SQLAlchemy和Pydantic模型

### database/
包含数据库连接和初始化相关的代码：
- `connection.py`: 数据库连接和会话管理

### crud/
包含CRUD操作：
- `wealth_product_crud.py`: 理财产品相关的CRUD操作
- `investment_crud.py`: 投资组合相关的CRUD操作

### utils/
包含工具函数：
- `date_utils.py`: 日期处理相关的工具函数

### 主要文件
- `app.py`: 主应用程序入口
- `data_processor.py`: 数据导入和导出处理器

### 测试套件
项目包含完整的pytest测试套件，用于验证各项功能：
- `tests/conftest.py`: 测试配置和fixtures
- `tests/test_database.py`: 数据库相关测试
- `tests/test_wealth_products.py`: 理财产品相关测试
- `tests/test_assets.py`: 资产相关测试
- `tests/test_transactions.py`: 交易相关测试
- `tests/test_queries.py`: 查询功能测试

可以通过以下命令运行所有测试：
```bash
python -m pytest tests/