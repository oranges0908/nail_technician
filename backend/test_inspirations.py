"""
灵感图库模块测试

测试 Iteration 4.1 的所有功能：
1. 创建灵感图
2. 获取灵感图列表（分页、过滤、搜索）
3. 获取灵感图详情
4. 更新灵感图
5. 删除灵感图
6. 热门灵感图查询
7. 最近灵感图查询
8. 标记灵感图使用
9. 数据隔离验证

运行前确保:
1. 后端服务正在运行
2. 数据库已初始化
3. 有测试用户可用
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


def test_create_inspiration(access_token: str, title: str, tags: list, category: str):
    """测试1: 创建灵感图"""
    print_section(f"测试1: 创建灵感图 - {title}")

    headers = get_auth_headers(access_token)
    response = requests.post(
        f"{API_V1_URL}/inspirations",
        headers=headers,
        json={
            "image_path": f"/uploads/inspirations/{title.replace(' ', '_')}.jpg",
            "title": title,
            "description": f"这是一张{category}风格的美甲设计灵感图",
            "tags": tags,
            "category": category,
            "source_platform": "小红书"
        }
    )

    assert response.status_code == 201, f"创建失败: {response.status_code} - {response.text}"

    data = response.json()
    print_json(data, "创建结果")

    assert data["title"] == title, "标题不匹配"
    assert data["tags"] == tags, "标签不匹配"
    assert data["category"] == category, "分类不匹配"
    assert data["usage_count"] == 0, "初始使用次数应为0"

    print("✅ 创建灵感图成功")
    return data


def test_list_inspirations(access_token: str):
    """测试2: 获取灵感图列表"""
    print_section("测试2: 获取灵感图列表（分页）")

    headers = get_auth_headers(access_token)
    response = requests.get(
        f"{API_V1_URL}/inspirations",
        headers=headers,
        params={"skip": 0, "limit": 20}
    )

    assert response.status_code == 200, f"获取列表失败: {response.status_code} - {response.text}"

    data = response.json()
    print_json(data, "列表响应")

    assert "total" in data, "缺少total字段"
    assert "inspirations" in data, "缺少inspirations字段"
    assert data["total"] > 0, "应该至少有1个灵感图"

    print(f"✅ 获取列表成功，共 {data['total']} 个灵感图")
    return data


def test_filter_by_category(access_token: str, category: str):
    """测试3: 按分类过滤灵感图"""
    print_section(f"测试3: 按分类过滤 - {category}")

    headers = get_auth_headers(access_token)
    response = requests.get(
        f"{API_V1_URL}/inspirations",
        headers=headers,
        params={"category": category}
    )

    assert response.status_code == 200, f"过滤失败: {response.status_code} - {response.text}"

    data = response.json()
    print_json(data, "过滤结果")

    # 验证所有结果都是指定分类
    for inspiration in data["inspirations"]:
        assert inspiration["category"] == category, f"分类不匹配: {inspiration['category']}"

    print(f"✅ 分类过滤成功，找到 {data['total']} 个 {category} 灵感图")
    return data


def test_filter_by_tags(access_token: str, tag: str):
    """测试4: 按标签过滤灵感图"""
    print_section(f"测试4: 按标签过滤 - {tag}")

    headers = get_auth_headers(access_token)
    response = requests.get(
        f"{API_V1_URL}/inspirations",
        headers=headers,
        params={"tags": [tag]}
    )

    assert response.status_code == 200, f"过滤失败: {response.status_code} - {response.text}"

    data = response.json()
    print_json(data, "过滤结果")

    # 验证所有结果都包含指定标签
    for inspiration in data["inspirations"]:
        assert tag in inspiration["tags"], f"标签不匹配: {inspiration['tags']}"

    print(f"✅ 标签过滤成功，找到 {data['total']} 个包含 '{tag}' 的灵感图")
    return data


def test_search_inspirations(access_token: str, keyword: str):
    """测试5: 搜索灵感图"""
    print_section(f"测试5: 搜索灵感图 - {keyword}")

    headers = get_auth_headers(access_token)
    response = requests.get(
        f"{API_V1_URL}/inspirations",
        headers=headers,
        params={"search": keyword}
    )

    assert response.status_code == 200, f"搜索失败: {response.status_code} - {response.text}"

    data = response.json()
    print_json(data, "搜索结果")

    # 验证结果包含搜索关键词
    for inspiration in data["inspirations"]:
        title = inspiration.get("title", "").lower()
        description = inspiration.get("description", "").lower()
        assert keyword.lower() in title or keyword.lower() in description, \
            f"搜索结果不匹配: {inspiration['title']}"

    print(f"✅ 搜索成功，找到 {data['total']} 个包含 '{keyword}' 的灵感图")
    return data


def test_get_inspiration_detail(access_token: str, inspiration_id: int):
    """测试6: 获取灵感图详情"""
    print_section(f"测试6: 获取灵感图详情 - ID {inspiration_id}")

    headers = get_auth_headers(access_token)
    response = requests.get(
        f"{API_V1_URL}/inspirations/{inspiration_id}",
        headers=headers
    )

    assert response.status_code == 200, f"获取详情失败: {response.status_code} - {response.text}"

    data = response.json()
    print_json(data, "灵感图详情")

    assert data["id"] == inspiration_id, "ID不匹配"
    assert "image_path" in data, "缺少image_path字段"
    assert "usage_count" in data, "缺少usage_count字段"

    print("✅ 获取详情成功")
    return data


def test_update_inspiration(access_token: str, inspiration_id: int):
    """测试7: 更新灵感图"""
    print_section(f"测试7: 更新灵感图 - ID {inspiration_id}")

    headers = get_auth_headers(access_token)
    new_tags = ["粉色", "优雅", "简约", "法式"]

    response = requests.put(
        f"{API_V1_URL}/inspirations/{inspiration_id}",
        headers=headers,
        json={
            "tags": new_tags,
            "description": "更新后的描述信息"
        }
    )

    assert response.status_code == 200, f"更新失败: {response.status_code} - {response.text}"

    data = response.json()
    print_json(data, "更新结果")

    assert data["tags"] == new_tags, "标签未更新"
    assert data["description"] == "更新后的描述信息", "描述未更新"

    print("✅ 更新灵感图成功")
    return data


def test_use_inspiration(access_token: str, inspiration_id: int):
    """测试8: 标记灵感图使用"""
    print_section(f"测试8: 标记灵感图使用 - ID {inspiration_id}")

    # 先获取当前使用次数
    headers = get_auth_headers(access_token)
    response = requests.get(
        f"{API_V1_URL}/inspirations/{inspiration_id}",
        headers=headers
    )
    original_count = response.json()["usage_count"]

    # 标记使用
    response = requests.post(
        f"{API_V1_URL}/inspirations/{inspiration_id}/use",
        headers=headers
    )

    assert response.status_code == 200, f"标记使用失败: {response.status_code} - {response.text}"

    data = response.json()
    print_json(data, "标记使用结果")

    assert data["usage_count"] == original_count + 1, "使用次数未增加"
    assert data["last_used_at"] is not None, "last_used_at未更新"

    print(f"✅ 标记使用成功，使用次数: {original_count} → {data['usage_count']}")
    return data


def test_get_popular_inspirations(access_token: str):
    """测试9: 获取热门灵感图"""
    print_section("测试9: 获取热门灵感图")

    headers = get_auth_headers(access_token)
    response = requests.get(
        f"{API_V1_URL}/inspirations/popular",
        headers=headers,
        params={"limit": 5}
    )

    assert response.status_code == 200, f"获取热门灵感图失败: {response.status_code} - {response.text}"

    data = response.json()
    print_json(data, "热门灵感图")

    assert isinstance(data, list), "返回结果应该是列表"
    assert len(data) <= 5, "返回数量不应超过limit"

    # 验证按使用次数排序
    if len(data) > 1:
        for i in range(len(data) - 1):
            assert data[i]["usage_count"] >= data[i + 1]["usage_count"], "排序错误"

    print(f"✅ 获取热门灵感图成功，共 {len(data)} 个")
    return data


def test_get_recent_inspirations(access_token: str):
    """测试10: 获取最近灵感图"""
    print_section("测试10: 获取最近灵感图")

    headers = get_auth_headers(access_token)
    response = requests.get(
        f"{API_V1_URL}/inspirations/recent",
        headers=headers,
        params={"limit": 5}
    )

    assert response.status_code == 200, f"获取最近灵感图失败: {response.status_code} - {response.text}"

    data = response.json()
    print_json(data, "最近灵感图")

    assert isinstance(data, list), "返回结果应该是列表"
    assert len(data) <= 5, "返回数量不应超过limit"

    # 验证按创建时间排序
    if len(data) > 1:
        for i in range(len(data) - 1):
            assert data[i]["created_at"] >= data[i + 1]["created_at"], "排序错误"

    print(f"✅ 获取最近灵感图成功，共 {len(data)} 个")
    return data


def test_delete_inspiration(access_token: str, inspiration_id: int):
    """测试11: 删除灵感图"""
    print_section(f"测试11: 删除灵感图 - ID {inspiration_id}")

    headers = get_auth_headers(access_token)
    response = requests.delete(
        f"{API_V1_URL}/inspirations/{inspiration_id}",
        headers=headers
    )

    assert response.status_code == 204, f"删除失败: {response.status_code} - {response.text}"

    print("✅ 删除灵感图成功")

    # 验证已删除（获取应返回404）
    response = requests.get(
        f"{API_V1_URL}/inspirations/{inspiration_id}",
        headers=headers
    )

    assert response.status_code == 404, "删除后仍能获取到灵感图"
    print("✅ 验证删除成功（404）")


def test_data_isolation(access_token1: str, access_token2: str, inspiration_id: int):
    """测试12: 数据隔离验证"""
    print_section("测试12: 数据隔离验证")

    # 用户1应该能访问
    headers1 = get_auth_headers(access_token1)
    response1 = requests.get(
        f"{API_V1_URL}/inspirations/{inspiration_id}",
        headers=headers1
    )
    assert response1.status_code == 200, "用户1应该能访问自己的灵感图"
    print("✅ 用户1能访问自己的灵感图")

    # 用户2不应该能访问用户1的灵感图
    headers2 = get_auth_headers(access_token2)
    response2 = requests.get(
        f"{API_V1_URL}/inspirations/{inspiration_id}",
        headers=headers2
    )
    assert response2.status_code == 404, "用户2不应该能访问用户1的灵感图"
    print("✅ 用户2无法访问用户1的灵感图（数据隔离生效）")


def main():
    """主测试流程"""
    print("\n" + "=" * 60)
    print("  Iteration 4.1 测试套件")
    print("  灵感图库管理")
    print("=" * 60)

    # 准备测试用户
    print_section("准备测试环境")
    timestamp = int(time.time())

    # 用户1
    user1_email = f"test_inspiration_user1_{timestamp}@example.com"
    user1_password = "Test123456"

    print(f"注册测试用户1: {user1_email}")
    register_test_user(f"test_inspiration_user1_{timestamp}", user1_email, user1_password)

    print(f"登录测试用户1...")
    access_token1 = login_user(user1_email, user1_password)
    if not access_token1:
        print("❌ 用户1登录失败，测试终止")
        return
    print("✅ 用户1登录成功")

    # 用户2（用于数据隔离测试）
    user2_email = f"test_inspiration_user2_{timestamp}@example.com"
    user2_password = "Test123456"

    print(f"注册测试用户2: {user2_email}")
    register_test_user(f"test_inspiration_user2_{timestamp}", user2_email, user2_password)

    print(f"登录测试用户2...")
    access_token2 = login_user(user2_email, user2_password)
    if not access_token2:
        print("❌ 用户2登录失败，测试终止")
        return
    print("✅ 用户2登录成功")

    # 开始测试
    created_ids = []

    # 测试1: 创建多个灵感图
    inspiration1 = test_create_inspiration(
        access_token1,
        title="法式优雅美甲",
        tags=["法式", "粉色", "优雅"],
        category="法式"
    )
    created_ids.append(inspiration1["id"])

    inspiration2 = test_create_inspiration(
        access_token1,
        title="渐变星空美甲",
        tags=["渐变", "蓝色", "星空"],
        category="渐变"
    )
    created_ids.append(inspiration2["id"])

    inspiration3 = test_create_inspiration(
        access_token1,
        title="粉色樱花美甲",
        tags=["粉色", "樱花", "浪漫"],
        category="彩绘"
    )
    created_ids.append(inspiration3["id"])

    # 测试2: 列表查询
    test_list_inspirations(access_token1)

    # 测试3: 分类过滤
    test_filter_by_category(access_token1, "法式")

    # 测试4: 标签过滤
    test_filter_by_tags(access_token1, "粉色")

    # 测试5: 搜索
    test_search_inspirations(access_token1, "美甲")

    # 测试6: 获取详情
    test_get_inspiration_detail(access_token1, inspiration1["id"])

    # 测试7: 更新
    test_update_inspiration(access_token1, inspiration1["id"])

    # 测试8: 标记使用（多次标记同一个）
    test_use_inspiration(access_token1, inspiration1["id"])
    test_use_inspiration(access_token1, inspiration1["id"])

    # 测试9: 热门灵感图
    test_get_popular_inspirations(access_token1)

    # 测试10: 最近灵感图
    test_get_recent_inspirations(access_token1)

    # 测试12: 数据隔离
    test_data_isolation(access_token1, access_token2, inspiration1["id"])

    # 测试11: 删除（最后测试）
    test_delete_inspiration(access_token1, inspiration2["id"])

    # 测试总结
    print_section("测试总结")
    print("✅ 所有测试通过！")
    print(f"\n测试统计:")
    print(f"  - 创建灵感图: 3 个")
    print(f"  - 列表查询: 1 次")
    print(f"  - 分类过滤: 1 次")
    print(f"  - 标签过滤: 1 次")
    print(f"  - 搜索查询: 1 次")
    print(f"  - 详情查询: 1 次")
    print(f"  - 更新操作: 1 次")
    print(f"  - 标记使用: 2 次")
    print(f"  - 热门查询: 1 次")
    print(f"  - 最近查询: 1 次")
    print(f"  - 数据隔离: 1 次")
    print(f"  - 删除操作: 1 次")
    print(f"\n✅ Iteration 4.1 灵感图库管理 - 全部功能测试通过！")


if __name__ == "__main__":
    main()
