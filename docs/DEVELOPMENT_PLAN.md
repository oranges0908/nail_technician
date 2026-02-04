# 美甲师能力成长系统 - 开发流程规划

## 文档说明

本文档按照**框架层 → 基础模块 → 业务模块**的顺序，将系统开发分解为多个迭代（Iteration），每个迭代控制在**1000行代码以内**。

### 开发原则

1. **迭代开发流程**：每个迭代严格遵循 **分析 → 设计 → 实现 → 测试 → 校对修正** 的循环
2. **代码控制**：每个迭代代码量控制在1000行以内，确保质量和可审查性
3. **版本管理**：每完成一个迭代，必须创建Git commit节点，记录改动概要
4. **定期整理**：每完成一个阶段或3-5个迭代后，进行Claude compact整理上下文
5. **质量保证**：每个迭代必须通过测试，确保功能完整且无bug后才能进入下一迭代

---

## 开发阶段概览

```
阶段1: 框架层 (5个迭代)
  ├── Iteration 1.1: 数据库基础设施
  ├── Iteration 1.2: 认证与授权系统
  ├── Iteration 1.3: 文件上传服务
  ├── Iteration 1.4: 错误处理与日志
  └── Iteration 1.5: API文档与健康检查

阶段2: 基础模块 (3个迭代)
  ├── Iteration 2.1: 用户管理模块
  ├── Iteration 2.2: 客户档案管理
  └── Iteration 2.3: 客户详细档案

阶段3: AI抽象层 (2个迭代)
  ├── Iteration 3.1: AI Provider抽象接口
  └── Iteration 3.2: OpenAI Provider实现

阶段4: 核心业务模块 (7个迭代)
  ├── Iteration 4.1: 灵感图库管理
  ├── Iteration 4.2: AI设计方案生成
  ├── Iteration 4.3: 设计方案微调
  ├── Iteration 4.4: 服务记录管理
  ├── Iteration 4.5: AI对比分析
  ├── Iteration 4.6: 能力维度管理
  └── Iteration 4.7: 能力分析与可视化

阶段5: 前端开发 (6个迭代)
  ├── Iteration 5.1: Flutter项目基础架构
  ├── Iteration 5.2: 认证与用户模块
  ├── Iteration 5.3: 客户管理界面
  ├── Iteration 5.4: 设计生成界面
  ├── Iteration 5.5: 服务记录界面
  └── Iteration 5.6: 能力中心界面

总计: 23个迭代
```

---

## 阶段1: 框架层 (Backend Foundation)

### Iteration 1.1: 数据库基础设施

**目标**: 建立数据库连接、迁移系统、基础模型

**代码量估算**: ~300行

#### 1. 分析 (Analysis)

**需求分析**:
- 支持PostgreSQL、MySQL、SQLite三种数据库
- 使用SQLAlchemy ORM
- 使用Alembic进行数据库迁移
- 建立数据库会话管理和依赖注入

**技术选型**:
- SQLAlchemy 2.0+ (已确定)
- Alembic (已确定)
- 数据库URL通过环境变量配置

#### 2. 设计 (Design)

**文件结构**:
```
backend/
├── alembic/                    # 新建
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── alembic.ini                 # 新建
├── app/
│   ├── db/
│   │   └── database.py        # 已存在，需完善
│   └── models/
│       └── __init__.py        # 已存在，需完善
```

**数据库配置设计**:
- `database.py`: 增强数据库引擎配置（连接池、超时等）
- `alembic/env.py`: 配置迁移环境，自动导入所有模型

**迁移策略**:
- 初始化Alembic
- 配置`env.py`自动发现模型
- 创建初始迁移（空的，为后续做准备）

#### 3. 实现 (Implementation)

**任务清单**:
- [ ] 初始化Alembic: `alembic init alembic`
- [ ] 完善`backend/app/db/database.py`:
  - 增加连接池配置
  - 增加数据库健康检查函数
  - 增加create_tables()工具函数（仅用于测试）
- [ ] 配置`alembic/env.py`:
  - 导入settings获取DATABASE_URL
  - 自动导入app.models中的所有模型
  - 配置target_metadata = Base.metadata
- [ ] 修改`alembic.ini`:
  - 注释掉sqlalchemy.url（改用env.py动态获取）
- [ ] 创建数据库迁移脚本模板
- [ ] 添加数据库初始化文档到README

**预期文件改动**:
- 新建: `alembic/`目录及配置
- 修改: `app/db/database.py` (+50行)
- 修改: `alembic/env.py` (+30行)
- 新建: `docs/DATABASE.md` (+100行)

#### 4. 测试 (Testing)

**测试用例**:
```python
# tests/test_database.py
def test_database_connection():
    """测试数据库连接"""
    from app.db.database import engine
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        assert result.scalar() == 1

def test_get_db_dependency():
    """测试数据库依赖注入"""
    from app.db.database import get_db
    db = next(get_db())
    assert db is not None
    db.close()

def test_alembic_migration():
    """测试Alembic迁移系统"""
    # 运行 alembic upgrade head
    # 验证没有错误
```

**手动测试**:
```bash
# 1. 初始化数据库
cd backend
alembic upgrade head

# 2. 检查数据库表创建（当前应该为空）
# 使用psql或sqlite3查看

# 3. 测试回滚
alembic downgrade -1
alembic upgrade head

# 4. 运行pytest
pytest tests/test_database.py -v
```

#### 5. 校对与修正 (Review & Fix)

**检查项**:
- [ ] 数据库连接池配置是否合理
- [ ] 三种数据库（PostgreSQL/MySQL/SQLite）是否都能正常工作
- [ ] Alembic迁移是否能正常执行
- [ ] 测试是否全部通过
- [ ] 代码是否符合PEP 8规范（运行black和flake8）

**与原始设计对比**:
参考`docs/ARCHITECTURE.md`中的数据库架构部分，确保：
- 支持的数据库类型正确
- 连接池配置合理
- 符合FastAPI最佳实践

#### 6. Commit节点

```bash
git add backend/alembic backend/alembic.ini backend/app/db/database.py tests/test_database.py
git commit -m "feat(backend): implement database infrastructure with Alembic

- Initialize Alembic migration system
- Enhance database.py with connection pool config
- Add database health check function
- Configure auto-discovery of models in alembic/env.py
- Add database tests
- Support PostgreSQL, MySQL, SQLite

Estimated lines: ~300
Status: ✅ All tests passing"
```

---

### Iteration 1.2: 认证与授权系统

**目标**: 实现JWT认证、用户注册登录、权限控制

**代码量估算**: ~800行

#### 1. 分析 (Analysis)

**需求分析**:
- JWT Token认证（Access Token 30分钟，Refresh Token 7天）
- 用户注册、登录、退出、刷新Token
- 密码加密（bcrypt）
- 依赖注入获取当前用户
- 基于用户ID的数据隔离

**安全要求**:
- 密码使用bcrypt哈希
- Token签名使用HS256算法
- 生产环境必须更改SECRET_KEY

#### 2. 设计 (Design)

**文件结构**:
```
backend/app/
├── core/
│   ├── security.py            # 新建
│   └── dependencies.py        # 新建
├── models/
│   └── user.py               # 已存在，需完善
├── schemas/
│   ├── user.py               # 已存在，需完善
│   └── token.py              # 已存在，需完善
├── services/
│   └── auth_service.py       # 新建
└── api/v1/
    ├── auth.py               # 已存在，需实现
    └── users.py              # 已存在，需实现
```

**核心功能设计**:

1. **security.py**:
   - `hash_password(password: str) -> str`: 密码哈希
   - `verify_password(plain, hashed) -> bool`: 密码验证
   - `create_access_token(data: dict) -> str`: 生成Access Token
   - `create_refresh_token(data: dict) -> str`: 生成Refresh Token
   - `decode_token(token: str) -> dict`: 解码Token

2. **dependencies.py**:
   - `get_current_user(token: str, db: Session) -> User`: 从Token获取当前用户
   - `get_current_active_user()`: 获取激活用户（排除is_active=False）

3. **auth_service.py**:
   - `register_user(db, user_data) -> User`: 注册
   - `authenticate_user(db, email, password) -> User | None`: 认证
   - `refresh_access_token(db, refresh_token) -> dict`: 刷新Token

4. **API路由**:
   - `POST /api/v1/auth/register`: 注册
   - `POST /api/v1/auth/login`: 登录
   - `POST /api/v1/auth/refresh`: 刷新Token
   - `GET /api/v1/users/me`: 获取当前用户信息

#### 3. 实现 (Implementation)

**任务清单**:
- [ ] 完善`app/models/user.py`:
  - 添加is_active字段
  - 添加created_at, updated_at
- [ ] 实现`app/core/security.py`:
  - 密码哈希和验证
  - JWT Token生成和解码
- [ ] 实现`app/core/dependencies.py`:
  - get_current_user依赖
  - get_current_active_user依赖
- [ ] 实现`app/services/auth_service.py`:
  - 用户注册逻辑
  - 用户认证逻辑
  - Token刷新逻辑
- [ ] 完善`app/schemas/user.py`:
  - UserCreate, UserUpdate, UserInDB
- [ ] 完善`app/schemas/token.py`:
  - Token, TokenData
- [ ] 实现`app/api/v1/auth.py`:
  - 注册端点
  - 登录端点
  - 刷新Token端点
- [ ] 实现`app/api/v1/users.py`:
  - GET /me端点
- [ ] 创建数据库迁移:
  - `alembic revision --autogenerate -m "add users table"`
  - `alembic upgrade head`

**预期文件改动**:
- 新建: `app/core/security.py` (~150行)
- 新建: `app/core/dependencies.py` (~80行)
- 新建: `app/services/auth_service.py` (~120行)
- 修改: `app/models/user.py` (+30行)
- 修改: `app/schemas/user.py` (+80行)
- 修改: `app/schemas/token.py` (+40行)
- 修改: `app/api/v1/auth.py` (~150行)
- 修改: `app/api/v1/users.py` (~80行)
- 新建: `tests/test_auth.py` (~150行)

#### 4. 测试 (Testing)

