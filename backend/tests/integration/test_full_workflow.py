"""
端到端集成测试 — 覆盖完整业务链路

测试场景：
1. 完整服务工作流：注册→登录→客户→设计→服务→完成→分析→能力
2. 多用户数据隔离
3. 设计迭代（优化 + 版本历史）
4. 服务记录过滤与分页
5. 错误处理与权限校验
"""
import pytest


# ================================================================
# Helpers
# ================================================================

def register_and_login(client, email, username, password):
    """注册用户并登录，返回 auth headers"""
    client.post("/api/v1/auth/register", json={
        "email": email,
        "username": username,
        "password": password,
    })
    resp = client.post("/api/v1/auth/login", data={
        "username": email,
        "password": password,
    })
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def create_customer(client, headers, name="测试客户", phone="13800138000"):
    """创建客户，返回响应 JSON"""
    resp = client.post("/api/v1/customers/", json={
        "name": name,
        "phone": phone,
    }, headers=headers)
    assert resp.status_code == 201
    return resp.json()


def generate_design(client, headers, prompt="粉色渐变法式美甲", title="测试设计"):
    """生成设计方案（需 mock_ai fixture），返回响应 JSON"""
    resp = client.post("/api/v1/designs/generate", json={
        "prompt": prompt,
        "title": title,
    }, headers=headers)
    assert resp.status_code == 201
    return resp.json()


def create_service_record(client, headers, customer_id, design_plan_id=None, date="2025-01-15"):
    """创建服务记录，返回响应 JSON"""
    payload = {
        "customer_id": customer_id,
        "service_date": date,
    }
    if design_plan_id:
        payload["design_plan_id"] = design_plan_id
    resp = client.post("/api/v1/services/", json=payload, headers=headers)
    assert resp.status_code == 201
    return resp.json()


# ================================================================
# 测试 1：完整服务工作流
# ================================================================

class TestFullServiceWorkflow:
    """端到端：注册 → 登录 → 客户 → 设计 → 服务 → 完成 → AI分析 → 能力查询"""

    def test_complete_workflow(self, client, mock_ai):
        # 1. 注册 + 登录
        headers = register_and_login(client, "artist@nail.com", "artist1", "password123")

        # 验证用户信息
        me = client.get("/api/v1/users/me", headers=headers)
        assert me.status_code == 200
        assert me.json()["email"] == "artist@nail.com"

        # 2. 创建客户
        customer = create_customer(client, headers, "张小姐", "13900139000")
        assert customer["name"] == "张小姐"
        customer_id = customer["id"]

        # 3. 生成设计方案（mock AI）
        design = generate_design(client, headers, "粉色渐变法式美甲搭配亮片装饰", "法式渐变")
        assert design["title"] == "法式渐变"
        assert design["generated_image_path"] is not None
        assert design["estimated_duration"] == 60
        assert design["difficulty_level"] == "中等"
        design_id = design["id"]

        # 4. 创建服务记录（关联客户和设计）
        service = create_service_record(client, headers, customer_id, design_id)
        assert service["status"] == "pending"
        assert service["customer_id"] == customer_id
        assert service["design_plan_id"] == design_id
        service_id = service["id"]

        # 5. 完成服务（上传实际效果图 + 复盘 + 反馈）
        complete_resp = client.put(f"/api/v1/services/{service_id}/complete", json={
            "actual_image_path": "/uploads/actuals/result_001.jpg",
            "service_duration": 75,
            "materials_used": "基础底胶, 彩色甲油, 亮片",
            "artist_review": "整体完成不错，渐变过渡比较自然，但边缘还需更细致",
            "customer_feedback": "很喜欢这个设计，颜色很好看",
            "customer_satisfaction": 4,
            "notes": "客户皮肤较敏感，注意选用温和底胶",
        }, headers=headers)
        assert complete_resp.status_code == 200
        completed = complete_resp.json()
        assert completed["status"] == "completed"
        assert completed["service_duration"] == 75

        # 6. 查看 AI 对比分析结果
        comparison_resp = client.get(
            f"/api/v1/services/{service_id}/comparison",
            headers=headers,
        )
        assert comparison_resp.status_code == 200
        comparison = comparison_resp.json()
        assert comparison["similarity_score"] == 85
        assert "differences" in comparison

        # 7. 初始化能力维度 + 查询能力统计
        init_resp = client.post("/api/v1/abilities/dimensions/init", headers=headers)
        assert init_resp.status_code == 201

        stats_resp = client.get("/api/v1/abilities/stats", headers=headers)
        assert stats_resp.status_code == 200
        stats = stats_resp.json()
        assert len(stats["dimensions"]) == 6
        assert stats["total_records"] > 0

        # 8. 查询能力总结
        summary_resp = client.get("/api/v1/abilities/summary", headers=headers)
        assert summary_resp.status_code == 200
        summary = summary_resp.json()
        assert len(summary["strengths"]) > 0
        assert summary["total_services"] >= 1

        # 9. 查看能力趋势
        trend_resp = client.get(
            "/api/v1/abilities/trend/颜色搭配",
            headers=headers,
        )
        assert trend_resp.status_code == 200
        trend = trend_resp.json()
        assert trend["dimension_name"] == "颜色搭配"
        assert len(trend["data_points"]) >= 1


