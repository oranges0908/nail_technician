# API 文档

## 基础信息

- 基础 URL: `http://localhost:8000/api/v1`
- 认证方式: JWT Bearer Token

## 认证接口

### 用户登录

```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=your_password
```

响应:
```json
{
  "access_token": "eyJ0eXAi...",
  "token_type": "bearer",
  "refresh_token": "eyJ0eXAi..."
}
```

### 用户注册

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "username",
  "password": "password123"
}
```

### 刷新令牌

```http
POST /api/v1/auth/refresh
Authorization: Bearer {refresh_token}
```

## 用户接口

### 获取用户列表

```http
GET /api/v1/users?skip=0&limit=100
Authorization: Bearer {access_token}
```

### 获取用户详情

```http
GET /api/v1/users/{user_id}
Authorization: Bearer {access_token}
```

### 创建用户

```http
POST /api/v1/users
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "email": "newuser@example.com",
  "username": "newuser",
  "password": "password123"
}
```

### 更新用户

```http
PUT /api/v1/users/{user_id}
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "username": "updated_username"
}
```

### 删除用户

```http
DELETE /api/v1/users/{user_id}
Authorization: Bearer {access_token}
```

## 健康检查

### 服务健康检查

```http
GET /health
```

### API 健康检查

```http
GET /api/v1/health
```

### 数据库健康检查

```http
GET /api/v1/health/db
```

## 错误响应

所有错误响应格式:

```json
{
  "detail": "错误描述信息"
}
```

常见状态码:
- 200: 成功
- 201: 创建成功
- 204: 删除成功（无内容）
- 400: 请求参数错误
- 401: 未授权
- 403: 禁止访问
- 404: 资源不存在
- 500: 服务器内部错误
- 501: 功能未实现
