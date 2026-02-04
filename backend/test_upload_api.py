"""
测试文件上传 API

运行前确保:
1. 后端服务正在运行 (uvicorn app.main:app --reload)
2. 数据库已初始化，有测试用户
"""
import requests
import io
from PIL import Image

BASE_URL = "http://localhost:8000/api/v1"

# 开发模式：使用假token（因为当前get_current_user会自动返回第一个用户）
HEADERS = {
    "Authorization": "Bearer dev-token"
}


def create_test_image(color: tuple = (255, 192, 203), size: tuple = (800, 600)) -> bytes:
    """创建测试图片（PNG格式）"""
    img = Image.new('RGB', size, color)
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes.read()


def test_upload_nail_photo():
    """测试上传客户指甲照片"""
    print("\n" + "="*60)
    print("测试1: 上传客户指甲照片")
    print("="*60)

    # 创建测试图片（粉色）
    image_data = create_test_image(color=(255, 192, 203), size=(800, 600))

    files = {
        'file': ('test_nail.png', image_data, 'image/png')
    }

    response = requests.post(f"{BASE_URL}/uploads/nails", files=files, headers=HEADERS)

    print(f"状态码: {response.status_code}")
    if response.status_code == 201:
        data = response.json()
        print(f"✅ 上传成功!")
        print(f"   文件名: {data['filename']}")
        print(f"   文件路径: {data['file_path']}")
        print(f"   文件URL: {data['file_url']}")
        print(f"   文件大小: {data['file_size']} bytes")
        print(f"   上传时间: {data['uploaded_at']}")
        return data['file_url']
    else:
        print(f"❌ 上传失败: {response.text}")
        return None


def test_upload_inspiration():
    """测试上传灵感图"""
    print("\n" + "="*60)
    print("测试2: 上传灵感参考图")
    print("="*60)

    # 创建测试图片（蓝色）
    image_data = create_test_image(color=(135, 206, 250), size=(1024, 1024))

    files = {
        'file': ('inspiration_ocean.png', image_data, 'image/png')
    }

    response = requests.post(f"{BASE_URL}/uploads/inspirations", files=files, headers=HEADERS)

    print(f"状态码: {response.status_code}")
    if response.status_code == 201:
        data = response.json()
        print(f"✅ 上传成功!")
        print(f"   文件名: {data['filename']}")
        print(f"   文件URL: {data['file_url']}")
        return data['file_url']
    else:
        print(f"❌ 上传失败: {response.text}")
        return None


def test_upload_design():
    """测试上传设计图"""
    print("\n" + "="*60)
    print("测试3: 上传设计方案图")
    print("="*60)

    # 创建测试图片（紫色）
    image_data = create_test_image(color=(147, 112, 219), size=(1024, 1024))

    files = {
        'file': ('design_purple.png', image_data, 'image/png')
    }

    response = requests.post(f"{BASE_URL}/uploads/designs", files=files, headers=HEADERS)

    print(f"状态码: {response.status_code}")
    if response.status_code == 201:
        data = response.json()
        print(f"✅ 上传成功!")
        print(f"   文件URL: {data['file_url']}")
        return data['file_url']
    else:
        print(f"❌ 上传失败: {response.text}")
        return None


def test_upload_actual():
    """测试上传实际完成图"""
    print("\n" + "="*60)
    print("测试4: 上传实际完成图")
    print("="*60)

    # 创建测试图片（红色）
    image_data = create_test_image(color=(220, 20, 60), size=(1024, 1024))

    files = {
        'file': ('actual_result.png', image_data, 'image/png')
    }

    response = requests.post(f"{BASE_URL}/uploads/actuals", files=files, headers=HEADERS)

    print(f"状态码: {response.status_code}")
    if response.status_code == 201:
        data = response.json()
        print(f"✅ 上传成功!")
        print(f"   文件URL: {data['file_url']}")
        return data['file_url']
    else:
        print(f"❌ 上传失败: {response.text}")
        return None