# ================================================================
# 测试 2：多用户数据隔离
# ================================================================

class TestMultiUserDataIsolation:
    """验证不同用户之间数据完全隔离"""

    def test_user_data_isolation(self, client, mock_ai):
        # 用户 A
        headers_a = register_and_login(client, "a@nail.com", "user_a", "password123")
        customer_a = create_customer(client, headers_a, "A的客户", "13100000001")
        design_a = generate_design(client, headers_a, "红色", "A的设计")

        # 用户 B
        headers_b = register_and_login(client, "b@nail.com", "user_b", "password123")
        customer_b = create_customer(client, headers_b, "B的客户", "13100000002")

        # 用户 B 不能看到 A 的客户
        resp = client.get("/api/v1/customers/", headers=headers_b)
        assert resp.status_code == 200
        data = resp.json()
        customer_names = [c["name"] for c in data["customers"]]
        assert "A的客户" not in customer_names
        assert "B的客户" in customer_names

        # 用户 B 不能看到 A 的设计
        resp = client.get("/api/v1/designs/", headers=headers_b)
        assert resp.status_code == 200
        data = resp.json()
        designs_list = data.get("designs", data) if isinstance(data, dict) else data
        assert len(designs_list) == 0

        # 用户 B 不能访问 A 的客户详情
        resp = client.get(f"/api/v1/customers/{customer_a['id']}", headers=headers_b)
        assert resp.status_code == 404

        # 用户 B 不能访问 A 的设计详情
        resp = client.get(f"/api/v1/designs/{design_a['id']}", headers=headers_b)
        assert resp.status_code == 404

        # 用户 B 不能用 A 的客户创建服务记录
        resp = client.post("/api/v1/services/", json={
            "customer_id": customer_a["id"],
            "service_date": "2025-01-15",
        }, headers=headers_b)
        assert resp.status_code == 400  # ValueError → 400

        # 用户 A 的服务记录对 B 不可见
        service_a = create_service_record(client, headers_a, customer_a["id"], design_a["id"])
        resp = client.get("/api/v1/services/", headers=headers_b)
        assert resp.status_code == 200
        assert len(resp.json()) == 0

        # 用户 B 不能访问 A 的服务记录
        resp = client.get(f"/api/v1/services/{service_a['id']}", headers=headers_b)
        assert resp.status_code == 404


# ================================================================
# 测试 3：设计迭代（优化 + 版本历史）
# ================================================================

class TestDesignRefinementWorkflow:
    """设计生成 → 优化 → 版本历史"""

    def test_design_refinement_and_versions(self, client, mock_ai):
        headers = register_and_login(client, "designer@nail.com", "designer", "password123")

        # 1. 生成初始设计
        design_v1 = generate_design(client, headers, "蓝色星空主题", "星空美甲")
        assert design_v1["version"] == 1
        v1_id = design_v1["id"]

        # 2. 优化设计
        refine_resp = client.post(f"/api/v1/designs/{v1_id}/refine", json={
            "refinement_instruction": "增加更多闪亮的星星效果，背景更深蓝",
        }, headers=headers)
        assert refine_resp.status_code == 201
        design_v2 = refine_resp.json()
        assert design_v2["version"] == 2
        assert design_v2["parent_design_id"] == v1_id

        # 3. 查看版本历史
        versions_resp = client.get(
            f"/api/v1/designs/{v1_id}/versions",
            headers=headers,
        )
        assert versions_resp.status_code == 200
        versions = versions_resp.json()
        assert len(versions) == 2
        assert versions[0]["version"] == 1
        assert versions[1]["version"] == 2

        # 4. 归档旧版本
        archive_resp = client.put(
            f"/api/v1/designs/{v1_id}/archive",
            headers=headers,
        )
        assert archive_resp.status_code == 200
        assert archive_resp.json()["is_archived"] == 1

        # 5. 列表过滤归档状态
        list_resp = client.get(
            "/api/v1/designs/",
            params={"is_archived": 0},
            headers=headers,
        )
        assert list_resp.status_code == 200
        data = list_resp.json()
        designs_list = data.get("designs", data) if isinstance(data, dict) else data
        design_ids = [d["id"] for d in designs_list]
        assert v1_id not in design_ids  # 已归档不在列表
        assert design_v2["id"] in design_ids  # 新版本仍在列表


# ================================================================
# 测试 4：服务记录过滤与分页
# ================================================================

