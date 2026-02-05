"""
测试客户管理 API

运行前确保:
1. 后端服务正在运行 (uvicorn app.main:app --reload)
2. 数据库已初始化，有测试用户
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# 开发模式：使用假token
HEADERS = {
    "Authorization": "Bearer dev-token",
    "Content-Type": "application/json"
}

# 全局变量存储测试数据
test_customer_id = None


def print_section(title: str):
    """打印分隔标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_response(response: requests.Response, show_json: bool = True):
    """打印响应信息"""
    print(f"状态码: {response.status_code}")

    if show_json and response.text:
        try:
            data = response.json()
            print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
        except:
            print(f"响应: {response.text}")

    return response


def test_health_check():
    """测试健康检查"""
    print_section("测试0: 健康检查")

    response = requests.get(f"{BASE_URL}/health")
    print_response(response)

    if response.status_code == 200:
        print("✅ 后端服务运行正常")
        return True
    else:
        print("❌ 后端服务未运行")
        return False


def test_create_customer():
    """测试创建客户"""
    global test_customer_id

    print_section("测试1: 创建客户")

    customer_data = {
        "name": "张小美",
        "phone": "13800138001",
        "email": "zhangxiaomei@example.com",
        "notes": "喜欢简约风格，偏好粉色系",
        "is_active": True
    }

    response = requests.post(
        f"{BASE_URL}/customers",
        headers=HEADERS,
        json=customer_data
    )

    print_response(response)

    if response.status_code == 201:
        data = response.json()
        test_customer_id = data["id"]
        print(f"✅ 创建成功! 客户ID: {test_customer_id}")
        return test_customer_id
    else:
        print("❌ 创建失败")
        return None


def test_create_duplicate_phone():
    """测试创建重复手机号客户（应该失败）"""
    print_section("测试2: 创建重复手机号客户（应该失败）")

    customer_data = {
        "name": "李小丽",
        "phone": "13800138001",  # 与上一个客户相同
        "email": "lixiaoli@example.com"
    }

    response = requests.post(
        f"{BASE_URL}/customers",
        headers=HEADERS,
        json=customer_data
    )

    print_response(response)

    if response.status_code == 409:
        print("✅ 正确拒绝了重复手机号")
    else:
        print("❌ 应该返回 409 Conflict")


def test_get_customer_list():
    """测试获取客户列表"""
    print_section("测试3: 获取客户列表")

    response = requests.get(
        f"{BASE_URL}/customers",
        headers=HEADERS,
        params={"skip": 0, "limit": 10}
    )

    print_response(response)

    if response.status_code == 200:
        data = response.json()
        print(f"✅ 获取成功! 总数: {data['total']}, 返回: {len(data['customers'])} 个客户")
    else:
        print("❌ 获取失败")


def test_search_customers():
    """测试搜索客户"""
    print_section("测试4: 搜索客户（姓名包含'张'）")

    response = requests.get(
        f"{BASE_URL}/customers",
        headers=HEADERS,
        params={"search": "张"}
    )

    print_response(response)

    if response.status_code == 200:
        data = response.json()
        print(f"✅ 搜索成功! 找到 {data['total']} 个匹配客户")
    else:
        print("❌ 搜索失败")


def test_get_customer_detail():
    """测试获取客户详情"""
    print_section("测试5: 获取客户详情")

    if not test_customer_id:
        print("⚠️ 跳过：没有可用的客户ID")
        return

    response = requests.get(
        f"{BASE_URL}/customers/{test_customer_id}",
        headers=HEADERS
    )

    print_response(response)

    if response.status_code == 200:
        print("✅ 获取详情成功")
    else:
        print("❌ 获取详情失败")


def test_update_customer():
    """测试更新客户信息"""
    print_section("测试6: 更新客户信息")

    if not test_customer_id:
        print("⚠️ 跳过：没有可用的客户ID")
        return

    update_data = {
        "name": "张小美（VIP）",
        "notes": "VIP客户，喜欢粉色系和珍珠装饰"
    }

    response = requests.put(
        f"{BASE_URL}/customers/{test_customer_id}",
        headers=HEADERS,
        json=update_data
    )

    print_response(response)

    if response.status_code == 200:
        data = response.json()
        print(f"✅ 更新成功! 新姓名: {data['name']}")
    else:
        print("❌ 更新失败")


def test_create_customer_profile():
    """测试创建客户档案"""
    print_section("测试7: 创建客户档案")

    if not test_customer_id:
        print("⚠️ 跳过：没有可用的客户ID")
        return

    profile_data = {
        "nail_shape": "椭圆形",
        "nail_length": "中等",
        "nail_condition": "指甲质地良好，无明显问题",
        "nail_photos": [
            "/uploads/nails/20260203_001_nail1.png",
            "/uploads/nails/20260203_002_nail2.png"
        ],
        "color_preferences": ["粉色", "裸色", "浅紫色"],
        "color_dislikes": ["黑色", "深绿色"],
        "style_preferences": ["简约", "可爱", "清新"],
        "pattern_preferences": "喜欢珍珠、碎钻装饰，不喜欢复杂图案",
        "allergies": "对某些胶水过敏",
        "prohibitions": "不接受过长的指甲",
        "occasion_preferences": {
            "daily": True,
            "work": True,
            "party": False,
            "wedding": False
        },
        "maintenance_preference": "持久性"
    }

    response = requests.put(
        f"{BASE_URL}/customers/{test_customer_id}/profile",
        headers=HEADERS,
        json=profile_data
    )

    print_response(response)

    if response.status_code == 200:
        print("✅ 创建档案成功")
    else:
        print("❌ 创建档案失败")


