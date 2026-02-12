# Nail 系统运维操作手册

## 目录

1. [系统概述](#1-系统概述)
2. [环境要求](#2-环境要求)
3. [首次部署](#3-首次部署)
4. [服务管理](#4-服务管理)
5. [日常运维](#5-日常运维)
6. [API 手动测试](#6-api-手动测试)
7. [前端应用](#7-前端应用)
8. [Docker 部署](#8-docker-部署)
9. [故障排查](#9-故障排查)

---

## 1. 系统概述

Nail 是 AI 驱动的美甲师能力成长系统，由以下组件组成：

| 组件 | 技术栈 | 默认端口 |
|------|--------|----------|
| 后端 API | FastAPI + SQLAlchemy | 8000 |
| 前端 App | Flutter (iOS/Android/Web) | - |
| 数据库 | SQLite (开发) / PostgreSQL (生产) | 5432 |
| 缓存 | Redis | 6379 |

**核心 API 路由一览**：

| 路径前缀 | 功能 | 是否需要认证 |
|----------|------|-------------|
| `/api/v1/health` | 健康检查 | 否 |
| `/api/v1/system` | 系统信息 | 否 |
| `/api/v1/auth` | 注册/登录/刷新Token | 否 |
| `/api/v1/users` | 用户管理 | 是 |
| `/api/v1/customers` | 客户管理 | 是 |
| `/api/v1/designs` | AI 设计生成 | 是 |
| `/api/v1/services` | 服务记录 | 是 |
| `/api/v1/uploads` | 文件上传 | 是 |
| `/api/v1/inspirations` | 灵感图库 | 是 |
| `/api/v1/abilities` | 能力分析 | 是 |

---

## 2. 环境要求

### 开发环境（本地 SQLite 模式）

- Python 3.11+
- pip
- Flutter SDK（前端开发时需要）

### 生产环境（Docker 模式）

- Docker 20.10+
- Docker Compose 2.0+

### 可选依赖

- OpenAI API Key（AI 设计生成和对比分析功能）
- Redis（缓存，生产环境推荐）

---

## 3. 首次部署

### 3.1 本地开发部署

```bash
# 1. 克隆项目
cd /path/to/nail

# 2. 配置环境变量
cp backend/.env.example backend/.env
# 编辑 backend/.env，至少设置以下项：
#   SECRET_KEY=<随机字符串>
#   OPENAI_API_KEY=<你的 OpenAI Key>（可选，AI 功能需要）

# 3. 创建 Python 虚拟环境
cd backend
python -m venv venv
source venv/bin/activate   # macOS/Linux
# venv\Scripts\activate    # Windows

# 4. 安装依赖
pip install -r requirements.txt

# 5. 初始化数据库
alembic upgrade head

# 6. 创建上传目录（通常自动创建）
mkdir -p uploads/{nails,inspirations,designs,actuals}

# 7. 启动服务
uvicorn app.main:app --reload
```

验证部署：
```bash
curl http://localhost:8000/health
# 期望返回: {"status": "healthy"}
```

### 3.2 Docker 部署

```bash
cd /path/to/nail

# 编辑 backend/.env（设置 OPENAI_API_KEY 等）

# 启动所有服务
docker-compose up -d

# 验证
curl http://localhost:8000/health
```

---

## 4. 服务管理

### 4.1 使用管理脚本（推荐）

项目提供了 `scripts/nail-service.sh` 脚本来管理服务：

```bash
# 启动后端服务（后台运行）
./scripts/nail-service.sh start

# 停止服务
./scripts/nail-service.sh stop

# 重启服务
./scripts/nail-service.sh restart

# 查看服务状态
./scripts/nail-service.sh status

# 查看实时日志
./scripts/nail-service.sh logs

# 初始化数据库（首次或重置）
./scripts/nail-service.sh init-db

# 运行测试
./scripts/nail-service.sh test
```

Docker 模式：

```bash
# 启动 Docker 全栈服务
./scripts/nail-service.sh docker-start

# 停止 Docker 服务
./scripts/nail-service.sh docker-stop

# 查看 Docker 日志
./scripts/nail-service.sh docker-logs
```

### 4.2 手动管理

```bash
cd backend

# 前台启动（开发调试用）
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 后台启动
source venv/bin/activate
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > logs/app.log 2>&1 &
echo $! > .pid

# 停止
kill $(cat .pid) && rm .pid
```

---

## 5. 日常运维

### 5.1 数据库操作

```bash
cd backend
source venv/bin/activate

# 查看当前迁移版本
alembic current

# 查看迁移历史
alembic history

# 执行迁移到最新
alembic upgrade head

# 回退一个版本
alembic downgrade -1

# 创建新迁移（修改 ORM 模型后）
alembic revision --autogenerate -m "描述"
```

### 5.2 日志查看

```bash
# 实时查看应用日志
tail -f backend/logs/app.log

# Docker 模式
docker-compose logs -f backend
```

### 5.3 代码质量检查

```bash
cd backend
source venv/bin/activate

black .          # 代码格式化
flake8           # Lint 检查
mypy app         # 类型检查
pytest           # 运行测试
```

### 5.4 数据备份

```bash
# SQLite 备份
cp backend/nail.db backend/nail.db.bak.$(date +%Y%m%d)

# 上传文件备份
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz backend/uploads/

# PostgreSQL 备份 (Docker 模式)
docker exec nail_postgres pg_dump -U nail_user nail_db > backup_$(date +%Y%m%d).sql
```

---

## 6. API 手动测试

### 6.1 通过 Swagger UI

浏览器打开 `http://localhost:8000/docs`，可交互式测试所有接口。

### 6.2 完整业务流程测试（curl）

**步骤 1：健康检查**

```bash
curl -s http://localhost:8000/api/v1/health | python -m json.tool
```

**步骤 2：注册用户**

```bash
curl -s -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "artist@example.com",
    "username": "nailartist",
    "password": "password123"
  }' | python -m json.tool
```

**步骤 3：登录获取 Token**

```bash
# 注意：登录接口是 OAuth2 表单格式，不是 JSON
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -d "username=artist@example.com&password=password123" \
  | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

echo "Token: $TOKEN"
```

**步骤 4：创建客户**

```bash
curl -s -X POST http://localhost:8000/api/v1/customers \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "张小花",
    "phone": "13800138000",
    "email": "xiaohua@example.com",
    "notes": "喜欢简约风格"
  }' | python -m json.tool
```

**步骤 5：查询客户列表**

```bash
curl -s http://localhost:8000/api/v1/customers \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool
```

**步骤 6：AI 生成设计方案**（需要 OpenAI API Key）

```bash
curl -s -X POST http://localhost:8000/api/v1/designs/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "prompt": "法式美甲，白色尖端配淡粉色底色，点缀金色亮片",
    "design_target": "10nails",
    "style_keywords": ["法式", "简约", "优雅"],
    "title": "春日法式美甲"
  }' | python -m json.tool
```

**步骤 7：上传实际完成照片**

```bash
curl -s -X POST http://localhost:8000/api/v1/uploads/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/photo.jpg" \
  -F "category=actuals" | python -m json.tool
```

**步骤 8：创建服务记录**

```bash
curl -s -X POST http://localhost:8000/api/v1/services \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "design_plan_id": 1,
    "service_date": "2026-02-11"
  }' | python -m json.tool
```

**步骤 9：完成服务并触发 AI 对比**（需要 OpenAI API Key）

```bash
curl -s -X POST http://localhost:8000/api/v1/services/1/complete \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "actual_image_path": "uploads/actuals/photo.jpg",
    "service_duration": 90,
    "materials_used": "甲油胶、底胶、封层、亮片",
    "artist_review": "渐变过渡可以更自然",
    "customer_satisfaction": 4
  }' | python -m json.tool
```

**步骤 10：查看 AI 对比结果**

```bash
curl -s http://localhost:8000/api/v1/services/1/comparison \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool
```

**步骤 11：查看能力分析**

```bash
curl -s http://localhost:8000/api/v1/abilities/summary \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool
```

---

## 7. 前端应用

### 7.1 运行 Flutter 前端

```bash
cd frontend/nail_app

# 安装依赖
flutter pub get

# 代码生成（修改 @JsonSerializable 模型后必须执行）
flutter pub run build_runner build --delete-conflicting-outputs

# 运行（自动选择设备）
flutter run

# 指定设备运行
flutter devices          # 查看可用设备
flutter run -d <device>  # 指定设备
flutter run -d chrome    # Web 模式
```

### 7.2 前端配置

API 地址配置位于 `frontend/nail_app/lib/config/api_config.dart`：

| 运行平台 | API 地址 |
|----------|----------|
| iOS 模拟器 | `http://localhost:8000` |
| Android 模拟器 | `http://10.0.2.2:8000` |
| 真机 | `http://<电脑IP>:8000` |
| Web | `http://localhost:8000` |

### 7.3 前端手动测试流程

1. 启动应用 → 看到登录页面
2. 点击注册 → 填写邮箱、用户名、密码 → 注册成功
3. 登录 → 进入主页
4. 客户管理 → 添加客户 → 填写姓名/电话
5. 设计生成 → 输入描述词 → 等待 AI 生成设计图
6. 服务记录 → 关联客户和设计方案 → 拍照上传完成效果
7. 能力中心 → 查看雷达图和成长曲线

---

## 8. Docker 部署

### 8.1 服务组成

```
┌─────────────────────────────────────────────┐
│  docker-compose                             │
│  ┌───────────┐ ┌───────┐ ┌───────────────┐  │
│  │ PostgreSQL│ │ Redis │ │   Backend     │  │
│  │  :5432    │ │ :6379 │ │   :8000       │  │
│  └───────────┘ └───────┘ └───────────────┘  │
│       ↑                         ↑           │
│  postgres_data            backend_uploads    │
└─────────────────────────────────────────────┘
```

### 8.2 常用命令

```bash
# 启动
docker-compose up -d

# 停止
docker-compose down

# 停止并删除数据卷（慎用！会丢失所有数据）
docker-compose down -v

# 重建镜像
docker-compose up -d --build

# 查看日志
docker-compose logs -f backend
docker-compose logs -f postgres

# 进入容器
docker exec -it nail_backend bash
docker exec -it nail_postgres psql -U nail_user nail_db
```

### 8.3 Docker 环境变量

Docker 模式下环境变量通过 `docker-compose.yml` 覆盖：

| 变量 | Docker 值 |
|------|-----------|
| `DATABASE_URL` | `postgresql://nail_user:nail_password@postgres:5432/nail_db` |
| `REDIS_HOST` | `redis` |

---

## 9. 故障排查

### 9.1 常见问题

| 问题 | 原因 | 解决方法 |
|------|------|----------|
| `ModuleNotFoundError` | 虚拟环境未激活 | `source backend/venv/bin/activate` |
| `alembic: command not found` | 未安装依赖 | `pip install -r requirements.txt` |
| 数据库表不存在 | 未执行迁移 | `alembic upgrade head` |
| 401 Unauthorized | Token 过期或缺失 | 重新登录获取 Token |
| AI 功能返回错误 | OpenAI Key 未设置或无效 | 检查 `.env` 中的 `OPENAI_API_KEY` |
| 端口 8000 被占用 | 有其他进程占用 | `lsof -i :8000` 找到并关闭 |
| Flutter build 报错 | `.g.dart` 文件过期 | `flutter pub run build_runner build --delete-conflicting-outputs` |

### 9.2 诊断命令

```bash
# 检查后端进程
lsof -i :8000

# 检查数据库文件
ls -la backend/nail.db

# 检查 Redis 连接
redis-cli ping

# 检查 Docker 服务状态
docker-compose ps

# 检查上传目录权限
ls -la backend/uploads/
```