**测试用例**:
```python
# tests/test_auth.py
def test_register_user(client):
    """测试用户注册"""
    response = client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "id" in response.json()

def test_login_success(client):
    """测试登录成功"""
    # 先注册
    client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "password123"
    })
    # 登录
    response = client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()

def test_login_wrong_password(client):
    """测试密码错误"""
    response = client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

def test_get_current_user(client):
    """测试获取当前用户"""
    # 注册并登录
    register_and_login(client)
    token = get_access_token(client)

    response = client.get("/api/v1/users/me", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"

def test_refresh_token(client):
    """测试刷新Token"""
    # 获取refresh_token
    refresh_token = get_refresh_token(client)

    response = client.post("/api/v1/auth/refresh", json={
        "refresh_token": refresh_token
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
```

**手动测试**:
```bash
# 1. 启动后端
uvicorn app.main:app --reload

# 2. 访问Swagger UI
# http://localhost:8000/docs

# 3. 测试注册
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"test","password":"pass123"}'

# 4. 测试登录
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"pass123"}'

# 5. 使用Token访问受保护端点
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer <access_token>"
```

#### 5. 校对与修正 (Review & Fix)

**检查项**:
- [ ] 密码是否使用bcrypt正确哈希
- [ ] JWT Token是否包含正确的过期时间
- [ ] Token刷新机制是否正常工作
- [ ] 未认证用户访问受保护端点是否返回401
- [ ] 所有测试是否通过
- [ ] 代码是否符合安全最佳实践

**安全审查**:
- [ ] 密码明文是否从响应中排除
- [ ] SECRET_KEY是否从环境变量读取
- [ ] Token过期时间是否合理
- [ ] 是否防止了常见的认证漏洞

**与原始设计对比**:
参考`docs/ARCHITECTURE.md`中的安全架构部分，确认：
- JWT配置符合设计（Access 30分钟，Refresh 7天）
- 密码加密方式正确
- API鉴权机制完整

#### 6. Commit节点

```bash
git add backend/app/core/security.py backend/app/core/dependencies.py \
  backend/app/services/auth_service.py backend/app/api/v1/auth.py \
  backend/app/api/v1/users.py backend/app/models/user.py \
  backend/app/schemas/ backend/alembic/versions/ tests/test_auth.py

git commit -m "feat(backend): implement JWT authentication system

- Add password hashing with bcrypt in security.py
- Implement JWT token generation and validation
- Add user registration and login endpoints
- Add current user dependency injection
- Add refresh token mechanism
- Create users table migration
- Add comprehensive auth tests

Security:
- Access token: 30 minutes
- Refresh token: 7 days
- Password: bcrypt hashed

Estimated lines: ~800
Status: ✅ All tests passing, security reviewed"
```

---

### Iteration 1.3: 文件上传服务

**目标**: 实现图片上传、存储、访问功能

**代码量估算**: ~400行

#### 1. 分析 (Analysis)

**需求分析**:
- 支持图片上传（JPG, PNG）
- 文件大小限制：10MB
- 按类型分目录存储（nails/, inspirations/, designs/, actuals/）
- 自动生成唯一文件名（避免覆盖）
- 通过HTTP访问已上传文件
- 文件验证（类型、大小）

**存储策略**:
- MVP阶段：本地文件系统（`backend/uploads/`）
- 未来：可迁移到对象存储（阿里云OSS/腾讯云COS）

#### 2. 设计 (Design)

**文件结构**:
```
backend/
├── app/
│   ├── core/
│   │   └── file_storage.py    # 新建
│   ├── schemas/
│   │   └── file.py            # 新建
│   └── api/v1/
│       └── upload.py          # 新建
├── uploads/                    # 运行时创建
│   ├── nails/
│   ├── inspirations/
│   ├── designs/
│   └── actuals/
```

**API设计**:
- `POST /api/v1/upload`: 通用上传接口
  - Query参数: `file_type` (nail/inspiration/design/actual)
  - Body: multipart/form-data
  - Response: `{"file_path": "/uploads/nails/xxx.jpg", "url": "http://..."}`

**文件命名规则**:
- 格式: `{timestamp}_{random_string}_{original_name}.{ext}`
- 示例: `1704038400_a3f2d1_nail_photo.jpg`

#### 3. 实现 (Implementation)

**任务清单**:
- [ ] 实现`app/core/file_storage.py`:
  - `validate_image_file(file)`: 验证文件类型和大小
  - `generate_unique_filename(original_name)`: 生成唯一文件名
  - `save_upload_file(file, file_type)`: 保存文件
  - `delete_file(file_path)`: 删除文件（工具函数）
- [ ] 创建`app/schemas/file.py`:
  - `FileUploadResponse`: 上传响应Schema
- [ ] 实现`app/api/v1/upload.py`:
  - 上传端点实现
  - 文件类型验证
  - 错误处理（文件过大、格式错误等）
- [ ] 修改`app/main.py`:
  - 添加静态文件服务: `app.mount("/uploads", StaticFiles(directory="uploads"))`
- [ ] 在`app/core/config.py`中添加配置:
  - `UPLOAD_DIR`, `MAX_UPLOAD_SIZE`, `ALLOWED_EXTENSIONS`
- [ ] 创建上传目录初始化脚本
- [ ] 添加`.gitignore`忽略`uploads/*`（保留目录结构）

**预期文件改动**:
- 新建: `app/core/file_storage.py` (~150行)
- 新建: `app/schemas/file.py` (~30行)
- 新建: `app/api/v1/upload.py` (~100行)
- 修改: `app/main.py` (+10行)
- 修改: `app/core/config.py` (+15行)
- 修改: `.gitignore` (+5行)
- 新建: `tests/test_upload.py` (~100行)

#### 4. 测试 (Testing)

**测试用例**:
```python
# tests/test_upload.py
def test_upload_image_success(client, auth_headers):
    """测试上传图片成功"""
    with open("tests/fixtures/test_image.jpg", "rb") as f:
        response = client.post(
            "/api/v1/upload?file_type=nail",
            files={"file": ("test.jpg", f, "image/jpeg")},
            headers=auth_headers
        )
    assert response.status_code == 200
    data = response.json()
    assert "file_path" in data
    assert "url" in data
    assert data["file_path"].startswith("/uploads/nails/")

def test_upload_file_too_large(client, auth_headers):
    """测试文件过大"""
    # 创建一个超过10MB的文件
    large_file = b"x" * (11 * 1024 * 1024)
    response = client.post(
        "/api/v1/upload?file_type=nail",
        files={"file": ("large.jpg", large_file, "image/jpeg")},
        headers=auth_headers
    )
    assert response.status_code == 413  # Payload Too Large

def test_upload_invalid_type(client, auth_headers):
    """测试无效文件类型"""
    response = client.post(
        "/api/v1/upload?file_type=nail",
        files={"file": ("test.txt", b"text content", "text/plain")},
        headers=auth_headers
    )
    assert response.status_code == 400

def test_access_uploaded_file(client, auth_headers):
    """测试访问上传的文件"""
    # 先上传
    with open("tests/fixtures/test_image.jpg", "rb") as f:
        upload_response = client.post(
            "/api/v1/upload?file_type=nail",
            files={"file": ("test.jpg", f, "image/jpeg")},
            headers=auth_headers
        )
    file_path = upload_response.json()["file_path"]

    # 访问文件
    response = client.get(file_path)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/")
```

**手动测试**:
```bash
# 1. 准备测试图片
wget https://via.placeholder.com/500 -O test.jpg

# 2. 上传图片
curl -X POST "http://localhost:8000/api/v1/upload?file_type=nail" \
  -H "Authorization: Bearer <token>" \
  -F "file=@test.jpg"

# 3. 访问上传的文件
# 使用返回的URL在浏览器中打开

# 4. 检查文件是否正确保存
ls -lh backend/uploads/nails/
```

#### 5. 校对与修正 (Review & Fix)

**检查项**:
- [ ] 文件类型验证是否正确
- [ ] 文件大小限制是否生效
- [ ] 文件命名是否唯一（避免覆盖）
- [ ] 各类型文件是否保存到正确目录
- [ ] 静态文件服务是否正常工作
- [ ] 所有测试是否通过
- [ ] 上传目录权限是否正确

**安全审查**:
- [ ] 是否验证了文件MIME类型
- [ ] 是否限制了文件扩展名
- [ ] 是否防止了路径遍历攻击
- [ ] 文件名是否经过清理

**与原始设计对比**:
参考`docs/ARCHITECTURE.md`中的文件存储架构，确认：
- 目录结构符合设计
- 文件命名规则合理
- 静态文件服务配置正确

#### 6. Commit节点

```bash
git add backend/app/core/file_storage.py backend/app/schemas/file.py \
  backend/app/api/v1/upload.py backend/app/main.py \
  backend/app/core/config.py backend/.gitignore tests/test_upload.py

git commit -m "feat(backend): implement file upload service

- Add file validation (type, size) in file_storage.py
- Implement image upload endpoint at /api/v1/upload
- Add static file serving at /uploads
- Create directory structure: nails/, inspirations/, designs/, actuals/
- Add unique filename generation with timestamp
- File size limit: 10MB
- Allowed types: JPG, PNG
- Add comprehensive upload tests

Estimated lines: ~400
Status: ✅ All tests passing, security reviewed"
```

---

### Iteration 1.4: 错误处理与日志

**目标**: 统一错误处理、日志记录、异常管理

**代码量估算**: ~350行

#### 1. 分析 (Analysis)

**需求分析**:
- 统一的异常处理机制
- 结构化日志记录
- 不同级别的日志（INFO, WARNING, ERROR）
- 请求/响应日志
- 数据库错误、AI错误的特定处理

**日志需求**:
- 开发环境：控制台输出 + 文件
- 生产环境：文件轮转（按日期）
- 关键操作记录（用户注册、AI调用、文件上传等）

#### 2. 设计 (Design)

**文件结构**:
```
backend/
├── app/
│   ├── core/
│   │   ├── exceptions.py      # 新建
│   │   └── logging.py         # 新建
│   └── middleware/
│       └── logging.py         # 新建
├── logs/                       # 运行时创建
│   ├── app.log
│   └── error.log
```

