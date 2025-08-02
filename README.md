# FundMan - 理财产品数据管理工具

## 项目结构

```
fundMan/
├── main.py                 # 主程序入口
├── pyproject.toml          # 项目依赖管理（含 pytest 覆盖率配置）
├── README.md               # 项目文档
├── data/                   # 数据文件目录
│   ├── products.csv        # 示例数据文件
│   └── fund_report.db      # SQLite数据库文件
├── fundman/                # 主应用包
│   ├── __init__.py
│   ├── app.py              # 主应用程序（CLI接口，已抽取 build_parser/parse_args 便于测试）
│   ├── data_processor.py   # 数据处理模块（导入/导出）
│   ├── crud/               # CRUD操作模块
│   │   ├── __init__.py
│   │   ├── wealth_product_crud.py # 理财产品CRUD操作
│   │   └── investment_crud.py     # 投资组合CRUD操作
│   ├── database/           # 数据库连接和初始化
│   │   ├── __init__.py
│   │   └── connection.py   # 数据库连接
│   ├── models/             # 数据模型模块
│   │   ├── __init__.py
│   │   ├── wealth_product.py # 理财产品数据模型（SQLAlchemy和Pydantic）
│   │   └── investment.py     # 投资组合数据模型（SQLAlchemy和Pydantic）
│   └── utils/              # 工具模块
│       ├── __init__.py
│       └── date_utils.py   # 日期处理工具
└── tests/                  # 测试套件
    ├── __init__.py
    ├── conftest.py         # 测试配置和fixtures（测试DB会话）
    ├── test_app.py         # app.py 函数级测试（init/import/export/query）
    ├── test_app_cli.py     # app.py CLI 分支测试（investment 子命令与错误分支）
    ├── test_database.py    # 数据库相关测试
    ├── test_wealth_products.py # 理财产品相关测试（基础CRUD）
    ├── test_assets.py      # 资产相关测试
    ├── test_transactions.py # 交易相关测试
    ├── test_queries.py     # 查询功能测试
    ├── test_data_processor.py # 导入/导出测试（CSV/XLSX、异常路径）
    └── test_crud_extra.py  # CRUD 覆盖增强测试（边界/更新/计算分支）
```

## 最新进展与覆盖率

- 已将原 demo.py 演示脚本重构为完整 pytest 测试套件。
- 引入 CLI 可测性改造：
  - 在 [`fundman/app.py`](fundman/app.py:1) 中新增 `build_parser()` 与 `parse_args(argv)`，测试可直接注入参数；
  - 新增 `_print_investment_help()`，避免依赖 argparse 私有属性。
- 覆盖率（截至最近一次运行）：
  - 总覆盖率：约 81%
  - 关键模块：
    - app.py：约 72%（CLI 主流程、多分支覆盖）
    - data_processor.py：约 96%（导入/导出、异常路径、XLS 引擎失败）
    - utils/date_utils.py：100%
    - crud/wealth_product_crud.py：约 57%（已补充 upsert 边界与局部更新）
    - crud/investment_crud.py：约 60%（已补充计算与查询分支）
- 覆盖率门槛配置：
  - 在 [`pyproject.toml`](pyproject.toml:1) 中已启用覆盖率门槛 `--cov-fail-under=65`，可在阶段性目标达成后逐步提升（建议至 75%/80%）。

运行测试与覆盖率报告
- 运行全部测试并显示覆盖率（终端摘要）：
  ```bash
  python -m pytest tests/ --cov=fundman --cov-report=term-missing
  ```
- 生成 HTML 覆盖率报告（在 htmlcov/ 目录）：
  ```bash
  python -m pytest tests/ --cov=fundman --cov-report=html
  # 打开 htmlcov/index.html 查看详细报告
  ```

## 功能介绍

1. 数据库初始化 - 创建SQLite数据库和表结构
2. 数据导入 - 从CSV/XLS/XLSX文件导入理财产品数据
3. 数据导出 - 导出数据为CSV/XLSX格式
4. 动态查询 - 按指定日期查询产品信息和剩余天数
5. 投资组合管理 - 管理资产和交易信息

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
- [`wealth_product.py`](fundman/models/wealth_product.py:1): 理财产品数据模型，包含SQLAlchemy和Pydantic模型
- [`investment.py`](fundman/models/investment.py:1): 投资组合数据模型，包含SQLAlchemy和Pydantic模型

### database/
包含数据库连接和初始化相关的代码：
- [`connection.py`](fundman/database/connection.py:1): 数据库连接和会话管理

### crud/
包含CRUD操作：
- [`wealth_product_crud.py`](fundman/crud/wealth_product_crud.py:1): 理财产品相关的CRUD操作
- [`investment_crud.py`](fundman/crud/investment_crud.py:1): 投资组合相关的CRUD操作

### utils/
包含工具函数：
- [`date_utils.py`](fundman/utils/date_utils.py:1): 日期处理相关的工具函数

### 主要文件
- [`app.py`](fundman/app.py:1): 主应用程序入口（CLI，可测试的参数解析）
- [`data_processor.py`](fundman/data_processor.py:1): 数据导入和导出处理器

### 测试套件
项目包含完整的pytest测试套件，用于验证各项功能：
- [`tests/conftest.py`](tests/conftest.py:1): 测试配置和fixtures
- [`tests/test_app.py`](tests/test_app.py:1): app函数级测试
- [`tests/test_app_cli.py`](tests/test_app_cli.py:1): app CLI 分支测试
- [`tests/test_database.py`](tests/test_database.py:1): 数据库相关测试
- [`tests/test_wealth_products.py`](tests/test_wealth_products.py:1): 理财产品相关测试
- [`tests/test_assets.py`](tests/test_assets.py:1): 资产相关测试
- [`tests/test_transactions.py`](tests/test_transactions.py:1): 交易相关测试
- [`tests/test_queries.py`](tests/test_queries.py:1): 查询功能测试
- [`tests/test_data_processor.py`](tests/test_data_processor.py:1): 导入/导出测试
- [`tests/test_crud_extra.py`](tests/test_crud_extra.py:1): CRUD 覆盖增强测试

## 覆盖率提升路线图（已执行与后续建议）

- 已执行：
  - date_utils 100% 覆盖
  - data_processor 96% 覆盖（导入/导出、异常）
  - app CLI 分支测试完善，函数级与主流程分支覆盖
  - CRUD 增强测试覆盖 upsert 边界、局部更新、交易计算与查询

- 建议（可选增强，不改变业务语义）：
  - 在 CRUD 层添加输入校验与明确异常（如空编码、负数量/单价、无效外键）并补充断言异常测试，将 crud 覆盖提升至 75%+
  - 提升 CI 覆盖率门槛：
    - 当前：`--cov-fail-under=65`
    - 建议阶段性提升至 75%/80%
