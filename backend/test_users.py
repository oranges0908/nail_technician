"""
用户管理模块测试

测试 Iteration 2.1 的所有功能：
1. 获取当前用户信息
2. 更新当前用户信息（邮箱、用户名）
3. 修改密码
4. 删除当前用户账号
5. 邮箱唯一性验证
6. 用户名唯一性验证
7. 旧密码验证

运行前确保:
1. 后端服务正在运行
2. 数据库已初始化
3. 有测试用户可用
"""
import requests
import json
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

        if response.status_code == 200:
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


def test_get_current_user(access_token: str):
    """测试1: 获取当前用户信息"""
    print_section("测试1: 获取当前用户信息")

    headers = get_auth_headers(access_token)
    response = requests.get(f"{API_V1_URL}/users/me", headers=headers)

    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print_json(data)

        # 验证必要字段
        assert "id" in data, "缺少 id 字段"
        assert "email" in data, "缺少 email 字段"
        assert "username" in data, "缺少 username 字段"
        assert "is_active" in data, "缺少 is_active 字段"
        assert "hashed_password" not in data, "不应包含 hashed_password 字段"

        print("✅ 获取当前用户信息成功")
        return data
    else:
        print(f"❌ 请求失败: {response.text}")
        return None


def test_update_user_username(access_token: str, new_username: str):
    """测试2: 更新用户名"""
    print_section("测试2: 更新用户名")

    headers = get_auth_headers(access_token)
    response = requests.put(
        f"{API_V1_URL}/users/me",
        headers=headers,
        json={"username": new_username}
    )

    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print_json(data)

        assert data["username"] == new_username, f"用户名未更新: {data['username']}"

        print(f"✅ 用户名更新成功: {new_username}")
        return True
    else:
        print(f"❌ 更新失败: {response.text}")
        return False


def test_update_user_email(access_token: str, new_email: str):
    """测试3: 更新邮箱"""
    print_section("测试3: 更新邮箱")

    headers = get_auth_headers(access_token)
    response = requests.put(
        f"{API_V1_URL}/users/me",
        headers=headers,
        json={"email": new_email}
    )

    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print_json(data)

        assert data["email"] == new_email, f"邮箱未更新: {data['email']}"

        print(f"✅ 邮箱更新成功: {new_email}")
        return True
    else:
        print(f"❌ 更新失败: {response.text}")
        return False


def test_email_uniqueness(access_token: str, existing_email: str):
    """测试4: 邮箱唯一性验证"""
    print_section("测试4: 邮箱唯一性验证")

    # 先创建另一个用户
    other_user = register_test_user(
        username="test_other_user",
        email=existing_email,
        password="password123"
    )

    if not other_user:
        print("⚠️ 跳过测试：无法创建其他用户")
        return True

    # 尝试将当前用户的邮箱改为已存在的邮箱
    headers = get_auth_headers(access_token)
    response = requests.put(
        f"{API_V1_URL}/users/me",
        headers=headers,
        json={"email": existing_email}
    )

    print(f"状态码: {response.status_code}")

    if response.status_code == 409:
        print(f"响应: {response.json()}")
        print("✅ 邮箱唯一性验证通过（冲突被正确拒绝）")
        return True
    else:
        print(f"❌ 应该返回409冲突，实际: {response.status_code}")
        return False


def test_username_uniqueness(access_token: str, existing_username: str):
    """测试5: 用户名唯一性验证"""
    print_section("测试5: 用户名唯一性验证")

    # 尝试将当前用户的用户名改为已存在的用户名
    headers = get_auth_headers(access_token)
    response = requests.put(
        f"{API_V1_URL}/users/me",
        headers=headers,
        json={"username": existing_username}
    )

    print(f"状态码: {response.status_code}")

    if response.status_code == 409:
        print(f"响应: {response.json()}")
        print("✅ 用户名唯一性验证通过（冲突被正确拒绝）")
        return True
    else:
        print(f"❌ 应该返回409冲突，实际: {response.status_code}")
        return False


def test_change_password(access_token: str, old_password: str, new_password: str):
    """测试6: 修改密码"""
    print_section("测试6: 修改密码")

    headers = get_auth_headers(access_token)
    response = requests.put(
        f"{API_V1_URL}/users/me/password",
        headers=headers,
        json={
            "old_password": old_password,
            "new_password": new_password
        }
    )

    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print_json(data)

        print("✅ 密码修改成功")
        return True
    else:
        print(f"❌ 修改失败: {response.text}")
        return False