**自定义异常设计**:
```python
class NailAppException(Exception):
    """基础异常类"""

class AuthenticationError(NailAppException):
    """认证错误"""

class FileUploadError(NailAppException):
    """文件上传错误"""

class AIServiceError(NailAppException):
    """AI服务错误"""

class ResourceNotFoundError(NailAppException):
    """资源未找到"""
```

**日志中间件设计**:
- 记录每个请求的URL、方法、IP、耗时
- 记录响应状态码
- 错误时记录完整traceback

#### 3. 实现 (Implementation)

**任务清单**:
- [ ] 实现`app/core/exceptions.py`:
  - 自定义异常类
  - 异常到HTTP状态码的映射
- [ ] 实现`app/core/logging.py`:
  - 配置日志格式
  - 配置日志处理器（console + file）
  - 配置日志轮转
- [ ] 实现`app/middleware/logging.py`:
  - 请求日志中间件
  - 记录请求耗时
- [ ] 修改`app/main.py`:
  - 添加全局异常处理器
  - 注册日志中间件
- [ ] 在各模块中使用日志:
  - auth_service.py: 记录登录/注册
  - file_storage.py: 记录文件上传
- [ ] 创建`logs/`目录（.gitignore）

**预期文件改动**:
- 新建: `app/core/exceptions.py` (~100行)
- 新建: `app/core/logging.py` (~80行)
- 新建: `app/middleware/logging.py` (~70行)
- 修改: `app/main.py` (+50行)
- 修改: `app/services/auth_service.py` (+20行，添加日志)
- 修改: `app/core/file_storage.py` (+15行，添加日志)
- 修改: `.gitignore` (+2行)

#### 4. 测试 (Testing)

**测试用例**:
```python
# tests/test_exceptions.py
def test_custom_exception_handler(client):
    """测试自定义异常处理"""
    # 触发ResourceNotFoundError
    response = client.get("/api/v1/users/99999")
    assert response.status_code == 404
    assert "detail" in response.json()

def test_validation_error_handler(client):
    """测试验证错误处理"""
    response = client.post("/api/v1/auth/register", json={
        "email": "invalid-email",  # 无效邮箱
        "password": "123"
    })
    assert response.status_code == 422

# tests/test_logging.py
def test_request_logging(client, caplog):
    """测试请求日志"""
    with caplog.at_level(logging.INFO):
        client.get("/api/v1/health")

    # 验证日志中包含请求信息
    assert "GET /api/v1/health" in caplog.text

def test_error_logging(client, caplog):
    """测试错误日志"""
    with caplog.at_level(logging.ERROR):
        client.get("/api/v1/users/invalid")

    # 验证错误被记录
    assert "ERROR" in caplog.text
```

**手动测试**:
```bash
# 1. 启动应用，观察日志输出
uvicorn app.main:app --reload

# 2. 发起正常请求
curl http://localhost:8000/api/v1/health

# 3. 触发错误
curl http://localhost:8000/api/v1/users/99999

# 4. 检查日志文件
tail -f backend/logs/app.log
tail -f backend/logs/error.log

# 5. 验证日志轮转（等待日期变化或手动修改日期）
```

#### 5. 校对与修正 (Review & Fix)

**检查项**:
- [ ] 异常处理是否覆盖所有场景
- [ ] 日志格式是否清晰易读
- [ ] 日志级别使用是否正确
- [ ] 敏感信息（密码、Token）是否被过滤
- [ ] 日志文件是否正确轮转
- [ ] 所有测试是否通过

**日志审查**:
- [ ] 是否记录了足够的上下文信息
- [ ] 错误日志是否包含traceback
- [ ] 是否避免了日志过多影响性能

**与原始设计对比**:
参考`docs/ARCHITECTURE.md`中的监控和日志部分，确认：
- 日志策略符合设计
- 关键操作已记录

#### 6. Commit节点

```bash
git add backend/app/core/exceptions.py backend/app/core/logging.py \
  backend/app/middleware/logging.py backend/app/main.py \
  backend/.gitignore tests/test_exceptions.py tests/test_logging.py

git commit -m "feat(backend): implement error handling and logging system

- Add custom exception classes (AuthenticationError, FileUploadError, etc.)
- Implement structured logging with file rotation
- Add request/response logging middleware
- Add global exception handlers
- Configure log levels (INFO, WARNING, ERROR)
- Add logging to auth and file upload services
- Filter sensitive data from logs

Estimated lines: ~350
Status: ✅ All tests passing"
```

---

### Iteration 1.5: API文档与健康检查

**目标**: 完善API文档、健康检查、系统监控端点

**代码量估算**: ~200行

#### 1. 分析 (Analysis)

**需求分析**:
- 完善Swagger UI文档
- 添加健康检查端点（数据库、Redis）
- 添加系统信息端点
- API标签和分组
- Schema示例数据

#### 2. 设计 (Design)

**API端点设计**:
- `GET /health`: 基础健康检查
- `GET /api/v1/health`: 详细健康检查（数据库、Redis）
- `GET /api/v1/system/info`: 系统信息（版本、环境等）

**文档优化**:
- 添加API描述和示例
- 分组标签（Auth, Users, Upload, etc.）
- 添加Schema示例

#### 3. 实现 (Implementation)

**任务清单**:
- [ ] 完善`app/api/v1/health.py`:
  - 添加数据库健康检查
  - 添加Redis健康检查（如果已连接）
- [ ] 新建`app/api/v1/system.py`:
  - 系统信息端点
- [ ] 修改`app/main.py`:
  - 完善FastAPI配置（title, description, version）
  - 添加tags_metadata
- [ ] 在各路由中添加详细文档:
  - summary, description
  - response_model
  - 示例数据
- [ ] 添加OpenAPI自定义配置

**预期文件改动**:
- 修改: `app/api/v1/health.py` (+50行)
- 新建: `app/api/v1/system.py` (~50行)
- 修改: `app/main.py` (+40行)
- 修改: 各API路由文件（添加文档，+60行）

#### 4. 测试 (Testing)

**测试用例**:
```python
# tests/test_health.py
def test_health_check(client):
    """测试健康检查"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_detailed_health_check(client):
    """测试详细健康检查"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "database" in data
    assert "status" in data

def test_system_info(client):
    """测试系统信息"""
    response = client.get("/api/v1/system/info")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert "environment" in data
```

**手动测试**:
```bash
# 1. 访问Swagger UI
open http://localhost:8000/docs

# 2. 测试健康检查
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/health

# 3. 测试系统信息
curl http://localhost:8000/api/v1/system/info

# 4. 验证API文档完整性
# 在Swagger UI中测试各端点
```

#### 5. 校对与修正 (Review & Fix)

**检查项**:
- [ ] 健康检查是否正确反映系统状态
- [ ] API文档是否清晰易懂
- [ ] Schema示例是否准确
- [ ] 所有测试是否通过

#### 6. Commit节点

```bash
git add backend/app/api/v1/health.py backend/app/api/v1/system.py \
  backend/app/main.py backend/app/api/v1/ tests/test_health.py

git commit -m "feat(backend): enhance API documentation and health checks

- Add detailed health check with database and Redis status
- Add system info endpoint
- Enhance Swagger UI with tags and descriptions
- Add schema examples for all models
- Improve API route documentation

Estimated lines: ~200
Status: ✅ All tests passing
📝 Stage 1 Complete: Framework Layer Done"
```

**🎯 阶段1完成检查点**:
- [ ] 所有测试通过
- [ ] API文档完整
- [ ] 代码审查通过
- [ ] 执行`black`和`flake8`代码格式化

**💾 建议在此进行Claude Compact**: 阶段1完成，可以整理上下文

---

## 阶段2: 基础模块 (Core Business Modules)

### Iteration 2.1: 用户管理模块

**目标**: 完善用户CRUD、个人资料管理

**代码量估算**: ~500行

#### 1. 分析 (Analysis)

**需求分析**:
- 获取当前用户信息
- 更新用户个人资料（用户名、邮箱）
- 修改密码
- 删除账号（软删除，设置is_active=False）
- 用户列表（管理员功能，Post-MVP）

**业务规则**:
- 用户只能修改自己的信息
- 修改邮箱需验证新邮箱未被使用
- 修改密码需验证旧密码

#### 2. 设计 (Design)

**API端点**:
- `GET /api/v1/users/me`: 获取当前用户
- `PUT /api/v1/users/me`: 更新当前用户
- `PUT /api/v1/users/me/password`: 修改密码
- `DELETE /api/v1/users/me`: 删除账号

**Schemas**:
```python
class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None

class PasswordChange(BaseModel):
    old_password: str
    new_password: str
```

#### 3. 实现 (Implementation)

**任务清单**:
- [ ] 完善`app/services/user_service.py`:
  - `get_user_by_id(db, user_id)`
  - `update_user(db, user_id, update_data)`
  - `change_password(db, user_id, old_pwd, new_pwd)`
  - `deactivate_user(db, user_id)`
- [ ] 完善`app/schemas/user.py`:
  - UserUpdate, PasswordChange
- [ ] 实现`app/api/v1/users.py`:
  - GET /me
  - PUT /me
  - PUT /me/password
  - DELETE /me
- [ ] 添加验证逻辑（邮箱唯一性、密码强度）

**预期文件改动**:
- 新建: `app/services/user_service.py` (~150行)
- 修改: `app/schemas/user.py` (+80行)
- 修改: `app/api/v1/users.py` (+150行)
- 新建: `tests/test_users.py` (~120行)

#### 4. 测试 (Testing)

**测试用例**:
```python
def test_get_current_user(client, auth_headers):
    response = client.get("/api/v1/users/me", headers=auth_headers)
    assert response.status_code == 200

def test_update_user(client, auth_headers):
    response = client.put("/api/v1/users/me",
        headers=auth_headers,
        json={"username": "newname"})
    assert response.status_code == 200
    assert response.json()["username"] == "newname"

def test_change_password(client, auth_headers):
    response = client.put("/api/v1/users/me/password",
        headers=auth_headers,
        json={"old_password": "oldpass", "new_password": "newpass"})
    assert response.status_code == 200

def test_delete_user(client, auth_headers):
    response = client.delete("/api/v1/users/me", headers=auth_headers)
    assert response.status_code == 200
    # 验证用户is_active=False
```

