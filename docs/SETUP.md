# 项目搭建指南

## 环境要求

### 后端
- Python 3.11+
- PostgreSQL 15+ 或 MySQL 8+
- Redis 7+

### 前端
- Flutter SDK 3.16+
- Dart 3.2+
- Android Studio / Xcode (for mobile development)

## 后端搭建步骤

### 1. 创建虚拟环境

```bash
cd backend
python -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库等信息
```

### 4. 初始化数据库

```bash
# 创建数据库迁移
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 5. 启动后端服务

```bash
# 开发模式
uvicorn app.main:app --reload

# 或者使用 Python 直接运行
python -m app.main
```

访问 API 文档: http://localhost:8000/docs

## 前端搭建步骤

### 1. 创建 Flutter 项目

```bash
cd frontend
flutter create nail_app
cd nail_app
```

### 2. 安装依赖

编辑 `pubspec.yaml` 添加必要依赖，然后运行:

```bash
flutter pub get
```

### 3. 配置 API 地址

创建配置文件 `lib/config/api_config.dart`

### 4. 运行 Flutter 应用

```bash
# 查看可用设备
flutter devices

# 运行到指定设备
flutter run -d <device_id>

# 或直接运行（会自动选择设备）
flutter run
```

## Docker 部署

### 启动所有服务

```bash
docker-compose up -d
```

### 查看日志

```bash
docker-compose logs -f backend
```

### 停止服务

```bash
docker-compose down
```

### 重建服务

```bash
docker-compose up -d --build
```

## 数据库迁移

### 创建迁移

```bash
cd backend
alembic revision --autogenerate -m "描述信息"
```

### 应用迁移

```bash
alembic upgrade head
```

### 回滚迁移

```bash
alembic downgrade -1
```

## 测试

### 后端测试

```bash
cd backend
pytest
```

### 前端测试

```bash
cd frontend/nail_app
flutter test
```

## 常见问题

### 数据库连接失败

检查:
1. 数据库服务是否启动
2. `.env` 文件中的数据库配置是否正确
3. 数据库用户权限是否正确

### Flutter 依赖安装失败

尝试:
```bash
flutter pub cache repair
flutter clean
flutter pub get
```

### Docker 容器启动失败

检查:
```bash
docker-compose logs
docker ps -a
```
