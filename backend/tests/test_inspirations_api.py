"""
灵感图库 API 测试 (P1)
覆盖: /api/v1/inspirations — CRUD、分类过滤、搜索、热门/最近、使用标记、数据隔离
"""


class TestCreateInspiration:
    """创建灵感图"""

    def test_create_inspiration_success(self, client, auth_headers):
        """正常创建灵感图返回 201"""
        response = client.post(
            "/api/v1/inspirations/",
            json={
                "image_path": "/uploads/inspirations/test.jpg",
                "title": "法式美甲灵感",
                "description": "优雅的法式美甲参考图",
                "tags": ["法式", "优雅"],
                "category": "法式",
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "法式美甲灵感"
        assert data["category"] == "法式"
        assert data["tags"] == ["法式", "优雅"]
        assert data["usage_count"] == 0

    def test_create_inspiration_minimal(self, client, auth_headers):
        """只提供必填字段（image_path）也能创建"""
        response = client.post(
            "/api/v1/inspirations/",
            json={"image_path": "/uploads/inspirations/minimal.jpg"},
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["image_path"] == "/uploads/inspirations/minimal.jpg"
        assert data["title"] is None


class TestListInspirations:
    """灵感图列表"""

    def test_list_empty(self, client, auth_headers):
        """无灵感图时返回空列表"""
        response = client.get("/api/v1/inspirations/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["inspirations"] == []

    def test_list_with_items(self, client, auth_headers, test_inspiration):
        """有灵感图时返回列表"""
        response = client.get("/api/v1/inspirations/", headers=auth_headers)
        data = response.json()
        assert data["total"] >= 1

    def test_list_search(self, client, auth_headers):
        """搜索过滤（按标题）"""
        client.post(
            "/api/v1/inspirations/",
            json={"image_path": "/a.jpg", "title": "粉色渐变灵感"},
            headers=auth_headers,
        )
        client.post(
            "/api/v1/inspirations/",
            json={"image_path": "/b.jpg", "title": "蓝色法式灵感"},
            headers=auth_headers,
        )

        response = client.get(
            "/api/v1/inspirations/?search=粉色", headers=auth_headers
        )
        data = response.json()
        assert data["total"] == 1

    def test_list_category_filter(self, client, auth_headers):
        """分类过滤"""
        client.post(
            "/api/v1/inspirations/",
            json={"image_path": "/a.jpg", "category": "法式"},
            headers=auth_headers,
        )
        client.post(
            "/api/v1/inspirations/",
            json={"image_path": "/b.jpg", "category": "渐变"},
            headers=auth_headers,
        )

        response = client.get(
            "/api/v1/inspirations/?category=法式", headers=auth_headers
        )
        data = response.json()
        assert data["total"] == 1


class TestGetInspiration:
    """获取灵感图详情"""

    def test_get_inspiration_success(self, client, auth_headers, test_inspiration):
        """获取灵感图详情成功"""
        iid = test_inspiration["id"]
        response = client.get(
            f"/api/v1/inspirations/{iid}", headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["title"] == "测试灵感图"

    def test_get_nonexistent(self, client, auth_headers):
        """不存在的灵感图返回 404"""
        response = client.get(
            "/api/v1/inspirations/99999", headers=auth_headers
        )
        assert response.status_code == 404


class TestUpdateInspiration:
    """更新灵感图"""

    def test_update_success(self, client, auth_headers, test_inspiration):
        """更新灵感图成功"""
        iid = test_inspiration["id"]
        response = client.put(
            f"/api/v1/inspirations/{iid}",
            json={"title": "更新后的标题", "category": "法式"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "更新后的标题"
        assert data["category"] == "法式"

    def test_update_nonexistent(self, client, auth_headers):
        """更新不存在的灵感图返回 404"""
        response = client.put(
            "/api/v1/inspirations/99999",
            json={"title": "不存在"},
            headers=auth_headers,
        )
        assert response.status_code == 404


class TestDeleteInspiration:
    """删除灵感图"""

    def test_delete_success(self, client, auth_headers, test_inspiration):
        """删除灵感图返回 204"""
        iid = test_inspiration["id"]
        response = client.delete(
            f"/api/v1/inspirations/{iid}", headers=auth_headers
        )
        assert response.status_code == 204

        # 确认已删除
        response = client.get(
            f"/api/v1/inspirations/{iid}", headers=auth_headers
        )
        assert response.status_code == 404

    def test_delete_nonexistent(self, client, auth_headers):
        """删除不存在的灵感图返回 404"""
        response = client.delete(
            "/api/v1/inspirations/99999", headers=auth_headers
        )
        assert response.status_code == 404


class TestUseInspiration:
    """使用标记"""

    def test_use_increments_count(self, client, auth_headers, test_inspiration):
        """标记使用后 usage_count +1"""
        iid = test_inspiration["id"]
        assert test_inspiration["usage_count"] == 0

        response = client.post(
            f"/api/v1/inspirations/{iid}/use", headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["usage_count"] == 1

        # 再次使用
        response = client.post(
            f"/api/v1/inspirations/{iid}/use", headers=auth_headers
        )
        assert response.json()["usage_count"] == 2

    def test_use_nonexistent(self, client, auth_headers):
        """使用不存在的灵感图返回 404"""
        response = client.post(
            "/api/v1/inspirations/99999/use", headers=auth_headers
        )
        assert response.status_code == 404


class TestPopularAndRecent:
    """热门和最近灵感图"""

    def test_popular_empty(self, client, auth_headers):
        """无灵感图时热门返回空列表"""
        response = client.get(
            "/api/v1/inspirations/popular", headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json() == []

    def test_recent_empty(self, client, auth_headers):
        """无灵感图时最近返回空列表"""
        response = client.get(
            "/api/v1/inspirations/recent", headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json() == []

    def test_popular_returns_items(self, client, auth_headers, test_inspiration):
        """有灵感图时热门返回数据"""
        response = client.get(
            "/api/v1/inspirations/popular", headers=auth_headers
        )
        assert response.status_code == 200
        assert len(response.json()) >= 1


class TestInspirationDataIsolation:
    """数据隔离"""

    def test_data_isolation(
        self, client, auth_headers, second_auth_headers, test_inspiration
    ):
        """第二用户看不到第一用户的灵感图"""
        response = client.get(
            "/api/v1/inspirations/", headers=second_auth_headers
        )
        data = response.json()
        assert data["total"] == 0

    def test_cannot_access_other_user_inspiration(
        self, client, auth_headers, second_auth_headers, test_inspiration
    ):
        """第二用户直接访问第一用户的灵感图返回 404"""
        iid = test_inspiration["id"]
        response = client.get(
            f"/api/v1/inspirations/{iid}", headers=second_auth_headers
        )
        assert response.status_code == 404