#### 5. 校对与修正 (Review & Fix)

**检查项**:
- [ ] 用户只能修改自己的信息
- [ ] 邮箱唯一性验证
- [ ] 密码修改需验证旧密码
- [ ] 软删除正确实现
- [ ] 所有测试通过

#### 6. Commit节点

```bash
git commit -m "feat(backend): implement user management module

- Add user CRUD operations
- Add password change functionality
- Add soft delete for user accounts
- Add email uniqueness validation
- Add comprehensive user tests

Estimated lines: ~500
Status: ✅ All tests passing"
```

---

### Iteration 2.2: 客户档案管理

**目标**: 实现客户基础档案的增删改查

**代码量估算**: ~600行

#### 1. 分析 (Analysis)

**需求分析**:
- 创建客户档案（姓名、电话、备注）
- 列出当前用户的所有客户
- 获取客户详情
- 更新客户信息
- 删除客户（级联删除所有关联数据）

**数据隔离**:
- 每个美甲师只能看到自己的客户
- 通过`user_id`字段实现数据隔离

#### 2. 设计 (Design)

**数据库模型**:
```python
class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    phone = Column(String(20))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    user = relationship("User", back_populates="customers")
```

**API端点**:
- `POST /api/v1/customers`: 创建客户
- `GET /api/v1/customers`: 列出客户（分页、搜索）
- `GET /api/v1/customers/{id}`: 获取客户详情
- `PUT /api/v1/customers/{id}`: 更新客户
- `DELETE /api/v1/customers/{id}`: 删除客户

#### 3. 实现 (Implementation)

**任务清单**:
- [ ] 创建`app/models/customer.py`:
  - Customer模型
- [ ] 在`app/models/__init__.py`中导入Customer
- [ ] 创建`app/schemas/customer.py`:
  - CustomerCreate, CustomerUpdate, CustomerResponse
- [ ] 创建`app/services/customer_service.py`:
  - CRUD操作
  - 数据隔离逻辑
  - 分页和搜索
- [ ] 创建`app/api/v1/customers.py`:
  - 所有CRUD端点
- [ ] 在`app/api/v1/__init__.py`中注册路由
- [ ] 创建数据库迁移:
  - `alembic revision --autogenerate -m "add customers table"`
  - `alembic upgrade head`

**预期文件改动**:
- 新建: `app/models/customer.py` (~50行)
- 新建: `app/schemas/customer.py` (~80行)
- 新建: `app/services/customer_service.py` (~180行)
- 新建: `app/api/v1/customers.py` (~150行)
- 修改: `app/models/__init__.py` (+2行)
- 修改: `app/api/v1/__init__.py` (+2行)
- 新建: `tests/test_customers.py` (~140行)

#### 4. 测试 (Testing)

**测试用例**:
```python
def test_create_customer(client, auth_headers):
    response = client.post("/api/v1/customers",
        headers=auth_headers,
        json={"name": "张三", "phone": "13800138000"})
    assert response.status_code == 200
    assert response.json()["name"] == "张三"

def test_list_customers(client, auth_headers):
    # 创建几个客户
    create_customers(client, auth_headers, count=3)

    response = client.get("/api/v1/customers", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()["items"]) == 3

def test_get_customer(client, auth_headers):
    customer_id = create_customer(client, auth_headers)

    response = client.get(f"/api/v1/customers/{customer_id}",
        headers=auth_headers)
    assert response.status_code == 200

def test_update_customer(client, auth_headers):
    customer_id = create_customer(client, auth_headers)

    response = client.put(f"/api/v1/customers/{customer_id}",
        headers=auth_headers,
        json={"name": "李四"})
    assert response.status_code == 200
    assert response.json()["name"] == "李四"

def test_delete_customer(client, auth_headers):
    customer_id = create_customer(client, auth_headers)

    response = client.delete(f"/api/v1/customers/{customer_id}",
        headers=auth_headers)
    assert response.status_code == 200

def test_data_isolation(client, auth_headers_user1, auth_headers_user2):
    """测试数据隔离：用户2不能访问用户1的客户"""
    customer_id = create_customer(client, auth_headers_user1)

    response = client.get(f"/api/v1/customers/{customer_id}",
        headers=auth_headers_user2)
    assert response.status_code == 404
```

#### 5. 校对与修正 (Review & Fix)

**检查项**:
- [ ] 数据隔离是否正确（用户只能访问自己的客户）
- [ ] 分页功能是否正常
- [ ] 搜索功能是否准确
- [ ] 级联删除是否正确配置
- [ ] 所有测试通过

**与原始设计对比**:
参考`docs/ARCHITECTURE.md`中的数据库设计，确认customers表结构正确。

#### 6. Commit节点

```bash
git commit -m "feat(backend): implement customer management module

- Add Customer model with user relationship
- Implement customer CRUD operations
- Add data isolation by user_id
- Add pagination and search
- Create customers table migration
- Add comprehensive customer tests

Estimated lines: ~600
Status: ✅ All tests passing, data isolation verified"
```

---

### Iteration 2.3: 客户详细档案

**目标**: 实现客户详细档案（甲型特征、偏好、禁忌）

**代码量估算**: ~700行

#### 1. 分析 (Analysis)

**需求分析**:
- 客户详细档案（一对一关系）
- 甲型特征（形状、大小、状态）
- 颜色偏好、风格偏好（JSON数组）
- 禁忌事项（JSON数组）
- 档案照片（多张，JSON数组）

**业务规则**:
- 一个客户只有一个详细档案
- 档案可以在创建客户时一起创建，也可以后续创建
- 档案更新会覆盖旧数据（非增量）

#### 2. 设计 (Design)

**数据库模型**:
```python
class CustomerProfile(Base):
    __tablename__ = "customer_profiles"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"),
                         unique=True, nullable=False)
    nail_shape = Column(String(50))  # almond, square, oval, etc.
    nail_size = Column(String(20))   # small, medium, large
    nail_condition = Column(String(50))  # healthy, brittle, etc.
    color_preferences = Column(JSON)  # ["#FF69B4", "#FFB6C1"]
    style_preferences = Column(JSON)  # ["minimalist", "elegant"]
    prohibitions = Column(JSON)       # ["glitter", "long"]
    profile_images = Column(JSON)     # ["/uploads/nails/xxx.jpg"]
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer = relationship("Customer", back_populates="profile")
```

**API端点**:
- `POST /api/v1/customers/{customer_id}/profile`: 创建/更新档案
- `GET /api/v1/customers/{customer_id}/profile`: 获取档案
- `DELETE /api/v1/customers/{customer_id}/profile`: 删除档案

#### 3. 实现 (Implementation)

**任务清单**:
- [ ] 创建`app/models/customer_profile.py`
- [ ] 修改`app/models/customer.py`:
  - 添加profile relationship
- [ ] 创建`app/schemas/customer_profile.py`:
  - ProfileCreate, ProfileUpdate, ProfileResponse
- [ ] 创建`app/services/customer_profile_service.py`:
  - create_or_update_profile
  - get_profile
  - delete_profile
- [ ] 创建`app/api/v1/customer_profiles.py`:
  - 嵌套在customers路由下
- [ ] 修改customers API以包含profile信息
- [ ] 创建数据库迁移
- [ ] 上传档案照片的集成

**预期文件改动**:
- 新建: `app/models/customer_profile.py` (~60行)
- 修改: `app/models/customer.py` (+10行)
- 新建: `app/schemas/customer_profile.py` (~120行)
- 新建: `app/services/customer_profile_service.py` (~150行)
- 新建: `app/api/v1/customer_profiles.py` (~120行)
- 修改: `app/schemas/customer.py` (+40行，添加profile字段)
- 修改: `app/api/v1/__init__.py` (+2行)
- 新建: `tests/test_customer_profiles.py` (~200行)

#### 4. 测试 (Testing)

**测试用例**:
```python
def test_create_profile(client, auth_headers, customer_id):
    response = client.post(f"/api/v1/customers/{customer_id}/profile",
        headers=auth_headers,
        json={
            "nail_shape": "almond",
            "nail_size": "medium",
            "color_preferences": ["#FF69B4", "#FFB6C1"],
            "style_preferences": ["minimalist", "elegant"],
            "prohibitions": ["glitter"]
        })
    assert response.status_code == 200
    assert response.json()["nail_shape"] == "almond"

def test_get_profile(client, auth_headers, customer_id):
    create_profile(client, auth_headers, customer_id)

    response = client.get(f"/api/v1/customers/{customer_id}/profile",
        headers=auth_headers)
    assert response.status_code == 200
    assert "color_preferences" in response.json()

def test_update_profile(client, auth_headers, customer_id):
    create_profile(client, auth_headers, customer_id)

    response = client.post(f"/api/v1/customers/{customer_id}/profile",
        headers=auth_headers,
        json={"nail_shape": "square"})
    assert response.status_code == 200
    assert response.json()["nail_shape"] == "square"

def test_get_customer_with_profile(client, auth_headers, customer_id):
    create_profile(client, auth_headers, customer_id)

    response = client.get(f"/api/v1/customers/{customer_id}",
        headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["profile"] is not None
```

#### 5. 校对与修正 (Review & Fix)

**检查项**:
- [ ] JSON字段是否正确存储和检索
- [ ] 一对一关系是否正确
- [ ] 级联删除是否工作（删除客户时自动删除档案）
- [ ] 所有测试通过

**与原始设计对比**:
参考`docs/ARCHITECTURE.md`中的customer_profiles表设计，确认字段完整。

#### 6. Commit节点

```bash
git commit -m "feat(backend): implement customer profile management

- Add CustomerProfile model with one-to-one relationship
- Implement profile CRUD operations
- Add JSON fields for preferences and prohibitions
- Support nail characteristics (shape, size, condition)
- Add profile to customer response
- Create customer_profiles table migration
- Add comprehensive profile tests

Estimated lines: ~700
Status: ✅ All tests passing
📝 Stage 2 Complete: Basic Modules Done"
```