class TestServiceFilteringAndPagination:
    """多条服务记录的过滤、状态筛选、分页"""

    def test_filtering_and_pagination(self, client, mock_ai):
        headers = register_and_login(client, "filter@nail.com", "filterer", "password123")
        customer = create_customer(client, headers, "过滤测试客户")

        # 创建 3 条服务记录
        s1 = create_service_record(client, headers, customer["id"], date="2025-01-10")
        s2 = create_service_record(client, headers, customer["id"], date="2025-01-11")
        s3 = create_service_record(client, headers, customer["id"], date="2025-01-12")

        # 完成 s1
        client.put(f"/api/v1/services/{s1['id']}/complete", json={
            "actual_image_path": "/uploads/actuals/test.jpg",
            "service_duration": 60,
        }, headers=headers)

        # 按状态过滤 — pending
        resp = client.get("/api/v1/services/", params={"status": "pending"}, headers=headers)
        assert resp.status_code == 200
        assert len(resp.json()) == 2

        # 按状态过滤 — completed
        resp = client.get("/api/v1/services/", params={"status": "completed"}, headers=headers)
        assert resp.status_code == 200
        assert len(resp.json()) == 1

        # 分页
        resp = client.get("/api/v1/services/", params={"limit": 2, "skip": 0}, headers=headers)
        assert resp.status_code == 200
        assert len(resp.json()) == 2

        resp = client.get("/api/v1/services/", params={"limit": 2, "skip": 2}, headers=headers)
        assert resp.status_code == 200
        assert len(resp.json()) == 1

        # 按客户过滤
        customer2 = create_customer(client, headers, "另一个客户", "13900000001")
        create_service_record(client, headers, customer2["id"], date="2025-01-13")

        resp = client.get("/api/v1/services/", params={"customer_id": customer["id"]}, headers=headers)
        assert resp.status_code == 200
        assert len(resp.json()) == 3  # 只有第一个客户的 3 条


# ================================================================
# 测试 5：错误处理与权限校验
# ================================================================

class TestErrorHandlingWorkflow:
    """各种错误场景的端到端验证"""

    def test_unauthenticated_access_denied(self, client):
        """未登录不能访问受保护路由"""
        protected_routes = [
            ("GET", "/api/v1/customers/"),
            ("GET", "/api/v1/designs/"),
            ("GET", "/api/v1/services/"),
            ("GET", "/api/v1/users/me"),
            ("GET", "/api/v1/abilities/stats"),
        ]
        for method, url in protected_routes:
            resp = client.request(method, url)
            assert resp.status_code == 401, f"{method} {url} should require auth"

    def test_nonexistent_resource_returns_404(self, client, mock_ai):
        """访问不存在的资源返回 404"""
        headers = register_and_login(client, "err@nail.com", "erruser", "password123")

        assert client.get("/api/v1/customers/9999", headers=headers).status_code == 404
        assert client.get("/api/v1/designs/9999", headers=headers).status_code == 404
        assert client.get("/api/v1/services/9999", headers=headers).status_code == 404

    def test_invalid_login_credentials(self, client):
        """错误凭证登录失败"""
        # 未注册的用户
        resp = client.post("/api/v1/auth/login", data={
            "username": "nobody@nail.com",
            "password": "wrongpass",
        })
        assert resp.status_code == 401

    def test_duplicate_registration(self, client):
        """重复注册同一邮箱失败"""
        user_data = {"email": "dup@nail.com", "username": "dup1", "password": "password123"}
        resp1 = client.post("/api/v1/auth/register", json=user_data)
        assert resp1.status_code == 201

        resp2 = client.post("/api/v1/auth/register", json=user_data)
        assert resp2.status_code in (400, 409)  # 冲突

    def test_complete_nonexistent_service(self, client, mock_ai):
        """完成不存在的服务记录返回错误"""
        headers = register_and_login(client, "svc@nail.com", "svcuser", "password123")
        resp = client.put("/api/v1/services/9999/complete", json={
            "actual_image_path": "/uploads/actuals/test.jpg",
            "service_duration": 60,
        }, headers=headers)
        assert resp.status_code == 400

    def test_service_with_invalid_customer(self, client, mock_ai):
        """用不存在的客户 ID 创建服务记录失败"""
        headers = register_and_login(client, "inv@nail.com", "invuser", "password123")
        resp = client.post("/api/v1/services/", json={
            "customer_id": 9999,
            "service_date": "2025-01-15",
        }, headers=headers)
        assert resp.status_code == 400

    def test_manual_analysis_trigger(self, client, mock_ai):
        """手动触发 AI 分析"""
        headers = register_and_login(client, "analyze@nail.com", "analyzer", "password123")
        customer = create_customer(client, headers, "分析测试客户")
        design = generate_design(client, headers, "测试", "分析测试设计")
        service = create_service_record(client, headers, customer["id"], design["id"])

        # 完成服务
        client.put(f"/api/v1/services/{service['id']}/complete", json={
            "actual_image_path": "/uploads/actuals/test.jpg",
            "service_duration": 60,
        }, headers=headers)

        # 手动重新触发分析
        resp = client.post(
            f"/api/v1/services/{service['id']}/analyze",
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["similarity_score"] == 85
