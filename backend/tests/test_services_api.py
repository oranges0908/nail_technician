"""
服务记录 API 测试 (P1)
覆盖: /api/v1/services — CRUD、完成服务、列表过滤、删除
"""
from unittest.mock import patch

from tests.conftest import _mock_ai_provider


class TestCreateServiceRecord:
    """创建服务记录"""

    def test_create_service_record_success(
        self, client, auth_headers, test_customer, test_design
    ):
        """正常创建服务记录返回 201"""
        response = client.post(
            "/api/v1/services/",
            json={
                "customer_id": test_customer["id"],
                "design_plan_id": test_design["id"],
                "service_date": "2025-01-15",
                "notes": "测试服务",
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["customer_id"] == test_customer["id"]
        assert data["design_plan_id"] == test_design["id"]
        assert data["status"] == "pending"

    def test_create_without_design(self, client, auth_headers, test_customer):
        """不关联设计方案也能创建服务记录"""
        response = client.post(
            "/api/v1/services/",
            json={
                "customer_id": test_customer["id"],
                "service_date": "2025-01-15",
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        assert response.json()["design_plan_id"] is None

    def test_create_invalid_customer(self, client, auth_headers):
        """关联不存在的客户返回 400"""
        response = client.post(
            "/api/v1/services/",
            json={
                "customer_id": 99999,
                "service_date": "2025-01-15",
            },
            headers=auth_headers,
        )
        assert response.status_code == 400


class TestGetServiceRecord:
    """获取服务记录详情"""

    def test_get_service_record_success(
        self, client, auth_headers, test_service_record
    ):
        """获取服务记录详情成功"""
        sid = test_service_record["id"]
        response = client.get(
            f"/api/v1/services/{sid}", headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["id"] == sid

    def test_get_nonexistent(self, client, auth_headers):
        """不存在的服务记录返回 404"""
        response = client.get(
            "/api/v1/services/99999", headers=auth_headers
        )
        assert response.status_code == 404


class TestListServiceRecords:
    """服务记录列表"""

    def test_list_empty(self, client, auth_headers):
        """无服务记录时返回空列表"""
        response = client.get("/api/v1/services/", headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == []

    def test_list_with_records(self, client, auth_headers, test_service_record):
        """有服务记录时返回列表"""
        response = client.get("/api/v1/services/", headers=auth_headers)
        data = response.json()
        assert len(data) >= 1

    def test_list_filter_by_customer(
        self, client, auth_headers, test_service_record, test_customer
    ):
        """按客户ID过滤"""
        response = client.get(
            f"/api/v1/services/?customer_id={test_customer['id']}",
            headers=auth_headers,
        )
        data = response.json()
        assert len(data) >= 1
        assert all(r["customer_id"] == test_customer["id"] for r in data)


class TestUpdateServiceRecord:
    """更新服务记录"""

    def test_update_success(self, client, auth_headers, test_service_record):
        """更新服务记录成功"""
        sid = test_service_record["id"]
        response = client.put(
            f"/api/v1/services/{sid}",
            json={"notes": "更新后的备注", "service_duration": 90},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["notes"] == "更新后的备注"
        assert data["service_duration"] == 90


class TestCompleteServiceRecord:
    """完成服务记录"""

    @patch("app.services.ai.factory.AIProviderFactory.get_provider")
    def test_complete_success(
        self, mock_get_provider, client, auth_headers, test_service_record
    ):
        """完成服务记录成功"""
        mock_get_provider.return_value = _mock_ai_provider()
        sid = test_service_record["id"]

        response = client.put(
            f"/api/v1/services/{sid}/complete",
            json={
                "actual_image_path": "/uploads/actuals/result.jpg",
                "service_duration": 75,
                "artist_review": "整体完成度高",
                "customer_satisfaction": 5,
            },
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["actual_image_path"] == "/uploads/actuals/result.jpg"
        assert data["service_duration"] == 75


class TestDeleteServiceRecord:
    """删除服务记录"""

    def test_delete_success(self, client, auth_headers, test_service_record):
        """删除服务记录返回 204"""
        sid = test_service_record["id"]
        response = client.delete(
            f"/api/v1/services/{sid}", headers=auth_headers
        )
        assert response.status_code == 204

        # 确认已删除
        response = client.get(
            f"/api/v1/services/{sid}", headers=auth_headers
        )
        assert response.status_code == 404

    def test_delete_nonexistent(self, client, auth_headers):
        """删除不存在的服务记录返回 400"""
        response = client.delete(
            "/api/v1/services/99999", headers=auth_headers
        )
        assert response.status_code == 400