**🎯 阶段2完成检查点**:
- [ ] 用户管理模块测试通过
- [ ] 客户管理模块测试通过
- [ ] 客户档案模块测试通过
- [ ] 数据隔离正确实现
- [ ] API文档更新

**💾 建议在此进行Claude Compact**: 阶段2完成，可以整理上下文

---

## 阶段3: AI抽象层 (AI Provider Layer)

### Iteration 3.1: AI Provider抽象接口

**目标**: 定义AI服务抽象接口和工厂模式

**代码量估算**: ~400行

#### 1. 分析 (Analysis)

**需求分析**:
- 定义统一的AI服务接口
- 支持多种AI Provider（OpenAI、Baidu等）
- 工厂模式创建Provider实例
- 错误处理和重试机制
- 响应缓存（Redis）

**核心方法**:
1. `generate_design()`: 生成设计图
2. `refine_design()`: 微调设计
3. `estimate_execution()`: 评估耗时和用料
4. `compare_images()`: 对比分析

#### 2. 设计 (Design)

**文件结构**:
```
backend/app/services/ai/
├── __init__.py
├── base.py              # 抽象基类
├── factory.py           # 工厂类
├── exceptions.py        # AI相关异常
└── cache.py             # 缓存策略
```

**抽象接口设计**:
```python
from abc import ABC, abstractmethod
from typing import List, Dict

class AIProvider(ABC):
    @abstractmethod
    async def generate_design(
        self,
        prompt: str,
        reference_images: List[str],
        design_target: str = "single",
        **kwargs
    ) -> str:
        """生成设计图，返回图片URL"""
        pass

    @abstractmethod
    async def refine_design(
        self,
        original_image: str,
        refinement_instruction: str,
        **kwargs
    ) -> str:
        """微调设计，返回新图片URL"""
        pass

    @abstractmethod
    async def estimate_execution(
        self,
        design_image: str
    ) -> Dict:
        """评估设计落地信息"""
        pass

    @abstractmethod
    async def compare_images(
        self,
        design_image: str,
        actual_image: str
    ) -> Dict:
        """对比两张图片"""
        pass
```

**工厂模式**:
```python
class AIProviderFactory:
    _instances = {}

    @classmethod
    def get_provider(cls, provider_type: str = None) -> AIProvider:
        if provider_type is None:
            provider_type = settings.AI_PROVIDER

        if provider_type not in cls._instances:
            if provider_type == "openai":
                cls._instances[provider_type] = OpenAIProvider(...)
            elif provider_type == "baidu":
                raise NotImplementedError("Baidu provider not implemented")
            else:
                raise ValueError(f"Unknown provider: {provider_type}")

        return cls._instances[provider_type]
```

#### 3. 实现 (Implementation)

**任务清单**:
- [ ] 创建`app/services/ai/__init__.py`
- [ ] 实现`app/services/ai/base.py`:
  - AIProvider抽象基类
  - 方法签名和文档字符串
- [ ] 实现`app/services/ai/exceptions.py`:
  - AIProviderError
  - AIGenerationError
  - AIAnalysisError
- [ ] 实现`app/services/ai/factory.py`:
  - AIProviderFactory
  - 单例模式缓存
- [ ] 实现`app/services/ai/cache.py`:
  - AI响应缓存策略
  - Redis集成
- [ ] 在`app/core/config.py`添加配置:
  - AI_PROVIDER
  - AI_CACHE_TTL
- [ ] 创建AI相关schemas:
  - `app/schemas/ai.py`

**预期文件改动**:
- 新建: `app/services/ai/__init__.py` (~20行)
- 新建: `app/services/ai/base.py` (~150行)
- 新建: `app/services/ai/exceptions.py` (~40行)
- 新建: `app/services/ai/factory.py` (~80行)
- 新建: `app/services/ai/cache.py` (~100行)
- 修改: `app/core/config.py` (+15行)
- 新建: `tests/test_ai_factory.py` (~80行)

#### 4. 测试 (Testing)

**测试用例**:
```python
# tests/test_ai_factory.py
def test_factory_creates_provider():
    """测试工厂创建Provider"""
    from app.services.ai.factory import AIProviderFactory

    # 注意：这个测试会在OpenAI实现后才能真正通过
    # 现在测试工厂逻辑
    factory = AIProviderFactory()
    # 验证工厂方法存在
    assert hasattr(factory, 'get_provider')

def test_factory_singleton():
    """测试单例模式"""
    from app.services.ai.factory import AIProviderFactory

    provider1 = AIProviderFactory.get_provider("openai")
    provider2 = AIProviderFactory.get_provider("openai")

    assert provider1 is provider2  # 同一实例

def test_ai_exceptions():
    """测试AI异常"""
    from app.services.ai.exceptions import AIProviderError

    with pytest.raises(AIProviderError):
        raise AIProviderError("Test error")

# tests/test_ai_cache.py
def test_cache_set_get(redis_client):
    """测试缓存存取"""
    from app.services.ai.cache import AICache

    cache = AICache(redis_client)
    cache.set("test_prompt", {"result": "test"})

    result = cache.get("test_prompt")
    assert result["result"] == "test"

def test_cache_expiry(redis_client):
    """测试缓存过期"""
    from app.services.ai.cache import AICache
    import time

    cache = AICache(redis_client, ttl=1)
    cache.set("test", {"data": "value"})

    time.sleep(2)
    result = cache.get("test")
    assert result is None
```

#### 5. 校对与修正 (Review & Fix)

**检查项**:
- [ ] 抽象接口是否清晰明确
- [ ] 工厂模式是否正确实现
- [ ] 异常类型是否合理
- [ ] 缓存策略是否正确
- [ ] 所有测试通过

**与原始设计对比**:
参考`docs/ARCHITECTURE.md`中的AI Provider架构设计，确认：
- 接口方法完整
- 工厂模式符合设计
- 可扩展性满足要求

#### 6. Commit节点

```bash
git commit -m "feat(backend): implement AI provider abstraction layer

- Add AIProvider abstract base class
- Define interface methods (generate_design, refine_design, etc.)
- Implement AIProviderFactory with singleton pattern
- Add AI-specific exceptions
- Add Redis-based caching for AI responses
- Add AI configuration in settings

Design pattern: Abstract Factory + Strategy
Estimated lines: ~400
Status: ✅ Framework ready for provider implementations"
```

---

### Iteration 3.2: OpenAI Provider实现

**目标**: 实现OpenAI Provider（DALL-E 3 + GPT-4 Vision）

**代码量估算**: ~900行

#### 1. 分析 (Analysis)

**需求分析**:
- 使用DALL-E 3生成设计图
- 使用GPT-4 Vision进行图像分析
- 实现设计微调（Vision分析 + DALL-E重新生成）
- 实现耗时和用料评估
- 实现图像对比分析

**OpenAI API**:
- DALL-E 3: `client.images.generate()`
- GPT-4 Vision: `client.chat.completions.create()` with image_url

#### 2. 设计 (Design)

**文件结构**:
```
backend/app/services/ai/
└── openai_provider.py   # OpenAI实现
```

**Prompt设计策略**:
- 设计生成：结合客户偏好生成详细prompt
- 微调：先用Vision分析，再生成新prompt
- 评估：使用结构化prompt要求JSON输出
- 对比：同时传入两张图片进行分析

#### 3. 实现 (Implementation)

**任务清单**:
- [ ] 创建`app/services/ai/openai_provider.py`:
  - 继承AIProvider
  - 实现所有抽象方法
- [ ] 实现`generate_design()`:
  - 根据design_target调整prompt
  - 调用DALL-E 3
  - 下载并保存图片到本地
  - 返回本地路径
- [ ] 实现`refine_design()`:
  - 使用GPT-4 Vision分析原图
  - 应用refinement_instruction
  - 生成新prompt
  - 调用DALL-E 3
- [ ] 实现`estimate_execution()`:
  - 使用GPT-4 Vision分析设计
  - 提取耗时、材料、复杂度
  - 返回结构化数据
- [ ] 实现`compare_images()`:
  - 同时传入设计图和实际图
  - 分析相似度、差异、建议
  - 提取能力评分
- [ ] 添加工具方法:
  - `_build_prompt()`: 构建prompt
  - `_download_image()`: 下载图片
  - `_parse_json_response()`: 解析JSON
- [ ] 在`app/core/config.py`添加:
  - OPENAI_API_KEY
  - OPENAI_MODEL_TEXT
  - OPENAI_MODEL_IMAGE
- [ ] 添加requirements:
  - openai>=1.0.0

**预期文件改动**:
- 新建: `app/services/ai/openai_provider.py` (~600行)
- 修改: `app/core/config.py` (+10行)
- 修改: `backend/requirements.txt` (+1行)
- 新建: `tests/test_openai_provider.py` (~250行)
- 新建: `tests/fixtures/` (测试图片)

#### 4. 测试 (Testing)

**重要**: OpenAI API测试需要真实API Key，建议使用Mock

**测试策略**:
1. **Mock测试**（默认）：模拟OpenAI响应
2. **集成测试**（可选）：使用真实API Key，标记为`@pytest.mark.integration`