def test_batch_upload():
    """测试批量上传"""
    print("\n" + "="*60)
    print("测试5: 批量上传灵感图")
    print("="*60)

    files = [
        ('files', ('inspiration1.png', create_test_image((255, 182, 193)), 'image/png')),
        ('files', ('inspiration2.png', create_test_image((173, 216, 230)), 'image/png')),
        ('files', ('inspiration3.png', create_test_image((221, 160, 221)), 'image/png')),
    ]

    response = requests.post(f"{BASE_URL}/uploads/batch/inspirations", files=files, headers=HEADERS)

    print(f"状态码: {response.status_code}")
    if response.status_code == 201:
        data = response.json()
        print(f"✅ 批量上传完成!")
        print(f"   总数: {data['total_count']}")
        print(f"   成功: {data['success_count']}")
        print(f"   失败: {data['failed_count']}")
        for i, file_info in enumerate(data['uploaded_files'], 1):
            print(f"   文件{i}: {file_info['filename']}")
    else:
        print(f"❌ 批量上传失败: {response.text}")


def test_invalid_file_type():
    """测试上传不支持的文件类型"""
    print("\n" + "="*60)
    print("测试6: 上传不支持的文件类型（应该失败）")
    print("="*60)

    # 创建文本文件
    files = {
        'file': ('test.txt', b'This is a text file', 'text/plain')
    }

    response = requests.post(f"{BASE_URL}/uploads/nails", files=files, headers=HEADERS)

    print(f"状态码: {response.status_code}")
    if response.status_code == 400:
        print(f"✅ 正确拒绝了不支持的文件类型")
        print(f"   错误信息: {response.json()['detail']}")
    else:
        print(f"❌ 应该拒绝但没有拒绝")


def test_file_too_large():
    """测试上传超大文件"""
    print("\n" + "="*60)
    print("测试7: 上传超大文件（应该失败）")
    print("="*60)

    # 创建超大图片（15MB）
    large_image = create_test_image(size=(5000, 5000))

    files = {
        'file': ('large_image.png', large_image, 'image/png')
    }

    response = requests.post(f"{BASE_URL}/uploads/nails", files=files, headers=HEADERS)

    print(f"状态码: {response.status_code}")
    if response.status_code == 413:
        print(f"✅ 正确拒绝了超大文件")
        print(f"   错误信息: {response.json()['detail']}")
    else:
        print(f"   状态: {response.status_code}")
        print(f"   注意: 文件大小为 {len(large_image)} bytes")


def test_static_file_access(file_url: str):
    """测试静态文件访问"""
    print("\n" + "="*60)
    print("测试8: 访问已上传的静态文件")
    print("="*60)

    if not file_url:
        print("❌ 没有可用的文件URL")
        return

    full_url = f"http://localhost:8000{file_url}"
    print(f"访问URL: {full_url}")

    response = requests.get(full_url)

    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ 静态文件访问成功!")
        print(f"   Content-Type: {response.headers.get('Content-Type')}")
        print(f"   Content-Length: {response.headers.get('Content-Length')} bytes")
    else:
        print(f"❌ 静态文件访问失败")


def main():
    print("\n" + "="*60)
    print("文件上传 API 测试套件")
    print("="*60)
    print("确保后端服务正在运行: uvicorn app.main:app --reload")
    print("="*60)

    try:
        # 测试服务是否运行
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("❌ 后端服务未运行，请先启动服务")
            return
        print("✅ 后端服务运行正常\n")

        # 执行所有测试
        file_url = test_upload_nail_photo()
        test_upload_inspiration()
        test_upload_design()
        test_upload_actual()
        test_batch_upload()
        test_invalid_file_type()
        test_file_too_large()

        if file_url:
            test_static_file_access(file_url)

        print("\n" + "="*60)
        print("测试完成！")
        print("="*60)
        print("\n提示: 可以在以下目录查看上传的文件:")
        print("  - backend/uploads/nails/")
        print("  - backend/uploads/inspirations/")
        print("  - backend/uploads/designs/")
        print("  - backend/uploads/actuals/")
        print("\n或访问 http://localhost:8000/docs 查看完整API文档")

    except requests.exceptions.ConnectionError:
        print("\n❌ 无法连接到后端服务，请确保服务正在运行")
        print("   运行: cd backend && uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ 测试过程中出错: {e}")


if __name__ == "__main__":
    main()
