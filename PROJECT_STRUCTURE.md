# Nail 项目结构

## 完整目录结构

```
nail/
├── README.md                      # 项目主文档
├── PROJECT_STRUCTURE.md           # 本文件 - 项目结构说明
├── .gitignore                     # Git 忽略配置
├── docker-compose.yml             # Docker 编排配置
│
├── backend/                       # FastAPI 后端
│   ├── Dockerfile                 # 后端 Docker 镜像
│   ├── requirements.txt           # Python 依赖
│   ├── .env.example               # 环境变量模板
│   │
│   ├── app/                       # 应用主目录
│   │   ├── __init__.py
│   │   ├── main.py                # FastAPI 应用入口
│   │   │
│   │   ├── core/                  # 核心配置
│   │   │   ├── __init__.py
│   │   │   └── config.py          # 应用配置
│   │   │
│   │   ├── db/                    # 数据库配置
│   │   │   ├── __init__.py
│   │   │   └── database.py        # SQLAlchemy 配置
│   │   │
│   │   ├── models/                # SQLAlchemy 数据模型
│   │   │   ├── __init__.py
│   │   │   └── user.py            # 用户模型
│   │   │
│   │   ├── schemas/               # Pydantic Schemas
│   │   │   ├── __init__.py
│   │   │   ├── user.py            # 用户 Schema
│   │   │   └── token.py           # Token Schema
│   │   │
│   │   ├── api/                   # API 路由
│   │   │   ├── __init__.py
│   │   │   └── v1/                # API v1 版本
│   │   │       ├── __init__.py
│   │   │       ├── health.py      # 健康检查
│   │   │       ├── auth.py        # 认证接口
│   │   │       └── users.py       # 用户接口
│   │   │
│   │   └── services/              # 业务逻辑层
│   │       └── __init__.py
│   │
│   └── tests/                     # 测试目录
│       ├── __init__.py
│       └── test_main.py           # 主测试文件
│
├── frontend/                      # Flutter 前端
│   ├── README.md                  # 前端文档
│   ├── flutter_structure.md       # Flutter 结构详解
│   ├── pubspec_template.yaml      # 依赖配置模板
│   │
│   └── nail_app/                  # Flutter 项目 (需创建)
│       ├── lib/
│       │   ├── config/            # 配置文件
│       │   ├── models/            # 数据模型
│       │   ├── providers/         # 状态管理
│       │   ├── services/          # API 服务
│       │   ├── screens/           # 页面
│       │   ├── widgets/           # 组件
│       │   ├── utils/             # 工具类
│       │   ├── routes/            # 路由
│       │   └── main.dart          # 入口文件
│       │
│       ├── test/                  # 测试
│       ├── android/               # Android 配置
│       ├── ios/                   # iOS 配置
│       └── pubspec.yaml           # 依赖配置
│
└── docs/                          # 文档目录
    ├── API.md                     # API 文档
    └── SETUP.md                   # 搭建指南
```

## 技术栈详情

### 后端 (FastAPI)

**框架与库:**
- FastAPI 0.109.0 - Web 框架
- Uvicorn - ASGI 服务器
- SQLAlchemy 2.0.25 - ORM
- Alembic - 数据库迁移
- Pydantic 2.5.3 - 数据验证
- Python-Jose - JWT 认证
- Redis - 缓存

**数据库支持:**
- PostgreSQL (推荐)
- MySQL
- SQLite (开发环境)

**项目特点:**
- RESTful API 设计
- JWT 认证机制
- 自动 API 文档 (Swagger/ReDoc)
- 分层架构 (路由-服务-模型)
- 异步支持
- CORS 跨域支持

### 前端 (Flutter)

**核心依赖:**
- Flutter SDK 3.16+
- Dart 3.2+

**主要库:**
- dio - HTTP 客户端
- provider - 状态管理
- shared_preferences - 本地存储
- go_router - 路由导航
- json_serializable - JSON 序列化
- flutter_screenutil - 屏幕适配

**支持平台:**
- Android
- iOS
- Web (可选)
- Desktop (可选)

### 数据库

**PostgreSQL (推荐):**
- 完整的关系型数据库功能
- 适合生产环境
- Docker 容器化部署

**Redis:**
- 缓存
- Session 管理
- 消息队列 (可选)

## 项目特性

### 后端特性

1. **模块化设计**
   - 清晰的目录结构
   - 分离的配置、模型、路由、服务层

2. **开发友好**
   - 热重载支持
   - 自动生成 API 文档
   - 完善的类型提示

3. **生产就绪**
   - Docker 支持
   - 环境变量配置
   - 数据库迁移
   - 单元测试

4. **安全性**
   - JWT 认证
   - 密码加密
   - CORS 配置
   - SQL 注入防护 (ORM)

### 前端特性

1. **跨平台**
   - 一套代码，多端运行
   - 原生性能

2. **现代化开发**
   - 响应式设计
   - 状态管理
   - 路由导航

3. **工程化**
   - 代码生成
   - 类型安全
   - 模块化组织

## 快速开始

### 1. 后端启动

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

访问: http://localhost:8000/docs

### 2. 前端创建

```bash
cd frontend
flutter create nail_app
cd nail_app
# 将 pubspec_template.yaml 内容复制到 pubspec.yaml
flutter pub get
flutter run
```

### 3. Docker 部署

```bash
docker-compose up -d
```

## 开发流程

### 后端开发

1. 在 `models/` 创建数据模型
2. 在 `schemas/` 创建 Pydantic Schema
3. 在 `services/` 实现业务逻辑
4. 在 `api/v1/` 创建路由
5. 编写测试
6. 运行迁移更新数据库

### 前端开发

1. 在 `models/` 定义数据模型
2. 在 `services/` 实现 API 调用
3. 在 `providers/` 管理状态
4. 在 `screens/` 创建页面
5. 在 `widgets/` 创建可复用组件
6. 配置路由

## 下一步

- [ ] 创建 Flutter 项目: `cd frontend && flutter create nail_app`
- [ ] 配置后端环境变量: `cp backend/.env.example backend/.env`
- [ ] 安装后端依赖: `cd backend && pip install -r requirements.txt`
- [ ] 启动后端服务测试
- [ ] 实现用户认证功能
- [ ] 实现具体业务逻辑
- [ ] 配置 CI/CD
- [ ] 部署到生产环境

## 文档链接

- [项目主文档](./README.md)
- [后端 API 文档](./docs/API.md)
- [项目搭建指南](./docs/SETUP.md)
- [Flutter 前端文档](./frontend/README.md)
- [Flutter 结构详解](./frontend/flutter_structure.md)