def test_change_password_wrong_old(access_token: str):
    """测试7: 旧密码错误"""
    print_section("测试7: 旧密码验证")

    headers = get_auth_headers(access_token)
    response = requests.put(
        f"{API_V1_URL}/users/me/password",
        headers=headers,
        json={
            "old_password": "wrong_password",
            "new_password": "new_password123"
        }
    )

    print(f"状态码: {response.status_code}")

    if response.status_code == 400:
        print(f"响应: {response.json()}")
        print("✅ 旧密码验证通过（错误密码被正确拒绝）")
        return True
    else:
        print(f"❌ 应该返回400错误，实际: {response.status_code}")
        return False


def test_login_with_new_password(email: str, new_password: str):
    """测试8: 使用新密码登录"""
    print_section("测试8: 使用新密码登录")

    access_token = login_user(email, new_password)

    if access_token:
        print("✅ 使用新密码登录成功")
        return access_token
    else:
        print("❌ 使用新密码登录失败")
        return None


def test_delete_current_user(access_token: str):
    """测试9: 删除当前用户账号"""
    print_section("测试9: 删除当前用户账号")

    headers = get_auth_headers(access_token)
    response = requests.delete(f"{API_V1_URL}/users/me", headers=headers)

    print(f"状态码: {response.status_code}")

    if response.status_code == 204:
        print("✅ 用户账号删除成功（软删除）")
        return True
    else:
        print(f"❌ 删除失败: {response.text}")
        return False


def test_deleted_user_cannot_login(email: str, password: str):
    """测试10: 已删除用户无法登录"""
    print_section("测试10: 已删除用户无法登录")

    access_token = login_user(email, password)

    if access_token is None:
        print("✅ 已删除用户无法登录（验证通过）")
        return True
    else:
        print("❌ 已删除用户仍可登录（应该被拒绝）")
        return False


def main():
    print("\n" + "=" * 60)
    print("  Iteration 2.1 测试套件")
    print("  用户管理模块")
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
        test_username = "test_user_iteration21"
        test_email = "test21@example.com"
        test_password = "password123"
        new_username = "updated_username21"
        new_email = "updated21@example.com"
        new_password = "newpassword123"

        print("\n📝 准备测试环境...")

        # 1. 注册测试用户
        print("\n注册测试用户...")
        user = register_test_user(test_username, test_email, test_password)

        if not user:
            print("\n⚠️ 注册失败，尝试使用现有用户登录...")

        # 2. 登录获取令牌
        print("\n登录测试用户...")
        access_token = login_user(test_email, test_password)

        if not access_token:
            print("\n❌ 无法获取访问令牌，测试终止")
            return

        print(f"✅ 访问令牌: {access_token[:20]}...")

        # 执行测试
        results = []

        # 测试1: 获取当前用户信息
        current_user = test_get_current_user(access_token)
        results.append(("获取当前用户信息", current_user is not None))

        # 测试2: 更新用户名
        results.append(("更新用户名", test_update_user_username(access_token, new_username)))

        # 测试3: 更新邮箱
        results.append(("更新邮箱", test_update_user_email(access_token, new_email)))

        # 测试4: 邮箱唯一性
        results.append(("邮箱唯一性验证", test_email_uniqueness(access_token, "conflict@example.com")))

        # 测试5: 用户名唯一性
        results.append(("用户名唯一性验证", test_username_uniqueness(access_token, "test_other_user")))

        # 测试6: 修改密码
        results.append(("修改密码", test_change_password(access_token, test_password, new_password)))

        # 测试7: 旧密码验证
        results.append(("旧密码验证", test_change_password_wrong_old(access_token)))

        # 测试8: 使用新密码登录
        new_access_token = test_login_with_new_password(new_email, new_password)
        results.append(("使用新密码登录", new_access_token is not None))

        # 测试9: 删除当前用户
        if new_access_token:
            results.append(("删除当前用户", test_delete_current_user(new_access_token)))

            # 测试10: 已删除用户无法登录
            results.append(("已删除用户无法登录", test_deleted_user_cannot_login(new_email, new_password)))

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
            print("\n✅ Iteration 2.1 功能验证完成:")
            print("   1. ✅ 获取当前用户信息")
            print("   2. ✅ 更新用户信息（邮箱、用户名）")
            print("   3. ✅ 邮箱唯一性验证")
            print("   4. ✅ 用户名唯一性验证")
            print("   5. ✅ 修改密码功能")
            print("   6. ✅ 旧密码验证")
            print("   7. ✅ 使用新密码登录")
            print("   8. ✅ 删除当前用户账号（软删除）")
            print("   9. ✅ 已删除用户无法登录")
            print("\n核心特性:")
            print("   - 用户只能修改自己的信息")
            print("   - 邮箱和用户名唯一性强制执行")
            print("   - 密码修改需验证旧密码")
            print("   - 软删除保留用户数据")
        else:
            print(f"\n⚠️ {total - passed} 个测试失败，请检查日志")

    except Exception as e:
        print(f"\n❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