def test_get_customer_profile():
    """测试获取客户档案"""
    print_section("测试8: 获取客户档案")

    if not test_customer_id:
        print("⚠️ 跳过：没有可用的客户ID")
        return

    response = requests.get(
        f"{BASE_URL}/customers/{test_customer_id}/profile",
        headers=HEADERS
    )

    print_response(response)

    if response.status_code == 200:
        print("✅ 获取档案成功")
    else:
        print("❌ 获取档案失败")


def test_update_customer_profile():
    """测试更新客户档案"""
    print_section("测试9: 更新客户档案")

    if not test_customer_id:
        print("⚠️ 跳过：没有可用的客户ID")
        return

    update_data = {
        "color_preferences": ["粉色", "裸色", "浅紫色", "香槟金"],
        "style_preferences": ["简约", "可爱", "清新", "优雅"]
    }

    response = requests.put(
        f"{BASE_URL}/customers/{test_customer_id}/profile",
        headers=HEADERS,
        json=update_data
    )

    print_response(response)

    if response.status_code == 200:
        data = response.json()
        print(f"✅ 更新档案成功")
        print(f"   颜色偏好: {data.get('color_preferences')}")
        print(f"   风格偏好: {data.get('style_preferences')}")
    else:
        print("❌ 更新档案失败")


def test_get_customer_with_profile():
    """测试获取客户（含档案）"""
    print_section("测试10: 获取客户详情（含档案）")

    if not test_customer_id:
        print("⚠️ 跳过：没有可用的客户ID")
        return

    response = requests.get(
        f"{BASE_URL}/customers/{test_customer_id}",
        headers=HEADERS
    )

    print_response(response)

    if response.status_code == 200:
        data = response.json()
        has_profile = data.get("profile") is not None
        print(f"✅ 获取成功! {'包含档案' if has_profile else '无档案'}")
    else:
        print("❌ 获取失败")


def test_delete_customer():
    """测试删除客户（软删除）"""
    print_section("测试11: 删除客户（软删除）")

    if not test_customer_id:
        print("⚠️ 跳过：没有可用的客户ID")
        return

    response = requests.delete(
        f"{BASE_URL}/customers/{test_customer_id}",
        headers=HEADERS
    )

    print_response(response, show_json=False)

    if response.status_code == 204:
        print("✅ 删除成功（软删除）")

        # 验证客户是否被标记为不活跃
        print("\n验证客户状态...")
        get_response = requests.get(
            f"{BASE_URL}/customers/{test_customer_id}",
            headers=HEADERS
        )

        if get_response.status_code == 200:
            data = get_response.json()
            print(f"   is_active: {data.get('is_active')}")
            if not data.get("is_active"):
                print("   ✅ 客户已被标记为不活跃")
            else:
                print("   ⚠️ 客户仍处于活跃状态")
    else:
        print("❌ 删除失败")


def test_filter_inactive_customers():
    """测试过滤不活跃客户"""
    print_section("测试12: 过滤不活跃客户")

    # 获取活跃客户
    print("\n获取活跃客户...")
    response = requests.get(
        f"{BASE_URL}/customers",
        headers=HEADERS,
        params={"is_active": True}
    )

    if response.status_code == 200:
        data = response.json()
        print(f"   活跃客户数: {data['total']}")

    # 获取不活跃客户
    print("\n获取不活跃客户...")
    response = requests.get(
        f"{BASE_URL}/customers",
        headers=HEADERS,
        params={"is_active": False}
    )

    if response.status_code == 200:
        data = response.json()
        print(f"   不活跃客户数: {data['total']}")
        print("✅ 过滤功能正常")
    else:
        print("❌ 过滤失败")


def main():
    print("\n" + "=" * 60)
    print("  客户管理 API 测试套件")
    print("=" * 60)
    print("确保后端服务正在运行: uvicorn app.main:app --reload")
    print("=" * 60)

    try:
        # 测试服务健康
        if not test_health_check():
            print("\n❌ 后端服务未运行，请先启动服务")
            return

        # 执行所有测试
        test_create_customer()
        test_create_duplicate_phone()
        test_get_customer_list()
        test_search_customers()
        test_get_customer_detail()
        test_update_customer()
        test_create_customer_profile()
        test_get_customer_profile()
        test_update_customer_profile()
        test_get_customer_with_profile()
        test_delete_customer()
        test_filter_inactive_customers()

        print("\n" + "=" * 60)
        print("  测试完成！")
        print("=" * 60)
        print("\n提示:")
        print("  - 访问 http://localhost:8000/docs 查看完整API文档")
        print("  - 数据库中现在有测试客户数据（含档案）")

    except requests.exceptions.ConnectionError:
        print("\n❌ 无法连接到后端服务，请确保服务正在运行")
        print("   运行: cd backend && uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