**测试用例**:
```python
# tests/test_openai_provider.py
import pytest
from unittest.mock import AsyncMock, patch

@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client"""
    with patch('openai.AsyncOpenAI') as mock:
        yield mock

def test_generate_design_single_nail(mock_openai_client):
    """测试生成单指设计"""
    from app.services.ai.openai_provider import OpenAIProvider

    # Mock DALL-E response
    mock_openai_client.return_value.images.generate = AsyncMock(
        return_value=Mock(data=[Mock(url="https://example.com/image.jpg")])
    )

    provider = OpenAIProvider(api_key="test")
    result = await provider.generate_design(
        prompt="Pink floral nail art",
        reference_images=[],
        design_target="single"
    )

    assert result.startswith("/uploads/designs/")

def test_refine_design(mock_openai_client):
    """测试微调设计"""
    # Mock GPT-4 Vision response
    mock_openai_client.return_value.chat.completions.create = AsyncMock(
        return_value=Mock(
            choices=[Mock(message=Mock(content="Refined prompt here"))]
        )
    )

    provider = OpenAIProvider(api_key="test")
    result = await provider.refine_design(
        original_image="/uploads/designs/original.jpg",
        refinement_instruction="Make it brighter"
    )

    assert result.startswith("/uploads/designs/")

def test_estimate_execution(mock_openai_client):
    """测试评估耗时"""
    mock_response = {
        "duration_min": 90,
        "duration_max": 120,
        "materials": [{"name": "Pink polish", "amount": "medium"}],
        "complexity": "medium"
    }

    mock_openai_client.return_value.chat.completions.create = AsyncMock(
        return_value=Mock(
            choices=[Mock(message=Mock(content=json.dumps(mock_response)))]
        )
    )

    provider = OpenAIProvider(api_key="test")
    result = await provider.estimate_execution("/uploads/designs/test.jpg")

    assert result["duration_min"] == 90
    assert result["complexity"] == "medium"

def test_compare_images(mock_openai_client):
    """测试图像对比"""
    mock_response = {
        "similarity_score": 85,
        "differences": {"color": "Slightly lighter"},
        "suggestions": ["Pay attention to color accuracy"]
    }

    provider = OpenAIProvider(api_key="test")
    result = await provider.compare_images(
        design_image="/uploads/designs/design.jpg",
        actual_image="/uploads/actuals/actual.jpg"
    )

    assert result["similarity_score"] == 85

@pytest.mark.integration
@pytest.mark.skip(reason="Requires real OpenAI API key")
def test_real_api_call():
    """集成测试：真实API调用"""
    import os
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY not set")

    provider = OpenAIProvider(api_key=api_key)
    result = await provider.generate_design(
        prompt="Simple pink nail art",
        reference_images=[],
        design_target="single"
    )

    assert os.path.exists(result)
```

**手动测试** (需要真实API Key):
```bash
# 1. 设置环境变量
export OPENAI_API_KEY=sk-your-api-key

# 2. 启动Python REPL
cd backend
python

# 3. 测试生成设计
from app.services.ai.factory import AIProviderFactory
import asyncio

async def test():
    provider = AIProviderFactory.get_provider("openai")
    result = await provider.generate_design(
        prompt="Elegant pink floral nail art",
        reference_images=[],
        design_target="single"
    )
    print(f"Generated: {result}")

asyncio.run(test())

# 4. 检查生成的图片
ls -lh backend/uploads/designs/
```

#### 5. 校对与修正 (Review & Fix)

**检查项**:
- [ ] 所有抽象方法是否正确实现
- [ ] Prompt是否清晰有效
- [ ] 图片下载和保存是否正确
- [ ] JSON解析是否健壮
- [ ] 错误处理是否完善
- [ ] API调用是否符合OpenAI最佳实践
- [ ] 成本控制（prompt长度、图片质量）

**成本优化**:
- [ ] 使用standard质量而非hd（节省成本）
- [ ] Prompt尽量精简
- [ ] 利用缓存避免重复调用

**与原始设计对比**:
参考`docs/ARCHITECTURE.md`中的OpenAI Provider设计，确认：
- 所有方法实现符合接口
- Prompt策略合理
- 错误处理完整

#### 6. Commit节点

```bash
git commit -m "feat(backend): implement OpenAI provider for AI services

- Implement OpenAIProvider class inheriting AIProvider
- Add DALL-E 3 integration for design generation
- Add GPT-4 Vision integration for image analysis
- Implement design refinement workflow
- Implement execution estimation (time and materials)
- Implement image comparison with similarity scoring
- Add image download and local storage
- Add comprehensive mock tests
- Add integration test markers for real API calls

APIs used:
- DALL-E 3: Image generation
- GPT-4 Vision: Image analysis

Estimated lines: ~900
Status: ✅ All mock tests passing
⚠️ Integration tests require OPENAI_API_KEY
📝 Stage 3 Complete: AI Layer Ready"
```

**🎯 阶段3完成检查点**:
- [ ] AI抽象层测试通过
- [ ] OpenAI Provider实现完整
- [ ] Mock测试全部通过
- [ ] （可选）集成测试通过
- [ ] API成本评估完成

**💾 建议在此进行Claude Compact**: 阶段3完成，AI层已就绪

---

## 阶段4: 核心业务模块 (Core Business Features)

### Iteration 4.1: 灵感图库管理

**目标**: 实现灵感图上传、标签管理、检索功能

**代码量估算**: ~550行

#### 1. 分析 (Analysis)

**需求分析**:
- 上传灵感图片
- 为图片添加标签（风格、颜色、季节等）
- 按标签检索图片
- 删除图片
- 列出所有灵感图（分页）

**业务规则**:
- 灵感图属于美甲师个人
- 支持批量上传
- 标签可以自由添加

#### 2. 设计 (Design)

**数据库模型**:
```python
class InspirationImage(Base):
    __tablename__ = "inspiration_images"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    image_path = Column(String(500), nullable=False)
    tags = Column(JSON)  # ["floral", "pink", "spring"]
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="inspiration_images")
```

**API端点**:
- `POST /api/v1/inspirations`: 上传灵感图
- `GET /api/v1/inspirations`: 列出灵感图（分页、标签筛选）
- `GET /api/v1/inspirations/{id}`: 获取灵感图详情
- `PUT /api/v1/inspirations/{id}`: 更新标签
- `DELETE /api/v1/inspirations/{id}`: 删除灵感图

#### 3-6. 实现、测试、校对、Commit

（详细步骤省略，参考前面的模式）

**预期文件改动**:
- 新建: `app/models/inspiration_image.py` (~40行)
- 新建: `app/schemas/inspiration.py` (~80行)
- 新建: `app/services/inspiration_service.py` (~150行)
- 新建: `app/api/v1/inspirations.py` (~150行)
- 新建: `tests/test_inspirations.py` (~130行)

**Commit节点**:
```bash
git commit -m "feat(backend): implement inspiration image gallery

- Add InspirationImage model
- Implement image upload with tagging
- Add tag-based search and filtering
- Add pagination for image listing
- Create inspiration_images table migration

Estimated lines: ~550
Status: ✅ All tests passing"
```

---

### Iteration 4.2: AI设计方案生成

**目标**: 实现AI设计方案生成功能

**代码量估算**: ~800行

#### 1. 分析 (Analysis)

**需求分析**:
- 基于客户档案生成设计方案
- 结合灵感图作为参考
- 支持自定义提示词
- 选择生成目标（1指/5指/10指）
- 自动评估耗时和用料
- 保存设计方案

**AI Prompt构建策略**:
```
基础Prompt = 客户偏好（颜色、风格） + 甲型特征 + 参考图描述
最终Prompt = 基础Prompt + 用户自定义提示词 + 生成目标描述
```

#### 2. 设计 (Design)

**数据库模型**:
```python
class DesignPlan(Base):
    __tablename__ = "design_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    customer_id = Column(Integer, ForeignKey("customers.id"))
    inspiration_image_ids = Column(JSON)  # [1, 2, 3]
    ai_prompt = Column(Text)  # 自动生成的prompt
    custom_prompt = Column(Text)  # 用户自定义
    design_target = Column(String(20), default="single")
    generated_image_path = Column(String(500))
    design_description = Column(Text)
    estimated_duration_min = Column(Integer)
    estimated_duration_max = Column(Integer)
    material_list = Column(JSON)
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
```

**API端点**:
- `POST /api/v1/designs/generate`: 生成设计方案

#### 3. 实现 (Implementation)

**核心逻辑**:
```python
# app/services/design_service.py
class DesignService:
    @staticmethod
    async def generate_design_plan(
        db: Session,
        user_id: int,
        customer_id: int,
        inspiration_image_ids: List[int],
        custom_prompt: str = "",
        design_target: str = "single"
    ):
        # 1. 获取客户档案
        customer = get_customer_with_profile(db, customer_id, user_id)

        # 2. 构建AI Prompt
        ai_prompt = build_prompt_from_profile(customer.profile)
        full_prompt = f"{ai_prompt}\n{custom_prompt}" if custom_prompt else ai_prompt

        # 3. 获取灵感图路径
        inspiration_images = get_inspiration_images(db, inspiration_image_ids, user_id)
        image_paths = [img.image_path for img in inspiration_images]

        # 4. 调用AI生成设计
        ai_provider = AIProviderFactory.get_provider()
        design_image_path = await ai_provider.generate_design(
            prompt=full_prompt,
            reference_images=image_paths,
            design_target=design_target
        )

        # 5. 评估耗时和用料
        estimation = await ai_provider.estimate_execution(design_image_path)

        # 6. 保存设计方案
        design_plan = DesignPlan(
            user_id=user_id,
            customer_id=customer_id,
            inspiration_image_ids=inspiration_image_ids,
            ai_prompt=ai_prompt,
            custom_prompt=custom_prompt,
            design_target=design_target,
            generated_image_path=design_image_path,
            estimated_duration_min=estimation["duration_min"],
            estimated_duration_max=estimation["duration_max"],
            material_list=estimation["materials"]
        )
        db.add(design_plan)
        db.commit()
        db.refresh(design_plan)

        return design_plan
```

**预期文件改动**:
- 新建: `app/models/design_plan.py` (~80行)
- 新建: `app/schemas/design.py` (~150行)
- 新建: `app/services/design_service.py` (~300行)
- 新建: `app/api/v1/designs.py` (~150行)
- 新建: `tests/test_designs.py` (~120行)

**Commit节点**:
```bash
git commit -m "feat(backend): implement AI design generation

- Add DesignPlan model
- Implement prompt building from customer profile
- Integrate AI provider for design generation
- Add automatic execution estimation
- Support custom prompts and design targets
- Create design_plans table migration

Estimated lines: ~800
Status: ✅ All tests passing (with AI mocks)"
```

---

### Iteration 4.3: 设计方案微调

**目标**: 实现基于现有设计的微调功能

**代码量估算**: ~500行

#### 1. 分析 (Analysis)

**需求分析**:
- 选择已有设计方案
- 输入微调指令（如"颜色调亮"、"增加金箔"）
- AI分析原设计并应用微调
- 保存为新版本，关联到原设计（parent_design_id）
- 保留微调历史

