"""
认证 API 测试 (P0)
覆盖: /api/v1/auth — 注册、登录、token 刷新、无 token 访问
"""


class TestRegister:
    """用户注册测试"""

    def test_register_success(self, client):
        """正常注册返回 201 和用户信息"""
        response = client.post("/api/v1/auth/register", json={
            "email": "new@example.com",
            "username": "newuser",
            "password": "password123"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "new@example.com"
        assert data["username"] == "newuser"
        assert data["is_active"] is True
        assert "hashed_password" not in data

    def test_register_duplicate_email(self, client, registered_user):
        """重复邮箱返回 409"""
        response = client.post("/api/v1/auth/register", json={
            "email": "test@example.com",  # 与 registered_user 相同
            "username": "differentuser",
            "password": "password123"
        })
        assert response.status_code == 409

    def test_register_duplicate_username(self, client, registered_user):
        """重复用户名返回 409"""
        response = client.post("/api/v1/auth/register", json={
            "email": "different@example.com",
            "username": "testuser",  # 与 registered_user 相同
            "password": "password123"
        })
        assert response.status_code == 409

    def test_register_short_password(self, client):
        """密码太短返回 422"""
        response = client.post("/api/v1/auth/register", json={
            "email": "short@example.com",
            "username": "shortpw",
            "password": "123"
        })
        assert response.status_code == 422


class TestLogin:
    """用户登录测试"""

    def test_login_with_email(self, client, test_user_data, registered_user):
        """使用邮箱登录成功"""
        response = client.post("/api/v1/auth/login", data={
            "username": test_user_data["email"],
            "password": test_user_data["password"],
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_with_username(self, client, test_user_data, registered_user):
        """使用用户名登录成功"""
        response = client.post("/api/v1/auth/login", data={
            "username": test_user_data["username"],
            "password": test_user_data["password"],
        })
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_login_wrong_password(self, client, test_user_data, registered_user):
        """错误密码返回 401"""
        response = client.post("/api/v1/auth/login", data={
            "username": test_user_data["email"],
            "password": "wrongpassword",
        })
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        """不存在的用户返回 401"""
        response = client.post("/api/v1/auth/login", data={
            "username": "nobody@example.com",
            "password": "whatever",
        })
        assert response.status_code == 401


class TestTokenRefresh:
    """Token 刷新测试"""

    def test_refresh_token_success(self, client, auth_tokens):
        """使用 refresh_token 获取新的 access_token"""
        response = client.post("/api/v1/auth/refresh", json={
            "refresh_token": auth_tokens["refresh_token"]
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_refresh_with_invalid_token(self, client):
        """无效 refresh_token 返回 401"""
        response = client.post("/api/v1/auth/refresh", json={
            "refresh_token": "invalid.token.here"
        })
        assert response.status_code == 401

    def test_refresh_with_access_token(self, client, auth_tokens):
        """用 access_token 当 refresh_token 返回 401"""
        response = client.post("/api/v1/auth/refresh", json={
            "refresh_token": auth_tokens["access_token"]
        })
        assert response.status_code == 401


class TestProtectedRoute:
    """受保护路由访问测试"""

    def test_no_token_returns_401(self, client):
        """无 token 访问受保护路由返回 401"""
        response = client.get("/api/v1/customers/")
        assert response.status_code == 401

    def test_invalid_token_returns_401(self, client):
        """无效 token 返回 401"""
        response = client.get(
            "/api/v1/customers/",
            headers={"Authorization": "Bearer invalid.token"}
        )
        assert response.status_code == 401
