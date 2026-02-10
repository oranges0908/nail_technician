"""
用户管理 API 测试 (P2)
覆盖: /api/v1/users — 获取当前用户、更新信息、修改密码、删除账号
"""


class TestGetCurrentUser:
    """获取当前用户信息"""

    def test_get_me_success(self, client, auth_headers):
        """获取当前用户信息成功"""
        response = client.get("/api/v1/users/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["username"] == "testuser"
        assert data["is_active"] is True
        assert "hashed_password" not in data

    def test_get_me_no_auth(self, client):
        """无认证返回 401"""
        response = client.get("/api/v1/users/me")
        assert response.status_code == 401


class TestUpdateCurrentUser:
    """更新当前用户信息"""

    def test_update_username(self, client, auth_headers):
        """更新用户名成功"""
        response = client.put(
            "/api/v1/users/me",
            json={"username": "newusername"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["username"] == "newusername"

    def test_update_email_conflict(self, client, auth_headers, second_auth_headers):
        """更新邮箱时邮箱冲突返回 409"""
        response = client.put(
            "/api/v1/users/me",
            json={"email": "second@example.com"},
            headers=auth_headers,
        )
        assert response.status_code == 409


class TestChangePassword:
    """修改密码"""

    def test_change_password_success(self, client, auth_headers, test_user_data):
        """修改密码成功"""
        response = client.put(
            "/api/v1/users/me/password",
            json={
                "old_password": test_user_data["password"],
                "new_password": "newpassword123",
            },
            headers=auth_headers,
        )
        assert response.status_code == 200

        # 验证新密码可以登录
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user_data["email"],
                "password": "newpassword123",
            },
        )
        assert response.status_code == 200

    def test_change_password_wrong_old(self, client, auth_headers):
        """旧密码错误返回 400"""
        response = client.put(
            "/api/v1/users/me/password",
            json={
                "old_password": "wrongpassword",
                "new_password": "newpassword123",
            },
            headers=auth_headers,
        )
        assert response.status_code == 400


class TestDeleteCurrentUser:
    """删除当前用户"""

    def test_delete_me_success(self, client, auth_headers):
        """删除当前用户成功（软删除）"""
        response = client.delete(
            "/api/v1/users/me", headers=auth_headers
        )
        assert response.status_code == 204