**版本管理**:
- 每次微调创建新记录
- parent_design_id指向原设计
- version字段递增

#### 2. 设计 (Design)

**API端点**:
- `POST /api/v1/designs/{id}/refine`: 微调设计

**工作流程**:
```
1. 获取原设计图片
2. 调用AI Provider的refine_design()
3. 生成新设计图片
4. 创建新DesignPlan记录（parent_design_id = 原设计ID）
5. version = parent.version + 1
6. 返回新设计方案
```

#### 3-6. 实现、测试、校对、Commit

**预期文件改动**:
- 修改: `app/models/design_plan.py` (+10行，添加parent_design_id)
- 修改: `app/services/design_service.py` (+150行)
- 修改: `app/api/v1/designs.py` (+80行)
- 新建: `tests/test_design_refinement.py` (~100行)

**Commit节点**:
```bash
git commit -m "feat(backend): implement design refinement feature

- Add parent_design_id for version tracking
- Implement design refinement workflow
- Add version history support
- Integrate AI refine_design() method
- Add refinement tests

Estimated lines: ~500
Status: ✅ All tests passing"
```

---

### Iteration 4.4: 服务记录管理

**目标**: 实现服务记录的创建、完成、查询

**代码量估算**: ~600行

#### 1. 分析 (Analysis)

**需求分析**:
- 创建服务记录（关联客户、设计方案）
- 记录服务日期和实际耗时
- 上传实际完成图
- 更新服务状态（pending → completed）
- 列出历史服务记录

#### 2. 设计 (Design)

**数据库模型**:
```python
class ServiceRecord(Base):
    __tablename__ = "service_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    customer_id = Column(Integer, ForeignKey("customers.id"))
    design_plan_id = Column(Integer, ForeignKey("design_plans.id"))
    service_date = Column(Date, nullable=False)
    service_duration = Column(Integer)  # 分钟
    actual_image_path = Column(String(500))
    notes = Column(Text)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
```

**API端点**:
- `POST /api/v1/services`: 创建服务记录
- `GET /api/v1/services`: 列出服务记录
- `GET /api/v1/services/{id}`: 获取服务详情
- `PUT /api/v1/services/{id}/complete`: 完成服务（上传实际图）
- `PUT /api/v1/services/{id}`: 更新服务记录

#### 3-6. 实现、测试、校对、Commit

**预期文件改动**:
- 新建: `app/models/service_record.py` (~60行)
- 新建: `app/schemas/service.py` (~120行)
- 新建: `app/services/service_record_service.py` (~180行)
- 新建: `app/api/v1/services.py` (~150行)
- 新建: `tests/test_services.py` (~140行)

**Commit节点**:
```bash
git commit -m "feat(backend): implement service record management

- Add ServiceRecord model
- Implement service CRUD operations
- Add service completion workflow
- Support actual image upload
- Create service_records table migration

Estimated lines: ~600
Status: ✅ All tests passing"
```

---

### Iteration 4.5: AI对比分析

**目标**: 实现设计图与实际图的AI对比分析

**代码量估算**: ~700行

#### 1. 分析 (Analysis)

**需求分析**:
- 当服务完成并上传实际图时，自动触发AI对比
- AI分析两张图片的相似度和差异
- 提取改进建议
- 保存对比结果
- 用于后续能力分析

#### 2. 设计 (Design)

**数据库模型**:
```python
class ComparisonResult(Base):
    __tablename__ = "comparison_results"

    id = Column(Integer, primary_key=True, index=True)
    service_record_id = Column(Integer, ForeignKey("service_records.id"), unique=True)
    similarity_score = Column(Integer)  # 0-100
    differences = Column(JSON)  # {"color": "...", "pattern": "..."}
    suggestions = Column(JSON)  # ["...", "..."]
    analyzed_at = Column(DateTime, default=datetime.utcnow)
```

**触发时机**:
- 服务状态变为completed时自动触发
- 也可以手动重新分析

**API端点**:
- `POST /api/v1/services/{id}/analyze`: 触发对比分析
- `GET /api/v1/services/{id}/comparison`: 获取对比结果

#### 3. 实现 (Implementation)

**核心逻辑**:
```python
# app/services/analysis_service.py
class AnalysisService:
    @staticmethod
    async def analyze_service(db: Session, service_id: int, user_id: int):
        # 1. 获取服务记录
        service = get_service_record(db, service_id, user_id)

        # 2. 验证有设计图和实际图
        if not service.design_plan or not service.actual_image_path:
            raise ValueError("Missing design or actual image")

        # 3. 调用AI对比
        ai_provider = AIProviderFactory.get_provider()
        comparison = await ai_provider.compare_images(
            design_image=service.design_plan.generated_image_path,
            actual_image=service.actual_image_path
        )

        # 4. 保存对比结果
        result = ComparisonResult(
            service_record_id=service_id,
            similarity_score=comparison["similarity_score"],
            differences=comparison["differences"],
            suggestions=comparison["suggestions"]
        )
        db.add(result)
        db.commit()

        # 5. 触发能力评分更新（下一个迭代）
        # await update_ability_scores(db, user_id, service_id, comparison)

        return result
```

**预期文件改动**:
- 新建: `app/models/comparison_result.py` (~50行)
- 新建: `app/schemas/analysis.py` (~100行)
- 新建: `app/services/analysis_service.py` (~200行)
- 修改: `app/api/v1/services.py` (+100行)
- 新建: `tests/test_analysis.py` (~150行)

**Commit节点**:
```bash
git commit -m "feat(backend): implement AI comparison analysis

- Add ComparisonResult model
- Implement AI-powered image comparison
- Add automatic analysis on service completion
- Extract similarity scores and differences
- Generate improvement suggestions
- Create comparison_results table migration

Estimated lines: ~700
Status: ✅ All tests passing (with AI mocks)"
```

---

### Iteration 4.6: 能力维度管理

**目标**: 实现能力维度定义和初始化

**代码量估算**: ~400行

#### 1. 分析 (Analysis)

**需求分析**:
- 预定义能力维度（颜色搭配、图案精度、细节处理等）
- 管理维度权重
- 支持自定义维度（Post-MVP）

**预定义维度**:
1. 颜色搭配 (Color Matching)
2. 图案精度 (Pattern Precision)
3. 细节处理 (Detail Work)
4. 整体构图 (Overall Composition)
5. 技法运用 (Technique Application)
6. 创意表达 (Creative Expression)

#### 2. 设计 (Design)

**数据库模型**:
```python
class AbilityDimension(Base):
    __tablename__ = "ability_dimensions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    weight = Column(Numeric(3, 2), default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)
```

**初始化数据**:
```python
INITIAL_DIMENSIONS = [
    {"name": "颜色搭配", "description": "色彩组合的协调性和创意", "weight": 1.0},
    {"name": "图案精度", "description": "图案绘制的精确度和细腻度", "weight": 1.0},
    {"name": "细节处理", "description": "细节的完整度和精致度", "weight": 1.0},
    {"name": "整体构图", "description": "设计的整体美感和平衡", "weight": 1.0},
    {"name": "技法运用", "description": "美甲技法的熟练度和多样性", "weight": 1.0},
    {"name": "创意表达", "description": "设计的创新性和独特性", "weight": 1.0},
]
```

**API端点**:
- `GET /api/v1/abilities/dimensions`: 列出所有维度
- `POST /api/v1/abilities/dimensions/init`: 初始化维度（仅管理员）

#### 3-6. 实现、测试、校对、Commit

**预期文件改动**:
- 新建: `app/models/ability_dimension.py` (~40行)
- 新建: `app/schemas/ability.py` (~80行)
- 新建: `app/services/ability_service.py` (~100行)
- 新建: `app/api/v1/abilities.py` (~80行)
- 新建: `alembic/versions/xxx_init_ability_dimensions.py` (数据迁移)
- 新建: `tests/test_abilities.py` (~100行)

**Commit节点**:
```bash
git commit -m "feat(backend): implement ability dimension system

- Add AbilityDimension model
- Define 6 core ability dimensions
- Add dimension initialization migration
- Add dimension listing API
- Create ability_dimensions table with initial data

Estimated lines: ~400
Status: ✅ All tests passing"
```

---

### Iteration 4.7: 能力分析与可视化数据

**目标**: 实现能力评分记录和统计分析

**代码量估算**: ~850行

#### 1. 分析 (Analysis)

**需求分析**:
- 从AI对比结果中提取能力评分
- 保存每次服务的能力评分
- 计算各维度的平均分
- 提供能力雷达图数据
- 识别擅长和待提升领域

**评分提取策略**:
- AI对比时要求返回各维度评分
- 修改`compare_images()`的响应格式，增加ability_scores

#### 2. 设计 (Design)

**数据库模型**:
```python
class AbilityRecord(Base):
    __tablename__ = "ability_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    service_record_id = Column(Integer, ForeignKey("service_records.id"))
    dimension_id = Column(Integer, ForeignKey("ability_dimensions.id"))
    score = Column(Integer)  # 0-100
    evidence = Column(JSON)  # 评分依据
    recorded_at = Column(DateTime, default=datetime.utcnow)
```

**API端点**:
- `GET /api/v1/abilities/stats`: 获取能力统计（雷达图数据）
- `GET /api/v1/abilities/history`: 获取能力成长曲线数据
- `GET /api/v1/abilities/summary`: 获取擅长/待提升总结

#### 3. 实现 (Implementation)

