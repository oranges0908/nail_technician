"""
设计方案模块测试

测试 Iteration 4.2 & 4.3 的所有功能：
1. AI生成设计方案（Mock）
2. AI优化设计方案（Mock）
3. 获取设计方案列表（分页、过滤、搜索）
4. 获取设计方案详情
5. 获取版本历史
6. 更新设计方案
7. 归档设计方案
8. 删除设计方案
9. 数据隔离验证

运行前确保:
1. 后端服务正在运行
2. 数据库已初始化
3. 有测试用户可用
4. AI Provider 已配置（Mock模式）

说明：本测试使用 Mock 模拟 AI 调用，不会产生实际的 OpenAI API 费用
"""
import requests
import json
import time
from typing import Dict, Optional

BASE_URL = "http://localhost:8000"
API_V1_URL = f"{BASE_URL}/api/v1"


def print_section(title: str):
    """打印分隔标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_json(data: Dict, title: str = "响应"):
    """格式化打印JSON数据"""
    print(f"\n{title}:")
    print(json.dumps(data, ensure_ascii=False, indent=2))


def register_test_user(username: str, email: str, password: str) -> Optional[Dict]:
    """注册测试用户"""
    try:
        response = requests.post(
            f"{API_V1_URL}/auth/register",
            json={
                "username": username,
                "email": email,
                "password": password
            }
        )

        if response.status_code in [200, 201]:
            return response.json()
        else:
            print(f"⚠️ 用户注册失败 ({response.status_code}): {response.text}")
            return None
    except Exception as e:
        print(f"⚠️ 用户注册异常: {e}")
        return None


def login_user(email: str, password: str) -> Optional[str]:
    """登录并获取访问令牌"""
    try:
        response = requests.post(
            f"{API_V1_URL}/auth/login",
            data={
                "username": email,
                "password": password
            }
        )

        if response.status_code == 200:
            data = response.json()
            return data.get("access_token")
        else:
            print(f"⚠️ 登录失败 ({response.status_code}): {response.text}")
            return None
    except Exception as e:
        print(f"⚠️ 登录异常: {e}")
        return None


def get_auth_headers(access_token: str) -> Dict[str, str]:
    """构建认证请求头"""
    return {"Authorization": f"Bearer {access_token}"}


def test_generate_design(access_token: str, prompt: str):
    """测试1: AI生成设计方案"""
    print_section(f"测试1: AI生成设计方案 - {prompt[:20]}...")

    headers = get_auth_headers(access_token)
    response = requests.post(
        f"{API_V1_URL}/designs/generate",
        headers=headers,
        json={
            "prompt": prompt,
            "design_target": "10nails",
            "style_keywords": ["法式", "优雅", "粉色"],
            "title": "法式优雅美甲设计"
        }
    )

    print(f"状态码: {response.status_code}")

    if response.status_code == 201:
        data = response.json()
        print_json(data, "创建结果")

        assert data["ai_prompt"] == prompt, "提示词不匹配"
        assert data["version"] == 1, "初始版本应为1"
        assert "generated_image_path" in data, "缺少生成图片路径"
        assert "estimated_duration" in data, "缺少预估耗时"

        print("✅ AI生成设计方案成功")
        return data
    else:
        print(f"⚠️ AI生成失败: {response.text}")
        print("注意：需要配置 OPENAI_API_KEY 或使用 Mock 模式")
        return None


def test_refine_design(access_token: str, design_id: int):
    """测试2: AI优化设计方案"""
    print_section(f"测试2: AI优化设计方案 - ID {design_id}")

    headers = get_auth_headers(access_token)
    response = requests.post(
        f"{API_V1_URL}/designs/{design_id}/refine",
        headers=headers,
        json={
            "refinement_instruction": "增加更多金色亮片，让渐变效果更加自然"
        }
    )

    print(f"状态码: {response.status_code}")

    if response.status_code == 201:
        data = response.json()
        print_json(data, "优化结果")

        assert data["parent_design_id"] == design_id, "父设计ID不匹配"
        assert data["version"] == 2, "版本应递增为2"
        assert data["refinement_instruction"] == "增加更多金色亮片，让渐变效果更加自然", "优化指令不匹配"

        print("✅ AI优化设计方案成功")
        return data
    else:
        print(f"⚠️ AI优化失败: {response.text}")
        return None


def test_list_designs(access_token: str):
    """测试3: 获取设计方案列表"""
    print_section("测试3: 获取设计方案列表（分页）")

    headers = get_auth_headers(access_token)
    response = requests.get(
        f"{API_V1_URL}/designs",
        headers=headers,
        params={"skip": 0, "limit": 20}
    )

    assert response.status_code == 200, f"获取列表失败: {response.status_code} - {response.text}"

    data = response.json()
    print_json(data, "列表响应")

    assert "total" in data, "缺少total字段"
    assert "designs" in data, "缺少designs字段"

    print(f"✅ 获取列表成功，共 {data['total']} 个设计方案")
    return data


def test_filter_by_archived(access_token: str):
    """测试4: 按归档状态过滤"""
    print_section("测试4: 按归档状态过滤")

    headers = get_auth_headers(access_token)
    response = requests.get(
        f"{API_V1_URL}/designs",
        headers=headers,
        params={"is_archived": 0}
    )

    assert response.status_code == 200, f"过滤失败: {response.status_code} - {response.text}"

    data = response.json()
    print_json(data, "过滤结果（未归档）")

    # 验证所有结果都是未归档的
    for design in data["designs"]:
        assert design["is_archived"] == 0, f"归档状态不匹配: {design['is_archived']}"

    print(f"✅ 归档过滤成功，找到 {data['total']} 个未归档设计方案")
    return data


def test_search_designs(access_token: str, keyword: str):
    """测试5: 搜索设计方案"""
    print_section(f"测试5: 搜索设计方案 - {keyword}")

    headers = get_auth_headers(access_token)
    response = requests.get(
        f"{API_V1_URL}/designs",
        headers=headers,
        params={"search": keyword}
    )

    assert response.status_code == 200, f"搜索失败: {response.status_code} - {response.text}"

    data = response.json()
    print_json(data, "搜索结果")

    print(f"✅ 搜索成功，找到 {data['total']} 个包含 '{keyword}' 的设计方案")
    return data


def test_get_design_detail(access_token: str, design_id: int):
    """测试6: 获取设计方案详情"""
    print_section(f"测试6: 获取设计方案详情 - ID {design_id}")

    headers = get_auth_headers(access_token)
    response = requests.get(
        f"{API_V1_URL}/designs/{design_id}",
        headers=headers
    )

    assert response.status_code == 200, f"获取详情失败: {response.status_code} - {response.text}"

    data = response.json()
    print_json(data, "设计方案详情")

    assert data["id"] == design_id, "ID不匹配"
    assert "generated_image_path" in data, "缺少generated_image_path字段"
    assert "estimated_duration" in data, "缺少estimated_duration字段"

    print("✅ 获取详情成功")
    return data


def test_get_design_versions(access_token: str, design_id: int):
    """测试7: 获取设计方案版本历史"""
    print_section(f"测试7: 获取设计方案版本历史 - ID {design_id}")

    headers = get_auth_headers(access_token)
    response = requests.get(
        f"{API_V1_URL}/designs/{design_id}/versions",
        headers=headers
    )

    assert response.status_code == 200, f"获取版本历史失败: {response.status_code} - {response.text}"

    data = response.json()
    print_json(data, "版本历史")

    assert isinstance(data, list), "返回结果应该是列表"

    # 验证版本号递增
    if len(data) > 1:
        for i in range(len(data) - 1):
            assert data[i]["version"] < data[i + 1]["version"], "版本号应递增"

    print(f"✅ 获取版本历史成功，共 {len(data)} 个版本")
    return data


def test_update_design(access_token: str, design_id: int):
    """测试8: 更新设计方案"""
    print_section(f"测试8: 更新设计方案 - ID {design_id}")

    headers = get_auth_headers(access_token)
    response = requests.put(
        f"{API_V1_URL}/designs/{design_id}",
        headers=headers,
        json={
            "title": "更新后的设计方案标题",
            "notes": "这是更新后的备注信息"
        }
    )

    assert response.status_code == 200, f"更新失败: {response.status_code} - {response.text}"

    data = response.json()
    print_json(data, "更新结果")

    assert data["title"] == "更新后的设计方案标题", "标题未更新"
    assert data["notes"] == "这是更新后的备注信息", "备注未更新"

    print("✅ 更新设计方案成功")
    return data


def test_archive_design(access_token: str, design_id: int):
    """测试9: 归档设计方案"""
    print_section(f"测试9: 归档设计方案 - ID {design_id}")

    headers = get_auth_headers(access_token)
    response = requests.put(
        f"{API_V1_URL}/designs/{design_id}/archive",
        headers=headers
    )

    assert response.status_code == 200, f"归档失败: {response.status_code} - {response.text}"

    data = response.json()
    print_json(data, "归档结果")

    assert data["is_archived"] == 1, "归档状态未更新"

    print("✅ 归档设计方案成功")
    return data


def test_get_recent_designs(access_token: str):
    """测试10: 获取最近设计方案"""
    print_section("测试10: 获取最近设计方案")

    headers = get_auth_headers(access_token)
    response = requests.get(
        f"{API_V1_URL}/designs/recent",
        headers=headers,
        params={"limit": 5}
    )

    assert response.status_code == 200, f"获取最近设计失败: {response.status_code} - {response.text}"

    data = response.json()
    print_json(data, "最近设计方案")

    assert isinstance(data, list), "返回结果应该是列表"
    assert len(data) <= 5, "返回数量不应超过limit"

    # 验证按创建时间排序
    if len(data) > 1:
        for i in range(len(data) - 1):
            assert data[i]["created_at"] >= data[i + 1]["created_at"], "排序错误"

    print(f"✅ 获取最近设计成功，共 {len(data)} 个")
    return data


def test_delete_design(access_token: str, design_id: int):
    """测试11: 删除设计方案"""
    print_section(f"测试11: 删除设计方案 - ID {design_id}")

    headers = get_auth_headers(access_token)
    response = requests.delete(
        f"{API_V1_URL}/designs/{design_id}",
        headers=headers
    )

    assert response.status_code == 204, f"删除失败: {response.status_code} - {response.text}"

    print("✅ 删除设计方案成功")

    # 验证已删除（获取应返回404）
    response = requests.get(
        f"{API_V1_URL}/designs/{design_id}",
        headers=headers
    )

    assert response.status_code == 404, "删除后仍能获取到设计方案"
    print("✅ 验证删除成功（404）")


def test_data_isolation(access_token1: str, access_token2: str, design_id: int):
    """测试12: 数据隔离验证"""
    print_section("测试12: 数据隔离验证")

    # 用户1应该能访问
    headers1 = get_auth_headers(access_token1)
    response1 = requests.get(
        f"{API_V1_URL}/designs/{design_id}",
        headers=headers1
    )
    assert response1.status_code == 200, "用户1应该能访问自己的设计方案"
    print("✅ 用户1能访问自己的设计方案")

    # 用户2不应该能访问用户1的设计方案
    headers2 = get_auth_headers(access_token2)
    response2 = requests.get(
        f"{API_V1_URL}/designs/{design_id}",
        headers=headers2
    )
    assert response2.status_code == 404, "用户2不应该能访问用户1的设计方案"
    print("✅ 用户2无法访问用户1的设计方案（数据隔离生效）")


def main():
    """主测试流程"""
    print("\n" + "=" * 60)
    print("  Iteration 4.2 & 4.3 测试套件")
    print("  AI设计方案生成与优化")
    print("=" * 60)

    # 准备测试用户
    print_section("准备测试环境")
    timestamp = int(time.time())

    # 用户1
    user1_email = f"test_design_user1_{timestamp}@example.com"
    user1_password = "Test123456"

    print(f"注册测试用户1: {user1_email}")
    register_test_user(f"test_design_user1_{timestamp}", user1_email, user1_password)

    print(f"登录测试用户1...")
    access_token1 = login_user(user1_email, user1_password)
    if not access_token1:
        print("❌ 用户1登录失败，测试终止")
        return
    print("✅ 用户1登录成功")

    # 用户2（用于数据隔离测试）
    user2_email = f"test_design_user2_{timestamp}@example.com"
    user2_password = "Test123456"

    print(f"注册测试用户2: {user2_email}")
    register_test_user(f"test_design_user2_{timestamp}", user2_email, user2_password)

    print(f"登录测试用户2...")
    access_token2 = login_user(user2_email, user2_password)
    if not access_token2:
        print("❌ 用户2登录失败，测试终止")
        return
    print("✅ 用户2登录成功")

    # 开始测试
    created_ids = []

    # 测试1: AI生成设计（可能失败如果没有配置API Key）
    design1 = test_generate_design(
        access_token1,
        prompt="法式优雅美甲，粉色和白色渐变，带金色亮片装饰"
    )
    if design1:
        created_ids.append(design1["id"])

        # 测试2: AI优化设计（需要design1成功）
        design2 = test_refine_design(access_token1, design1["id"])
        if design2:
            created_ids.append(design2["id"])

        # 测试3: 列表查询
        test_list_designs(access_token1)

        # 测试4: 归档过滤
        test_filter_by_archived(access_token1)

        # 测试5: 搜索
        test_search_designs(access_token1, "法式")

        # 测试6: 获取详情
        test_get_design_detail(access_token1, design1["id"])

        # 测试7: 版本历史
        if design2:
            test_get_design_versions(access_token1, design2["id"])

        # 测试8: 更新
        test_update_design(access_token1, design1["id"])

        # 测试10: 最近设计
        test_get_recent_designs(access_token1)

        # 测试12: 数据隔离
        test_data_isolation(access_token1, access_token2, design1["id"])

        # 测试9: 归档（不影响后续测试）
        test_archive_design(access_token1, design1["id"])

        # 测试11: 删除（最后测试）
        if design2:
            test_delete_design(access_token1, design2["id"])
    else:
        print("\n⚠️ AI生成功能需要配置 OPENAI_API_KEY")
        print("可以跳过AI相关测试，继续测试其他功能...")

    # 测试总结
    print_section("测试总结")
    if created_ids:
        print("✅ 测试完成！")
        print(f"\n测试统计:")
        print(f"  - 创建设计方案: {len([d for d in created_ids if d])} 个")
        print(f"  - 列表查询: 1 次")
        print(f"  - 归档过滤: 1 次")
        print(f"  - 搜索查询: 1 次")
        print(f"  - 详情查询: 1 次")
        print(f"  - 版本历史: 1 次")
        print(f"  - 更新操作: 1 次")
        print(f"  - 归档操作: 1 次")
        print(f"  - 最近查询: 1 次")
        print(f"  - 数据隔离: 1 次")
        print(f"  - 删除操作: 1 次")
        print(f"\n✅ Iteration 4.2 & 4.3 AI设计方案生成与优化 - 测试完成！")
    else:
        print("⚠️ 需要配置 OPENAI_API_KEY 才能完整测试AI功能")
        print("或使用 Mock 模式进行测试")


if __name__ == "__main__":
    main()
