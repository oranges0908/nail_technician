"""
认证与用户管理 API 测试

运行前确保:
1. 后端服务正在运行 (uvicorn app.main:app --reload)
2. 数据库已初始化
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# 全局变量存储测试数据
test_user_data = {
    "email": "testuser@example.com",
    "username": "testuser",
    "password": "password123"
}
test_access_token = None
refresh_token_str = None
test_user_id = None


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


def test_register():
    """测试用户注册"""
    global test_user_id

    print_section("测试1: 用户注册")

    response = requests.post(
        f"{BASE_URL}/auth/register",
        json=test_user_data
    )

    print_response(response)

    if response.status_code == 201:
        data = response.json()
        test_user_id = data["id"]
        print(f"✅ 注册成功! 用户ID: {test_user_id}")
        print(f"   用户名: {data['username']}")
        print(f"   邮箱: {data['email']}")
        return True
    else:
        print("❌ 注册失败")
        return False


def test_register_duplicate_email():
    """测试注册重复邮箱（应该失败）"""
    print_section("测试2: 注册重复邮箱（应该失败）")

    duplicate_data = {
        "email": test_user_data["email"],  # 重复邮箱
        "username": "anotheruser",
        "password": "password456"
    }

    response = requests.post(
        f"{BASE_URL}/auth/register",
        json=duplicate_data
    )

    print_response(response)

    if response.status_code == 409:
        print("✅ 正确拒绝了重复邮箱")
        return True
    else:
        print("❌ 应该返回 409 Conflict")
        return False


def test_register_duplicate_username():
    """测试注册重复用户名（应该失败）"""
    print_section("测试3: 注册重复用户名（应该失败）")

    duplicate_data = {
        "email": "another@example.com",
        "username": test_user_data["username"],  # 重复用户名
        "password": "password456"
    }

    response = requests.post(
        f"{BASE_URL}/auth/register",
        json=duplicate_data
    )

    print_response(response)

    if response.status_code == 409:
        print("✅ 正确拒绝了重复用户名")
        return True
    else:
        print("❌ 应该返回 409 Conflict")
        return False


def test_login():
    """测试用户登录"""
    global test_access_token, refresh_token_str

    print_section("测试4: 用户登录")

    # OAuth2PasswordRequestForm 使用 form data
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={
            "username": test_user_data["email"],  # 可以使用邮箱或用户名
            "password": test_user_data["password"]
        }
    )

    print_response(response)

    if response.status_code == 200:
        data = response.json()
        test_access_token = data["access_token"]
        refresh_token_str = data["refresh_token"]
        print("✅ 登录成功!")
        print(f"   Access Token: {test_access_token[:50]}...")
        print(f"   Refresh Token: {refresh_token_str[:50]}...")
        return True
    else:
        print("❌ 登录失败")
        return False


def test_login_wrong_password():
    """测试错误密码登录（应该失败）"""
    print_section("测试5: 错误密码登录（应该失败）")

    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={
            "username": test_user_data["email"],
            "password": "wrongpassword"
        }
    )

    print_response(response)

    if response.status_code == 401:
        print("✅ 正确拒绝了错误密码")
        return True
    else:
        print("❌ 应该返回 401 Unauthorized")
        return False


def test_get_current_user():
    """测试获取当前用户信息"""
    print_section("测试6: 获取当前用户信息")

    if not test_access_token:
        print("⚠️ 跳过：没有可用的 access token")
        return False

    response = requests.get(
        f"{BASE_URL}/users/me",
        headers={"Authorization": f"Bearer {test_access_token}"}
    )

    print_response(response)

    if response.status_code == 200:
        data = response.json()
        print("✅ 获取当前用户信息成功")
        print(f"   用户ID: {data['id']}")
        print(f"   用户名: {data['username']}")
        print(f"   邮箱: {data['email']}")
        return True
    else:
        print("❌ 获取失败")
        return False


def test_get_current_user_without_token():
    """测试无 token 获取用户信息（应该失败）"""
    print_section("测试7: 无 Token 获取用户信息（应该失败）")

    response = requests.get(f"{BASE_URL}/users/me")

    print_response(response)

    if response.status_code == 401:
        print("✅ 正确拒绝了无 token 请求")
        return True
    else:
        print("❌ 应该返回 401 Unauthorized")
        return False


def test_update_current_user():
    """测试更新当前用户信息"""
    print_section("测试8: 更新当前用户信息")

    if not test_access_token:
        print("⚠️ 跳过：没有可用的 access token")
        return False

    update_data = {
        "username": "testuser_updated"
    }

    response = requests.put(
        f"{BASE_URL}/users/me",
        headers={"Authorization": f"Bearer {test_access_token}"},
        json=update_data
    )

    print_response(response)

    if response.status_code == 200:
        data = response.json()
        print("✅ 更新成功!")
        print(f"   新用户名: {data['username']}")
        return True
    else:
        print("❌ 更新失败")
        return False


def test_change_password():
    """测试修改密码"""
    print_section("测试9: 修改密码")

    if not test_access_token:
        print("⚠️ 跳过：没有可用的 access token")
        return False

    password_data = {
        "old_password": test_user_data["password"],
        "new_password": "newpassword123"
    }

    response = requests.put(
        f"{BASE_URL}/users/me/password",
        headers={"Authorization": f"Bearer {test_access_token}"},
        json=password_data
    )

    print_response(response)

    if response.status_code == 200:
        print("✅ 修改密码成功")
        # 更新测试数据中的密码
        test_user_data["password"] = "newpassword123"
        return True
    else:
        print("❌ 修改密码失败")
        return False


def test_change_password_wrong_old():
    """测试错误的旧密码修改（应该失败）"""
    print_section("测试10: 错误的旧密码修改（应该失败）")

    if not test_access_token:
        print("⚠️ 跳过：没有可用的 access token")
        return False

    password_data = {
        "old_password": "wrongoldpassword",
        "new_password": "newpassword456"
    }

    response = requests.put(
        f"{BASE_URL}/users/me/password",
        headers={"Authorization": f"Bearer {test_access_token}"},
        json=password_data
    )

    print_response(response)

    if response.status_code == 400:
        print("✅ 正确拒绝了错误的旧密码")
        return True
    else:
        print("❌ 应该返回 400 Bad Request")
        return False


def test_refresh_token():
    """测试刷新 Access Token"""
    global test_access_token, refresh_token_str

    print_section("测试11: 刷新 Access Token")

    if not refresh_token_str:
        print("⚠️ 跳过：没有可用的 refresh token")
        return False

    response = requests.post(
        f"{BASE_URL}/auth/refresh",
        json={"refresh_token": refresh_token_str}  # JSON body
    )

    print_response(response)

    if response.status_code == 200:
        data = response.json()
        test_access_token = data["access_token"]
        print("✅ 刷新 Access Token 成功")
        print(f"   新 Access Token: {test_access_token[:50]}...")
        return True
    else:
        print("❌ 刷新失败")
        return False


def test_logout():
    """测试登出"""
    print_section("测试12: 登出")

    response = requests.post(f"{BASE_URL}/auth/logout")

    print_response(response, show_json=False)

    if response.status_code == 204:
        print("✅ 登出成功（客户端应清除 token）")
        return True
    else:
        print("❌ 登出失败")
        return False


def main():
    print("\n" + "=" * 60)
    print("  认证与用户管理 API 测试套件")
    print("=" * 60)
    print("确保后端服务正在运行: uvicorn app.main:app --reload")
    print("=" * 60)

    try:
        # 测试服务健康
        if not test_health_check():
            print("\n❌ 后端服务未运行，请先启动服务")
            return

        # 执行所有测试
        test_register()
        test_register_duplicate_email()
        test_register_duplicate_username()
        test_login()
        test_login_wrong_password()
        test_get_current_user()
        test_get_current_user_without_token()
        test_update_current_user()
        test_change_password()
        test_change_password_wrong_old()
        test_refresh_token()
        test_logout()

        print("\n" + "=" * 60)
        print("  测试完成！")
        print("=" * 60)
        print("\n提示:")
        print("  - 访问 http://localhost:8000/docs 查看完整API文档")
        print("  - 测试用户已创建并可用于后续测试")
        print(f"  - 用户名: {test_user_data['username']}")
        print(f"  - 邮箱: {test_user_data['email']}")

    except requests.exceptions.ConnectionError:
        print("\n❌ 无法连接到后端服务，请确保服务正在运行")
        print("   运行: cd backend && uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
