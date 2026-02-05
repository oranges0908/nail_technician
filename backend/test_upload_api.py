"""
文件上传 API 测试

测试所有文件上传相关功能：
1. 上传客户指甲照片
2. 上传灵感图
3. 上传设计图
4. 上传实际完成图
5. 批量上传
6. 文件验证（类型、大小）
7. 文件删除

运行前确保:
1. 后端服务正在运行 (uvicorn app.main:app --reload)
2. 数据库已初始化
3. 已有测试用户（或运行 test_auth_api.py 创建）
"""
import requests
import json
import io
from PIL import Image

BASE_URL = "http://localhost:8000/api/v1"

# 全局变量
test_access_token = None
uploaded_files = []  # 存储上传的文件信息，用于后续删除


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


def create_test_image(filename: str, format: str = "JPEG") -> io.BytesIO:
    """
    创建测试图片

    Args:
        filename: 文件名
        format: 图片格式（JPEG, PNG, GIF, WebP）

    Returns:
        BytesIO: 图片字节流
    """
    # 创建一个简单的测试图片（100x100像素，红色背景）
    img = Image.new('RGB', (100, 100), color='red')

    # 保存到字节流
    img_bytes = io.BytesIO()
    img.save(img_bytes, format=format)
    img_bytes.seek(0)
    img_bytes.name = filename  # 设置文件名

    return img_bytes


def create_large_test_image(filename: str) -> io.BytesIO:
    """创建大于10MB的测试图片（用于测试文件大小限制）"""
    # 创建一个3000x3000像素的图片（约9MB）
    img = Image.new('RGB', (4000, 4000), color='blue')

    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG', quality=100)
    img_bytes.seek(0)
    img_bytes.name = filename

    return img_bytes


def login_test_user():
    """登录测试用户获取 token"""
    global test_access_token

    print_section("前置步骤: 登录测试用户")

    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={
            "username": "testuser_updated",  # 使用 test_auth_api 创建的用户
            "password": "newpassword123"
        }
    )

    if response.status_code == 200:
        data = response.json()
        test_access_token = data["access_token"]
        print(f"✅ 登录成功! Access Token: {test_access_token[:50]}...")
        return True
    else:
        print(f"❌ 登录失败: {response.status_code}")
        print("提示: 请先运行 test_auth_api.py 创建测试用户")
        return False


def test_upload_nail_photo():
    """测试上传客户指甲照片"""
    global uploaded_files

    print_section("测试1: 上传客户指甲照片")

    # 创建测试图片
    test_image = create_test_image("test_nail.jpg", "JPEG")

    response = requests.post(
        f"{BASE_URL}/uploads/nails",
        headers={"Authorization": f"Bearer {test_access_token}"},
        files={"file": ("test_nail.jpg", test_image, "image/jpeg")}
    )

    print_response(response)

    if response.status_code == 201:
        data = response.json()
        uploaded_files.append({"category": "nails", "filename": data["filename"]})
        print(f"✅ 上传成功!")
        print(f"   文件名: {data['filename']}")
        print(f"   URL: {data['file_url']}")
        print(f"   大小: {data['file_size']} bytes")
        return True
    else:
        print("❌ 上传失败")
        return False


def test_upload_inspiration():
    """测试上传灵感图"""
    global uploaded_files

    print_section("测试2: 上传灵感参考图")

    test_image = create_test_image("inspiration.png", "PNG")

    response = requests.post(
        f"{BASE_URL}/uploads/inspirations",
        headers={"Authorization": f"Bearer {test_access_token}"},
        files={"file": ("inspiration.png", test_image, "image/png")}
    )

    print_response(response)

    if response.status_code == 201:
        data = response.json()
        uploaded_files.append({"category": "inspirations", "filename": data["filename"]})
        print(f"✅ 上传成功! URL: {data['file_url']}")
        return True
    else:
        print("❌ 上传失败")
        return False


def test_upload_design():
    """测试上传设计图"""
    global uploaded_files

    print_section("测试3: 上传设计图")

    test_image = create_test_image("design.webp", "WebP")

    response = requests.post(
        f"{BASE_URL}/uploads/designs",
        headers={"Authorization": f"Bearer {test_access_token}"},
        files={"file": ("design.webp", test_image, "image/webp")}
    )

    print_response(response)

    if response.status_code == 201:
        data = response.json()
        uploaded_files.append({"category": "designs", "filename": data["filename"]})
        print(f"✅ 上传成功! URL: {data['file_url']}")
        return True
    else:
        print("❌ 上传失败")
        return False


def test_upload_actual():
    """测试上传实际完成图"""
    global uploaded_files

    print_section("测试4: 上传实际完成图")

    test_image = create_test_image("actual.jpg", "JPEG")

    response = requests.post(
        f"{BASE_URL}/uploads/actuals",
        headers={"Authorization": f"Bearer {test_access_token}"},
        files={"file": ("actual.jpg", test_image, "image/jpeg")}
    )

    print_response(response)

    if response.status_code == 201:
        data = response.json()
        uploaded_files.append({"category": "actuals", "filename": data["filename"]})
        print(f"✅ 上传成功! URL: {data['file_url']}")
        return True
    else:
        print("❌ 上传失败")
        return False


