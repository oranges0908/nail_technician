# Nail - Flutter + FastAPI 跨平台应用

## 项目简介

这是一个基于 Flutter + FastAPI + 数据库存储的跨平台移动应用项目。

## 技术栈

### 后端
- **FastAPI**: 现代、快速的 Python Web 框架
- **SQLAlchemy**: ORM 数据库操作
- **PostgreSQL/MySQL**: 关系型数据库
- **Redis**: 缓存和会话管理
- **Alembic**: 数据库迁移工具

### 前端
- **Flutter**: Google 跨平台 UI 框架
- **Provider/Riverpod**: 状态管理
- **Dio**: HTTP 客户端
- **Shared Preferences**: 本地存储

## 项目结构

```
nail/
├── backend/              # FastAPI 后端
│   ├── app/
│   │   ├── api/          # API 路由
│   │   │   └── v1/       # API v1 版本
│   │   ├── core/         # 核心配置
│   │   ├── db/           # 数据库配置
│   │   ├── models/       # SQLAlchemy 模型
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # 业务逻辑层
│   │   └── main.py       # 应用入口
│   ├── tests/            # 后端测试
│   ├── alembic/          # 数据库迁移
│   ├── requirements.txt  # Python 依赖
│   └── .env.example      # 环境变量示例
├── frontend/             # Flutter 前端
│   └── nail_app/         # Flutter 应用
├── docs/                 # 项目文档
├── docker-compose.yml    # Docker 编排
└── README.md
```

## 快速开始

### 后端启动

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 前端启动

```bash
cd frontend/nail_app
flutter pub get
flutter run
```

### Docker 启动

```bash
docker-compose up -d
```

## API 文档

后端启动后访问: http://localhost:8000/docs

## 开发规范

- 后端遵循 PEP 8 编码规范
- 前端遵循 Flutter 官方风格指南
- Git 提交信息采用约定式提交规范

## 许可证

MIT License