**核心逻辑**:
```python
# app/services/ability_service.py (续)
class AbilityService:
    @staticmethod
    async def record_abilities_from_comparison(
        db: Session,
        user_id: int,
        service_id: int,
        comparison_result: dict
    ):
        """从对比结果中提取并记录能力评分"""
        ability_scores = comparison_result.get("ability_scores", {})

        for dimension_name, score_data in ability_scores.items():
            dimension = get_dimension_by_name(db, dimension_name)
            if not dimension:
                continue

            record = AbilityRecord(
                user_id=user_id,
                service_record_id=service_id,
                dimension_id=dimension.id,
                score=score_data["score"],
                evidence=score_data.get("evidence", {})
            )
            db.add(record)

        db.commit()

    @staticmethod
    def get_ability_stats(db: Session, user_id: int) -> Dict:
        """获取能力雷达图数据"""
        dimensions = db.query(AbilityDimension).all()
        stats = {}

        for dim in dimensions:
            avg_score = db.query(func.avg(AbilityRecord.score))\
                .filter(
                    AbilityRecord.user_id == user_id,
                    AbilityRecord.dimension_id == dim.id
                )\
                .scalar()

            stats[dim.name] = {
                "score": round(avg_score or 0, 1),
                "count": get_record_count(db, user_id, dim.id)
            }

        return stats

    @staticmethod
    def get_ability_summary(db: Session, user_id: int) -> Dict:
        """获取擅长和待提升总结"""
        stats = AbilityService.get_ability_stats(db, user_id)

        sorted_by_score = sorted(stats.items(), key=lambda x: x[1]["score"], reverse=True)

        return {
            "strengths": sorted_by_score[:3],  # 前3名
            "improvements": sorted_by_score[-3:],  # 后3名
        }
```

**修改AI Provider**:
```python
# app/services/ai/openai_provider.py
async def compare_images(self, design_image: str, actual_image: str) -> Dict:
    """增强版对比分析，包含能力评分"""
    prompt = """
    Compare these two nail art images (design vs actual result).

    Provide analysis in JSON format:
    {
        "similarity_score": 0-100,
        "differences": {
            "color": "description",
            "pattern": "description",
            ...
        },
        "suggestions": ["...", "..."],
        "ability_scores": {
            "颜色搭配": {"score": 0-100, "evidence": "..."},
            "图案精度": {"score": 0-100, "evidence": "..."},
            "细节处理": {"score": 0-100, "evidence": "..."},
            "整体构图": {"score": 0-100, "evidence": "..."},
            "技法运用": {"score": 0-100, "evidence": "..."},
            "创意表达": {"score": 0-100, "evidence": "..."}
        }
    }
    """
    # ... AI调用
```

**预期文件改动**:
- 新建: `app/models/ability_record.py` (~50行)
- 修改: `app/schemas/ability.py` (+100行)
- 修改: `app/services/ability_service.py` (+300行)
- 修改: `app/services/analysis_service.py` (+50行，集成能力记录)
- 修改: `app/services/ai/openai_provider.py` (+50行，修改prompt)
- 修改: `app/api/v1/abilities.py` (+150行)
- 新建: `tests/test_ability_analysis.py` (~150行)

**Commit节点**:
```bash
git commit -m "feat(backend): implement ability tracking and analysis

- Add AbilityRecord model for tracking scores
- Extract ability scores from AI comparison
- Implement ability statistics calculation
- Add radar chart data endpoint
- Add ability growth history endpoint
- Add strengths/improvements summary
- Enhance AI comparison prompt with ability scoring
- Create ability_records table migration

Estimated lines: ~850
Status: ✅ All tests passing
📝 Stage 4 Complete: All Core Business Features Done"
```

**🎯 阶段4完成检查点**:
- [ ] 所有业务模块测试通过
- [ ] AI集成正常工作（Mock测试）
- [ ] 能力追踪逻辑正确
- [ ] API文档完整更新
- [ ] 数据库迁移全部完成

**💾 强烈建议在此进行Claude Compact**: 后端开发完成，上下文很长

---

## 阶段5: 前端开发 (Flutter Frontend)

**注意**: 前端开发每个迭代代码量较大，建议拆分更细或调整为1500行限制

### Iteration 5.1: Flutter项目基础架构

**目标**: 创建Flutter项目、配置依赖、搭建基础架构

**代码量估算**: ~800行

#### 1. 分析 (Analysis)

**需求分析**:
- 创建Flutter项目
- 配置所有依赖包
- 搭建目录结构
- 配置API服务基础
- 配置主题和路由

#### 2. 设计 (Design)

**目录结构**:
```
frontend/nail_app/
├── lib/
│   ├── config/
│   │   ├── api_config.dart
│   │   ├── app_config.dart
│   │   └── theme_config.dart
│   ├── models/
│   ├── services/
│   │   └── api_service.dart
│   ├── providers/
│   ├── screens/
│   │   └── splash_screen.dart
│   ├── widgets/
│   │   └── common/
│   ├── routes/
│   │   └── app_router.dart
│   ├── utils/
│   │   └── constants.dart
│   └── main.dart
├── test/
├── pubspec.yaml
└── analysis_options.yaml
```

#### 3. 实现 (Implementation)

**任务清单**:
- [ ] 创建Flutter项目:
  ```bash
  cd frontend
  flutter create nail_app
  cd nail_app
  ```
- [ ] 复制`pubspec_template.yaml`内容到`pubspec.yaml`
- [ ] 创建目录结构
- [ ] 实现`lib/config/api_config.dart`
- [ ] 实现`lib/config/theme_config.dart`
- [ ] 实现`lib/services/api_service.dart`（Dio配置）
- [ ] 实现`lib/routes/app_router.dart`
- [ ] 实现`lib/main.dart`
- [ ] 运行`flutter pub get`

#### 4-6. 测试、校对、Commit

**Commit节点**:
```bash
git add frontend/nail_app
git commit -m "feat(frontend): initialize Flutter project architecture

- Create Flutter project structure
- Configure dependencies (dio, provider, go_router, etc.)
- Setup API service with Dio interceptors
- Configure app theme and routing
- Add splash screen

Estimated lines: ~800
Status: ✅ App builds and runs"
```

---

### Iteration 5.2 - 5.6: 其他前端迭代

（后续前端迭代详细规划省略，每个迭代包括：认证界面、客户管理界面、设计生成界面、服务记录界面、能力中心界面）

每个迭代遵循相同的流程：分析 → 设计 → 实现 → 测试 → 校对 → Commit

---

## 总结与建议

### 开发节奏建议

1. **每日工作量**: 建议每天完成1-2个迭代
2. **Code Review**: 每完成一个阶段后进行代码审查
3. **测试优先**: 先写测试用例，再实现功能（TDD可选）
4. **小步快跑**: 每个commit保持小而聚焦

### Claude Compact时机

建议在以下时机执行Claude compact:
- ✅ 完成阶段1（框架层）后
- ✅ 完成阶段2（基础模块）后
- ✅ 完成阶段3（AI层）后
- ✅ 完成阶段4（业务模块）后
- ✅ 开始前端开发前

### 质量控制检查清单

每个迭代完成后检查:
- [ ] 所有测试通过（pytest -v）
- [ ] 代码格式化（black .）
- [ ] 代码检查（flake8）
- [ ] 类型检查（mypy app，可选）
- [ ] API文档更新
- [ ] Git commit信息清晰
- [ ] 没有遗留TODO或FIXME

### 风险管理

**高风险项**:
1. **AI API调用成本**: OpenAI API按调用收费，开发阶段使用Mock测试
2. **图片存储空间**: 注意磁盘空间，定期清理测试数据
3. **数据库迁移**: 每次迁移前备份数据

**缓解措施**:
- 开发阶段用Mock测试，减少AI调用
- 设置测试数据自动清理脚本
- 使用Alembic正确管理迁移

---

## 快速参考

### 常用命令

```bash
# 后端
cd backend
uvicorn app.main:app --reload          # 启动开发服务器
pytest -v                               # 运行测试
black .                                 # 格式化代码
alembic revision --autogenerate -m ""   # 创建迁移
alembic upgrade head                    # 应用迁移

# 前端
cd frontend/nail_app
flutter run                             # 运行应用
flutter test                            # 运行测试
flutter pub run build_runner build      # 生成代码

# Git
git status                              # 查看状态
git add .                               # 暂存改动
git commit -m "feat: description"       # 提交
git log --oneline                       # 查看历史
```

### Commit消息规范

```
feat(scope): 简短描述

- 详细改动1
- 详细改动2

Estimated lines: ~XXX
Status: ✅ Description
```

**类型**:
- `feat`: 新功能
- `fix`: Bug修复
- `refactor`: 重构
- `test`: 测试
- `docs`: 文档
- `chore`: 构建/工具

**Scope**:
- `backend`
- `frontend`
- `database`
- `ai`

---

## 附录：完整迭代列表

| 迭代ID | 名称 | 代码量 | 状态 |
|--------|------|--------|------|
| 1.1 | 数据库基础设施 | ~300行 | ⏳ |
| 1.2 | 认证与授权系统 | ~800行 | ⏳ |
| 1.3 | 文件上传服务 | ~400行 | ⏳ |
| 1.4 | 错误处理与日志 | ~350行 | ⏳ |
| 1.5 | API文档与健康检查 | ~200行 | ⏳ |
| 2.1 | 用户管理模块 | ~500行 | ⏳ |
| 2.2 | 客户档案管理 | ~600行 | ⏳ |
| 2.3 | 客户详细档案 | ~700行 | ⏳ |
| 3.1 | AI Provider抽象接口 | ~400行 | ⏳ |
| 3.2 | OpenAI Provider实现 | ~900行 | ⏳ |
| 4.1 | 灵感图库管理 | ~550行 | ⏳ |
| 4.2 | AI设计方案生成 | ~800行 | ⏳ |
| 4.3 | 设计方案微调 | ~500行 | ⏳ |
| 4.4 | 服务记录管理 | ~600行 | ⏳ |
| 4.5 | AI对比分析 | ~700行 | ⏳ |
| 4.6 | 能力维度管理 | ~400行 | ⏳ |
| 4.7 | 能力分析与可视化 | ~850行 | ⏳ |
| 5.1 | Flutter基础架构 | ~800行 | ⏳ |
| 5.2 | 认证与用户模块 | ~900行 | ⏳ |
| 5.3 | 客户管理界面 | ~950行 | ⏳ |
| 5.4 | 设计生成界面 | ~1000行 | ⏳ |
| 5.5 | 服务记录界面 | ~900行 | ⏳ |
| 5.6 | 能力中心界面 | ~950行 | ⏳ |

**总计**: 23个迭代，约15,000行代码

---

**文档版本**: v1.0
**创建日期**: 2024-01-08
**最后更新**: 2024-01-08
