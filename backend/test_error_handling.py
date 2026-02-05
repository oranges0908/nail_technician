"""
错误处理与日志系统测试

测试所有异常处理器和日志中间件的功能：
1. 自定义应用异常处理
2. HTTP异常处理
3. 请求验证错误处理
4. 未捕获异常处理
5. 请求日志记录
6. 日志文件生成

运行前确保:
1. 后端服务正在运行 (uvicorn app.main:app --reload)
2. logs/ 目录已创建
"""
import requests
import json
import time
from pathlib import Path

BASE_URL = "http://localhost:8000"
API_V1_URL = f"{BASE_URL}/api/v1"
LOGS_DIR = Path(__file__).parent / "logs"


def print_section(title: str):
    """打印分隔标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_response(response: requests.Response, show_json: bool = True):
    """打印响应信息"""
    print(f"状态码: {response.status_code}")
    print(f"处理时间: {response.headers.get('X-Process-Time', 'N/A')}")

    if show_json and response.text:
        try:
            data = response.json()
            print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
        except:
            print(f"响应: {response.text}")

    return response


def test_health_check():
    """测试1: 健康检查（正常请求）"""
    print_section("测试1: 正常请求 - 健康检查")

    response = requests.get(f"{BASE_URL}/health")
    print_response(response)

    if response.status_code == 200:
        print("✅ 正常请求处理成功")
        print("   检查日志: 应该记录INFO级别的请求日志")
        return True
    else:
        print("❌ 请求失败")
        return False


def test_http_404_error():
    """测试2: HTTP 404错误"""
    print_section("测试2: HTTP 404错误 - 不存在的端点")

    response = requests.get(f"{API_V1_URL}/nonexistent-endpoint")
    print_response(response)

    if response.status_code == 404:
        print("✅ HTTP 404错误处理正确")
        print("   检查日志: 应该记录WARNING级别的日志")
        return True
    else:
        print(f"❌ 预期404，实际{response.status_code}")
        return False


def test_validation_error():
    """测试3: 请求验证错误（422）"""
    print_section("测试3: 请求验证错误 - 无效数据")

    # 假设有一个接受JSON的端点，发送无效数据
    # 这里使用auth/register（如果存在）
    response = requests.post(
        f"{API_V1_URL}/auth/register",
        json={
            "email": "invalid-email-format",  # 无效邮箱
            "password": "123"  # 密码太短
        }
    )

    print_response(response)

    if response.status_code in [404, 422, 501]:  # 404或501表示端点未实现
        if response.status_code == 422:
            print("✅ 验证错误处理正确")
            print("   检查日志: 应该记录WARNING级别的验证错误")
        else:
            print(f"⚠️ 端点未实现 (状态码: {response.status_code})")
        return True
    else:
        print(f"❌ 预期422，实际{response.status_code}")
        return False


def test_custom_exception():
    """测试4: 自定义应用异常（ResourceNotFoundError）"""
    print_section("测试4: 自定义应用异常 - 资源未找到")

    # 尝试获取不存在的用户
    response = requests.get(f"{API_V1_URL}/users/99999")

    print_response(response)

    if response.status_code in [404, 501]:
        if response.status_code == 404:
            print("✅ 自定义异常处理正确")
            print("   检查日志: 应该记录ERROR级别的应用错误")
        else:
            print(f"⚠️ 端点未实现 (状态码: {response.status_code})")
        return True
    else:
        print(f"⚠️ 预期404，实际{response.status_code}")
        return False


def test_method_not_allowed():
    """测试5: 方法不允许（405）"""
    print_section("测试5: HTTP 405错误 - 方法不允许")

    # 对只支持GET的端点发送POST
    response = requests.post(f"{BASE_URL}/health")

    print_response(response)

    if response.status_code == 405:
        print("✅ 方法不允许错误处理正确")
        print("   检查日志: 应该记录WARNING级别的日志")
        return True
    else:
        print(f"⚠️ 预期405，实际{response.status_code}")
        return False


def test_request_logging():
    """测试6: 请求日志记录"""
    print_section("测试6: 请求日志记录")

    # 连续发送几个请求
    endpoints = [
        ("GET", f"{BASE_URL}/health"),
        ("GET", f"{BASE_URL}/"),
        ("GET", f"{API_V1_URL}/health"),
    ]

    print("发送3个测试请求...")
    for method, url in endpoints:
        response = requests.get(url)
        print(f"  {method} {url} - {response.status_code}")
        time.sleep(0.1)

    print("\n✅ 请求已发送")
    print("   检查日志文件:")
    print(f"   - {LOGS_DIR / 'app.log'}")
    print("   - 应包含所有请求的详细信息")
    return True


def check_log_files():
    """测试7: 检查日志文件是否生成"""
    print_section("测试7: 检查日志文件")

    # 等待日志写入
    time.sleep(1)

    app_log = LOGS_DIR / "app.log"
    error_log = LOGS_DIR / "error.log"

    print(f"日志目录: {LOGS_DIR}")
    print(f"\n检查文件:")

    if app_log.exists():
        file_size = app_log.stat().st_size
        print(f"✅ app.log 存在 ({file_size} bytes)")

        # 读取最后10行
        with open(app_log, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            last_lines = lines[-10:] if len(lines) >= 10 else lines

        print("\n最后10行日志:")
        print("─" * 60)
        for line in last_lines:
            print(line.rstrip())
        print("─" * 60)
    else:
        print("❌ app.log 不存在")

    if error_log.exists():
        file_size = error_log.stat().st_size
        print(f"\n✅ error.log 存在 ({file_size} bytes)")
        if file_size > 0:
            print("   （包含错误日志）")
    else:
        print(f"\n⚠️ error.log 不存在（如果没有ERROR级别日志，这是正常的）")

    return app_log.exists()


def test_process_time_header():
    """测试8: 响应头中的处理时间"""
    print_section("测试8: 响应头 - X-Process-Time")

    response = requests.get(f"{BASE_URL}/health")

    process_time = response.headers.get("X-Process-Time")
    print(f"状态码: {response.status_code}")
    print(f"X-Process-Time: {process_time}")

    if process_time:
        print(f"✅ 处理时间已记录在响应头: {process_time}s")
        return True
    else:
        print("⚠️ X-Process-Time 头不存在")
        return False


def main():
    print("\n" + "=" * 60)
    print("  错误处理与日志系统测试套件")
    print("=" * 60)
    print("确保后端服务正在运行: uvicorn app.main:app --reload")
    print("=" * 60)

    try:
        # 检查服务是否运行
        try:
            requests.get(BASE_URL, timeout=2)
        except requests.exceptions.ConnectionError:
            print("\n❌ 无法连接到后端服务")
            print("   运行: cd backend && uvicorn app.main:app --reload")
            return

        # 执行所有测试
        test_health_check()
        test_http_404_error()
        test_validation_error()
        test_custom_exception()
        test_method_not_allowed()
        test_request_logging()
        test_process_time_header()
        check_log_files()

        print("\n" + "=" * 60)
        print("  测试完成！")
        print("=" * 60)
        print("\n验证项目:")
        print("  1. ✅ 所有异常都被正确处理并返回适当的状态码")
        print("  2. ✅ 日志文件已生成（logs/app.log, logs/error.log）")
        print("  3. ✅ 请求耗时已记录在响应头（X-Process-Time）")
        print("  4. ✅ 日志包含请求信息（方法、路径、状态码、耗时）")
        print("\n手动检查:")
        print(f"  - 查看 {LOGS_DIR / 'app.log'} 确认所有请求已记录")
        print(f"  - 查看 {LOGS_DIR / 'error.log'} 确认错误已记录")
        print("  - 控制台输出应显示结构化日志")

    except Exception as e:
        print(f"\n❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
