# FundMan 项目结构说明

## 目录结构

```
fundman/
├── __init__.py
├── app.py
├── data_processor.py
├── database/
│   ├── __init__.py
│   ├── connection.py
│   └── crud.py
├── models/
│   ├── __init__.py
│   ├── pydantic_models.py
│   └── sqlalchemy_models.py
└── utils/
    ├── __init__.py
    └── date_utils.py
```

## 模块说明

### models/
包含Pydantic和SQLAlchemy数据模型：

- `pydantic_models.py`: Pydantic数据模型，用于数据验证和序列化
- `sqlalchemy_models.py`: SQLAlchemy数据库模型，用于数据库操作

### database/
包含数据库连接和操作相关的代码：

- `connection.py`: 数据库连接和会话管理
- `crud.py`: 数据库的增删改查操作

### utils/
包含工具函数：

- `date_utils.py`: 日期处理相关的工具函数

## 主要文件

- `app.py`: 主应用程序入口
- `data_processor.py`: 数据导入和导出处理器

## 旧文件（已弃用）

以 `.old` 结尾的文件是重构前的旧版本，已不再使用，但保留作为备份：
- `crud.py.old`
- `database.py.old`
- `db.py.old`
- `models.py.old`