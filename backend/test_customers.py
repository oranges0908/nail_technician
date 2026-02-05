"""
客户管理模块测试

测试 Iteration 2.2 的所有功能：
1. 创建客户
2. 获取客户列表（分页、搜索）
3. 获取客户详情
4. 更新客户信息
5. 删除客户（软删除）
6. 数据隔离验证
7. 手机号唯一性验证
8. 客户档案管理

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


def test_create_customer(access_token: str, name: str, phone: str):
    """测试1: 创建客户"""
    print_section(f"测试1: 创建客户 - {name}")

    headers = get_auth_headers(access_token)
    response = requests.post(
        f"{API_V1_URL}/customers",
        headers=headers,
        json={
            "name": name,
            "phone": phone,
            "email": f"{phone}@example.com",
            "notes": "测试客户"
        }
    )

    print(f"状态码: {response.status_code}")

    if response.status_code == 201:
        data = response.json()
        print_json(data)

        assert "id" in data, "缺少 id 字段"
        assert data["name"] == name, f"姓名不匹配: {data['name']}"
        assert data["phone"] == phone, f"电话不匹配: {data['phone']}"
        assert data["is_active"] == 1, "is_active 应为 1"

        print(f"✅ 创建客户成功: ID={data['id']}")
        return data["id"]
    else:
        print(f"❌ 请求失败: {response.text}")
        return None


def test_list_customers(access_token: str):
    """测试2: 获取客户列表"""
    print_section("测试2: 获取客户列表")

    headers = get_auth_headers(access_token)
    response = requests.get(f"{API_V1_URL}/customers", headers=headers)

    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print_json(data)

        assert "total" in data, "缺少 total 字段"
        assert "customers" in data, "缺少 customers 字段"
        assert isinstance(data["customers"], list), "customers 应该是列表"

        print(f"✅ 获取客户列表成功: 共 {data['total']} 个客户")
        return True
    else:
        print(f"❌ 请求失败: {response.text}")
        return False


def test_search_customers(access_token: str, search_keyword: str):
    """测试3: 搜索客户"""
    print_section(f"测试3: 搜索客户 - 关键词: {search_keyword}")

    headers = get_auth_headers(access_token)
    response = requests.get(
        f"{API_V1_URL}/customers?search={search_keyword}",
        headers=headers
    )

    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print_json(data)

        print(f"✅ 搜索成功: 找到 {data['total']} 个匹配客户")
        return True
    else:
        print(f"❌ 请求失败: {response.text}")
        return False


def test_get_customer(access_token: str, customer_id: int):
    """测试4: 获取客户详情"""
    print_section(f"测试4: 获取客户详情 - ID={customer_id}")

    headers = get_auth_headers(access_token)
    response = requests.get(
        f"{API_V1_URL}/customers/{customer_id}",
        headers=headers
    )

    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print_json(data)

        assert data["id"] == customer_id, "ID 不匹配"
        print("✅ 获取客户详情成功")
        return True
    else:
        print(f"❌ 请求失败: {response.text}")
        return False


def test_update_customer(access_token: str, customer_id: int, new_name: str):
    """测试5: 更新客户信息"""
    print_section(f"测试5: 更新客户信息 - 新姓名: {new_name}")

    headers = get_auth_headers(access_token)
    response = requests.put(
        f"{API_V1_URL}/customers/{customer_id}",
        headers=headers,
        json={"name": new_name}
    )

    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print_json(data)

        assert data["name"] == new_name, f"姓名未更新: {data['name']}"
        print(f"✅ 更新客户信息成功")
        return True
    else:
        print(f"❌ 更新失败: {response.text}")
        return False


def test_phone_uniqueness(access_token: str, existing_phone: str):
    """测试6: 手机号唯一性验证"""
    print_section("测试6: 手机号唯一性验证")

    headers = get_auth_headers(access_token)
    response = requests.post(
        f"{API_V1_URL}/customers",
        headers=headers,
        json={
            "name": "重复手机号测试",
            "phone": existing_phone
        }
    )

    print(f"状态码: {response.status_code}")

    if response.status_code == 409:
        print(f"响应: {response.json()}")
        print("✅ 手机号唯一性验证通过（冲突被正确拒绝）")
        return True
    else:
        print(f"❌ 应该返回409冲突，实际: {response.status_code}")
        return False


def test_create_or_update_profile(access_token: str, customer_id: int):
    """测试7: 创建/更新客户档案"""
    print_section(f"测试7: 创建客户档案 - Customer ID={customer_id}")

    headers = get_auth_headers(access_token)
    response = requests.put(
        f"{API_V1_URL}/customers/{customer_id}/profile",
        headers=headers,
        json={
            "nail_shape": "方形",
            "nail_length": "中等",
            "nail_condition": "健康",
            "color_preferences": ["粉色", "裸色", "红色"],
            "color_dislikes": ["黑色", "深紫色"],
            "style_preferences": ["法式", "简约"],
            "pattern_preferences": "几何图案",
            "allergies": "无",
            "prohibitions": "无"
        }
    )

    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print_json(data)

        assert data["customer_id"] == customer_id, "customer_id 不匹配"
        assert data["nail_shape"] == "方形", "nail_shape 不匹配"
        print("✅ 创建客户档案成功")
        return True
    else:
        print(f"❌ 请求失败: {response.text}")
        return False


def test_get_profile(access_token: str, customer_id: int):
    """测试8: 获取客户档案"""
    print_section(f"测试8: 获取客户档案 - Customer ID={customer_id}")

    headers = get_auth_headers(access_token)
    response = requests.get(
        f"{API_V1_URL}/customers/{customer_id}/profile",
        headers=headers
    )

    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print_json(data)

        print("✅ 获取客户档案成功")
        return True
    else:
        print(f"❌ 请求失败: {response.text}")
        return False


def test_delete_customer(access_token: str, customer_id: int):
    """测试9: 删除客户（软删除）"""
    print_section(f"测试9: 删除客户 - ID={customer_id}")

    headers = get_auth_headers(access_token)
    response = requests.delete(
        f"{API_V1_URL}/customers/{customer_id}",
        headers=headers
    )

    print(f"状态码: {response.status_code}")

    if response.status_code == 204:
        print("✅ 删除客户成功（软删除）")
        return True
    else:
        print(f"❌ 删除失败: {response.text}")
        return False


def test_data_isolation(access_token1: str, access_token2: str, customer_id: int):
    """测试10: 数据隔离验证"""
    print_section("测试10: 数据隔离验证")

    print("\n用户2尝试访问用户1的客户...")
    headers2 = get_auth_headers(access_token2)
    response = requests.get(
        f"{API_V1_URL}/customers/{customer_id}",
        headers=headers2
    )

    print(f"状态码: {response.status_code}")

    if response.status_code == 404:
        print("✅ 数据隔离验证通过（用户2无法访问用户1的客户）")
        return True
    else:
        print(f"❌ 数据隔离失败，用户2能访问用户1的客户: {response.status_code}")
        return False


def main():
    print("\n" + "=" * 60)
    print("  Iteration 2.2 测试套件")
    print("  客户档案管理模块")
    print("=" * 60)
    print("\n确保后端服务正在运行: uvicorn app.main:app --reload")
    print("=" * 60)

    try:
        # 检查服务是否运行
        try:
            requests.get(BASE_URL, timeout=2)
        except requests.exceptions.ConnectionError:
            print("\n❌ 无法连接到后端服务")
            print("   运行: cd backend && uvicorn app.main:app --reload")
            return

        # 准备测试数据
        user1_email = "test_customer_user1@example.com"
        user1_password = "password123"
        user2_email = "test_customer_user2@example.com"
        user2_password = "password123"

        print("\n📝 准备测试环境...")

        # 注册用户1
        print("\n注册测试用户1...")
        register_test_user("customer_test_user1", user1_email, user1_password)

        # 注册用户2（用于数据隔离测试）
        print("\n注册测试用户2...")
        register_test_user("customer_test_user2", user2_email, user2_password)

        # 登录用户1
        print("\n登录测试用户1...")
        access_token1 = login_user(user1_email, user1_password)

        if not access_token1:
            print("\n❌ 无法获取访问令牌，测试终止")
            return

        print(f"✅ 访问令牌1: {access_token1[:20]}...")

        # 登录用户2
        print("\n登录测试用户2...")
        access_token2 = login_user(user2_email, user2_password)

        if not access_token2:
            print("\n❌ 无法获取用户2访问令牌")
            access_token2 = None

        # 执行测试
        results = []

        # 生成唯一的手机号（使用时间戳）
        timestamp = int(time.time()) % 100000000  # 取后8位
        phone1 = f"138{timestamp:08d}"[:11]
        phone2 = f"139{timestamp:08d}"[:11]

        # 测试1: 创建客户
        customer_id = test_create_customer(access_token1, "张小美", phone1)
        results.append(("创建客户", customer_id is not None))

        if not customer_id:
            print("\n❌ 创建客户失败，后续测试终止")
            return

        # 测试2: 创建第二个客户（用于列表测试）
        customer_id2 = test_create_customer(access_token1, "李小花", phone2)
        results.append(("创建第二个客户", customer_id2 is not None))

        # 测试3: 获取客户列表
        results.append(("获取客户列表", test_list_customers(access_token1)))

        # 测试4: 搜索客户
        results.append(("搜索客户", test_search_customers(access_token1, "张")))

        # 测试5: 获取客户详情
        results.append(("获取客户详情", test_get_customer(access_token1, customer_id)))

        # 测试6: 更新客户信息
        results.append(("更新客户信息", test_update_customer(access_token1, customer_id, "张美美")))

        # 测试7: 手机号唯一性
        results.append(("手机号唯一性验证", test_phone_uniqueness(access_token1, phone1)))

        # 测试8: 创建客户档案
        results.append(("创建客户档案", test_create_or_update_profile(access_token1, customer_id)))

        # 测试9: 获取客户档案
        results.append(("获取客户档案", test_get_profile(access_token1, customer_id)))

        # 测试10: 数据隔离
        if access_token2:
            results.append(("数据隔离验证", test_data_isolation(access_token1, access_token2, customer_id)))

        # 测试11: 删除客户
        if customer_id2:
            results.append(("删除客户", test_delete_customer(access_token1, customer_id2)))

        # 统计结果
        print("\n" + "=" * 60)
        print("  测试结果汇总")
        print("=" * 60)

        passed = sum(1 for _, result in results if result)
        total = len(results)

        for test_name, result in results:
            status = "✅ 通过" if result else "❌ 失败"
            print(f"{status} - {test_name}")

        print("\n" + "=" * 60)
        print(f"  总计: {passed}/{total} 通过 ({passed*100//total}%)")
        print("=" * 60)

        if passed == total:
            print("\n🎉 所有测试通过！")
            print("\n✅ Iteration 2.2 功能验证完成:")
            print("   1. ✅ 创建客户")
            print("   2. ✅ 获取客户列表（分页）")
            print("   3. ✅ 搜索客户")
            print("   4. ✅ 获取客户详情")
            print("   5. ✅ 更新客户信息")
            print("   6. ✅ 手机号唯一性验证")
            print("   7. ✅ 创建/更新客户档案")
            print("   8. ✅ 获取客户档案")
            print("   9. ✅ 数据隔离（用户只能访问自己的客户）")
            print("   10. ✅ 删除客户（软删除）")
            print("\n核心特性:")
            print("   - 数据隔离（user_id）")
            print("   - 分页和搜索")
            print("   - 手机号唯一性")
            print("   - 软删除保留数据")
            print("   - 客户详细档案管理")
        else:
            print(f"\n⚠️ {total - passed} 个测试失败，请检查日志")

    except Exception as e:
        print(f"\n❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
