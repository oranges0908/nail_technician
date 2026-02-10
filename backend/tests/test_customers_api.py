"""
客户管理 API 测试 (P0)
覆盖: /api/v1/customers — CRUD、分页、搜索、数据隔离
"""


class TestCreateCustomer:
    """创建客户"""

    def test_create_customer_success(self, client, auth_headers):
        """正常创建客户返回 201"""
        response = client.post(
            "/api/v1/customers/",
            json={"name": "张三", "phone": "13900001111"},
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "张三"
        assert data["phone"] == "13900001111"
        assert data["is_active"] is True

    def test_create_customer_with_optional_fields(self, client, auth_headers):
        """创建客户时带可选字段"""
        response = client.post(
            "/api/v1/customers/",
            json={
                "name": "李四",
                "phone": "13900002222",
                "email": "lisi@example.com",
                "notes": "VIP客户"
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "lisi@example.com"
        assert data["notes"] == "VIP客户"

    def test_create_customer_duplicate_phone(self, client, auth_headers, test_customer):
        """重复手机号报错"""
        response = client.post(
            "/api/v1/customers/",
            json={"name": "另一个客户", "phone": test_customer["phone"]},
            headers=auth_headers,
        )
        # 服务层应该抛出冲突错误
        assert response.status_code in (409, 500)


class TestListCustomers:
    """获取客户列表"""

    def test_list_empty(self, client, auth_headers):
        """无客户时返回空列表"""
        response = client.get("/api/v1/customers/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["customers"] == []

    def test_list_with_customers(self, client, auth_headers, test_customer):
        """有客户时返回列表"""
        response = client.get("/api/v1/customers/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert len(data["customers"]) >= 1

    def test_list_pagination(self, client, auth_headers):
        """分页参数生效"""
        # 创建 3 个客户
        for i in range(3):
            client.post(
                "/api/v1/customers/",
                json={"name": f"客户{i}", "phone": f"1390000{i:04d}"},
                headers=auth_headers,
            )

        # 第一页，每页 2 条
        response = client.get(
            "/api/v1/customers/?skip=0&limit=2",
            headers=auth_headers,
        )
        data = response.json()
        assert data["total"] == 3
        assert len(data["customers"]) == 2

        # 第二页
        response = client.get(
            "/api/v1/customers/?skip=2&limit=2",
            headers=auth_headers,
        )
        data = response.json()
        assert len(data["customers"]) == 1


class TestGetCustomer:
    """获取客户详情"""

    def test_get_customer_success(self, client, auth_headers, test_customer):
        """获取客户详情成功"""
        cid = test_customer["id"]
        response = client.get(
            f"/api/v1/customers/{cid}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["name"] == test_customer["name"]

    def test_get_nonexistent_customer(self, client, auth_headers):
        """不存在的客户返回 404"""
        response = client.get(
            "/api/v1/customers/99999",
            headers=auth_headers,
        )
        assert response.status_code == 404


class TestUpdateCustomer:
    """更新客户"""

    def test_update_customer_success(self, client, auth_headers, test_customer):
        """更新客户信息成功"""
        cid = test_customer["id"]
        response = client.put(
            f"/api/v1/customers/{cid}",
            json={"name": "改名客户", "notes": "新备注"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "改名客户"
        assert data["notes"] == "新备注"

    def test_update_nonexistent_customer(self, client, auth_headers):
        """更新不存在的客户返回 404"""
        response = client.put(
            "/api/v1/customers/99999",
            json={"name": "不存在"},
            headers=auth_headers,
        )
        assert response.status_code == 404


class TestDeleteCustomer:
    """删除客户（软删除）"""

    def test_delete_customer_success(self, client, auth_headers, test_customer):
        """删除客户返回 204"""
        cid = test_customer["id"]
        response = client.delete(
            f"/api/v1/customers/{cid}",
            headers=auth_headers,
        )
        assert response.status_code == 204

    def test_delete_nonexistent_customer(self, client, auth_headers):
        """删除不存在的客户返回 404"""
        response = client.delete(
            "/api/v1/customers/99999",
            headers=auth_headers,
        )
        assert response.status_code == 404


class TestSearchCustomers:
    """搜索客户"""

    def test_search_by_name(self, client, auth_headers):
        """按姓名搜索"""
        client.post(
            "/api/v1/customers/",
            json={"name": "王小明", "phone": "13700001111"},
            headers=auth_headers,
        )
        client.post(
            "/api/v1/customers/",
            json={"name": "张大力", "phone": "13700002222"},
            headers=auth_headers,
        )

        response = client.get(
            "/api/v1/customers/?search=王小",
            headers=auth_headers,
        )
        data = response.json()
        assert data["total"] == 1
        assert data["customers"][0]["name"] == "王小明"


class TestCustomerDataIsolation:
    """数据隔离：不同用户看不到对方客户"""

    def test_data_isolation(self, client, auth_headers, second_auth_headers, test_customer):
        """第二用户看不到第一用户的客户"""
        # 第二用户获取列表
        response = client.get(
            "/api/v1/customers/",
            headers=second_auth_headers,
        )
        data = response.json()
        assert data["total"] == 0

    def test_cannot_access_other_user_customer(
        self, client, auth_headers, second_auth_headers, test_customer
    ):
        """第二用户直接访问第一用户的客户 ID 返回 404"""
        cid = test_customer["id"]
        response = client.get(
            f"/api/v1/customers/{cid}",
            headers=second_auth_headers,
        )
        assert response.status_code == 404