def test_upload_invalid_type():
    """测试上传不支持的文件类型（应该失败）"""
    print_section("测试5: 上传不支持的文件类型（应该失败）")

    # 创建一个文本文件伪装成图片
    fake_file = io.BytesIO(b"This is not an image")
    fake_file.name = "fake.txt"

    response = requests.post(
        f"{BASE_URL}/uploads/nails",
        headers={"Authorization": f"Bearer {test_access_token}"},
        files={"file": ("fake.txt", fake_file, "text/plain")}
    )

    print_response(response)

    if response.status_code == 400:
        print("✅ 正确拒绝了不支持的文件类型")
        return True
    else:
        print("❌ 应该返回 400 Bad Request")
        return False


def test_upload_large_file():
    """测试上传过大的文件（应该失败）"""
    print_section("测试6: 上传过大的文件（应该失败）")

    # 创建大于10MB的图片
    large_image = create_large_test_image("large.jpg")

    response = requests.post(
        f"{BASE_URL}/uploads/nails",
        headers={"Authorization": f"Bearer {test_access_token}"},
        files={"file": ("large.jpg", large_image, "image/jpeg")}
    )

    print_response(response)

    if response.status_code == 413:
        print("✅ 正确拒绝了过大的文件")
        return True
    else:
        print(f"⚠️ 预期返回 413，实际返回 {response.status_code}")
        print("   （如果文件未超过10MB，此测试可能失败）")
        return False


def test_batch_upload():
    """测试批量上传"""
    global uploaded_files

    print_section("测试7: 批量上传")

    # 创建3个测试图片
    files = [
        ("files", ("batch1.jpg", create_test_image("batch1.jpg", "JPEG"), "image/jpeg")),
        ("files", ("batch2.png", create_test_image("batch2.png", "PNG"), "image/png")),
        ("files", ("batch3.webp", create_test_image("batch3.webp", "WebP"), "image/webp")),
    ]

    response = requests.post(
        f"{BASE_URL}/uploads/batch/nails",
        headers={"Authorization": f"Bearer {test_access_token}"},
        files=files
    )

    print_response(response)

    if response.status_code == 201:
        data = response.json()
        print(f"✅ 批量上传完成!")
        print(f"   成功: {data['success_count']}/{data['total_count']}")
        print(f"   失败: {data['failed_count']}")

        # 保存上传的文件信息
        for file_info in data["uploaded_files"]:
            uploaded_files.append({"category": "nails", "filename": file_info["filename"]})

        return True
    else:
        print("❌ 批量上传失败")
        return False


def test_upload_without_auth():
    """测试无认证上传（应该失败）"""
    print_section("测试8: 无认证上传（应该失败）")

    test_image = create_test_image("noauth.jpg", "JPEG")

    response = requests.post(
        f"{BASE_URL}/uploads/nails",
        files={"file": ("noauth.jpg", test_image, "image/jpeg")}
    )

    print_response(response)

    if response.status_code == 401:
        print("✅ 正确拒绝了无认证请求")
        return True
    else:
        print("❌ 应该返回 401 Unauthorized")
        return False


def test_delete_file():
    """测试删除文件"""
    print_section("测试9: 删除文件")

    if not uploaded_files:
        print("⚠️ 跳过：没有可删除的文件")
        return False

    # 删除第一个上传的文件
    file_to_delete = uploaded_files[0]
    category = file_to_delete["category"]
    filename = file_to_delete["filename"]

    response = requests.delete(
        f"{BASE_URL}/uploads/{category}/{filename}",
        headers={"Authorization": f"Bearer {test_access_token}"}
    )

    print(f"删除文件: {category}/{filename}")
    print(f"状态码: {response.status_code}")

    if response.status_code == 204:
        print(f"✅ 文件删除成功")
        uploaded_files.pop(0)  # 从列表中移除
        return True
    else:
        print_response(response)
        print("❌ 删除失败")
        return False


def cleanup_uploaded_files():
    """清理测试过程中上传的所有文件"""
    print_section("清理: 删除所有测试文件")

    deleted_count = 0
    failed_count = 0

    for file_info in uploaded_files:
        category = file_info["category"]
        filename = file_info["filename"]

        response = requests.delete(
            f"{BASE_URL}/uploads/{category}/{filename}",
            headers={"Authorization": f"Bearer {test_access_token}"}
        )

        if response.status_code == 204:
            deleted_count += 1
            print(f"✅ 删除: {category}/{filename}")
        else:
            failed_count += 1
            print(f"❌ 删除失败: {category}/{filename}")

    print(f"\n清理完成: 删除 {deleted_count} 个文件，失败 {failed_count} 个")


def main():
    print("\n" + "=" * 60)
    print("  文件上传 API 测试套件")
    print("=" * 60)
    print("确保后端服务正在运行: uvicorn app.main:app --reload")
    print("=" * 60)

    try:
        # 登录获取 token
        if not login_test_user():
            return

        # 执行所有测试
        test_upload_nail_photo()
        test_upload_inspiration()
        test_upload_design()
        test_upload_actual()
        test_upload_invalid_type()
        test_upload_large_file()
        test_batch_upload()
        test_upload_without_auth()
        test_delete_file()

        # 清理测试文件
        cleanup_uploaded_files()

        print("\n" + "=" * 60)
        print("  测试完成！")
        print("=" * 60)
        print("\n提示:")
        print("  - 访问 http://localhost:8000/docs 查看完整API文档")
        print("  - 上传的文件保存在 backend/uploads/ 目录")
        print("  - 可通过 http://localhost:8000/uploads/{category}/{filename} 访问")

    except requests.exceptions.ConnectionError:
        print("\n❌ 无法连接到后端服务，请确保服务正在运行")
        print("   运行: cd backend && uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
