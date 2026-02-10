"""
设计方案 API 测试 (P0)
覆盖: /api/v1/designs — 生成(mock AI)、优化、列表、版本历史、归档、删除
"""
from unittest.mock import AsyncMock, patch


# Mock AI Provider 返回值
MOCK_GENERATED_IMAGE = "https://example.com/generated_design.png"
MOCK_ESTIMATION = {
    "estimated_duration": 60,
    "difficulty_level": "中等",
    "materials": ["基础底胶", "彩色甲油", "亮片"],
    "techniques": ["渐变", "彩绘"]
}


def _mock_ai_provider():
    """创建 mock AI provider 实例"""
    mock_provider = AsyncMock()
    mock_provider.generate_design.return_value = MOCK_GENERATED_IMAGE
    mock_provider.refine_design.return_value = "https://example.com/refined_design.png"
    mock_provider.estimate_execution.return_value = MOCK_ESTIMATION
    return mock_provider


class TestGenerateDesign:
    """生成设计方案（mock AI）"""

    @patch("app.services.ai.factory.AIProviderFactory.get_provider")
    def test_generate_design_success(self, mock_get_provider, client, auth_headers):
        """正常生成设计返回 201"""
        mock_get_provider.return_value = _mock_ai_provider()

        response = client.post(
            "/api/v1/designs/generate",
            json={
                "prompt": "优雅粉色渐变美甲，带金色亮片装饰",
                "design_target": "10nails",
                "title": "粉色渐变",
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["ai_prompt"] == "优雅粉色渐变美甲，带金色亮片装饰"
        assert data["generated_image_path"] == MOCK_GENERATED_IMAGE
        assert data["version"] == 1
        assert data["estimated_duration"] == 60
        assert data["difficulty_level"] == "中等"

    @patch("app.services.ai.factory.AIProviderFactory.get_provider")
    def test_generate_design_with_customer(
        self, mock_get_provider, client, auth_headers, test_customer
    ):
        """关联客户的设计生成"""
        mock_get_provider.return_value = _mock_ai_provider()

        response = client.post(
            "/api/v1/designs/generate",
            json={
                "prompt": "简约法式美甲",
                "customer_id": test_customer["id"],
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        assert response.json()["customer_id"] == test_customer["id"]

    @patch("app.services.ai.factory.AIProviderFactory.get_provider")
    def test_generate_design_invalid_customer(
        self, mock_get_provider, client, auth_headers
    ):
        """关联不存在的客户返回 404"""
        mock_get_provider.return_value = _mock_ai_provider()

        response = client.post(
            "/api/v1/designs/generate",
            json={
                "prompt": "简约法式美甲",
                "customer_id": 99999,
            },
            headers=auth_headers,
        )
        assert response.status_code == 404


def _create_design(client, auth_headers, title="测试设计"):
    """辅助：创建一个设计并返回响应 JSON"""
    with patch("app.services.ai.factory.AIProviderFactory.get_provider") as mock:
        mock.return_value = _mock_ai_provider()
        response = client.post(
            "/api/v1/designs/generate",
            json={"prompt": "测试提示词", "title": title},
            headers=auth_headers,
        )
        assert response.status_code == 201
        return response.json()


class TestRefineDesign:
    """优化设计方案"""

    @patch("app.services.ai.factory.AIProviderFactory.get_provider")
    def test_refine_design_success(self, mock_get_provider, client, auth_headers):
        """优化设计返回新版本"""
        design = _create_design(client, auth_headers)
        mock_get_provider.return_value = _mock_ai_provider()

        response = client.post(
            f"/api/v1/designs/{design['id']}/refine",
            json={"refinement_instruction": "增加更多亮片"},
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["version"] == 2
        assert data["parent_design_id"] == design["id"]
        assert data["refinement_instruction"] == "增加更多亮片"

    @patch("app.services.ai.factory.AIProviderFactory.get_provider")
    def test_refine_nonexistent_design(self, mock_get_provider, client, auth_headers):
        """优化不存在的设计返回 404"""
        mock_get_provider.return_value = _mock_ai_provider()

        response = client.post(
            "/api/v1/designs/99999/refine",
            json={"refinement_instruction": "增加亮片"},
            headers=auth_headers,
        )
        assert response.status_code == 404


class TestListDesigns:
    """设计列表"""

    def test_list_empty(self, client, auth_headers):
        """无设计时返回空列表"""
        response = client.get("/api/v1/designs/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["designs"] == []

    def test_list_with_designs(self, client, auth_headers):
        """有设计时返回列表"""
        _create_design(client, auth_headers, "设计A")
        _create_design(client, auth_headers, "设计B")

        response = client.get("/api/v1/designs/", headers=auth_headers)
        data = response.json()
        assert data["total"] == 2
        assert len(data["designs"]) == 2

    def test_list_search(self, client, auth_headers):
        """搜索过滤"""
        _create_design(client, auth_headers, "粉色渐变设计")
        _create_design(client, auth_headers, "蓝色法式")

        response = client.get(
            "/api/v1/designs/?search=粉色",
            headers=auth_headers,
        )
        data = response.json()
        assert data["total"] == 1


class TestDesignVersions:
    """设计版本历史"""

    @patch("app.services.ai.factory.AIProviderFactory.get_provider")
    def test_get_versions(self, mock_get_provider, client, auth_headers):
        """获取版本历史"""
        # 创建原始设计
        design = _create_design(client, auth_headers)
        mock_get_provider.return_value = _mock_ai_provider()

        # 创建优化版本
        client.post(
            f"/api/v1/designs/{design['id']}/refine",
            json={"refinement_instruction": "第一次优化"},
            headers=auth_headers,
        )

        # 获取版本历史
        response = client.get(
            f"/api/v1/designs/{design['id']}/versions",
            headers=auth_headers,
        )
        assert response.status_code == 200
        versions = response.json()
        assert len(versions) == 2
        assert versions[0]["version"] == 1
        assert versions[1]["version"] == 2


class TestArchiveDesign:
    """归档设计"""

    def test_archive_design_success(self, client, auth_headers):
        """归档设计成功"""
        design = _create_design(client, auth_headers)

        response = client.put(
            f"/api/v1/designs/{design['id']}/archive",
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["is_archived"] == 1

    def test_archive_nonexistent(self, client, auth_headers):
        """归档不存在的设计返回 404"""
        response = client.put(
            "/api/v1/designs/99999/archive",
            headers=auth_headers,
        )
        assert response.status_code == 404


class TestDeleteDesign:
    """删除设计"""

    def test_delete_design_success(self, client, auth_headers):
        """删除设计成功返回 204"""
        design = _create_design(client, auth_headers)

        response = client.delete(
            f"/api/v1/designs/{design['id']}",
            headers=auth_headers,
        )
        assert response.status_code == 204

        # 确认已删除
        response = client.get(
            f"/api/v1/designs/{design['id']}",
            headers=auth_headers,
        )
        assert response.status_code == 404

    def test_delete_nonexistent(self, client, auth_headers):
        """删除不存在的设计返回 404"""
        response = client.delete(
            "/api/v1/designs/99999",
            headers=auth_headers,
        )
        assert response.status_code == 404
