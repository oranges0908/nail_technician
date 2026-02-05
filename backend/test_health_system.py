"""
健康检查与系统信息端点测试

测试 Iteration 1.5 的所有功能：
1. 基础健康检查
2. 详细健康检查（包括数据库状态）
3. 系统信息查询
4. API版本查询
5. Swagger UI文档可用性

运行前确保:
1. 后端服务正在运行 (uvicorn app.main:app --reload)
2. 数据库已初始化
"""
import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"
API_V1_URL = f"{BASE_URL}/api/v1"


def print_section(title: str):
    """打印分隔标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_json(data: Dict[Any, Any], title: str = "响应"):
    """格式化打印JSON数据"""
    print(f"\n{title}:")
    print(json.dumps(data, ensure_ascii=False, indent=2))


def test_basic_health_check():
    """测试1: 基础健康检查"""
    print_section("测试1: 基础健康检查")

    response = requests.get(f"{API_V1_URL}/health")
    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print_json(data)

        # 验证必要字段
        assert "status" in data, "缺少 status 字段"
        assert "timestamp" in data, "缺少 timestamp 字段"
        assert "service" in data, "缺少 service 字段"
        assert "version" in data, "缺少 version 字段"
        assert data["status"] == "healthy", "服务状态不是 healthy"

        print("✅ 基础健康检查通过")
        return True
    else:
        print(f"❌ 请求失败，状态码: {response.status_code}")
        return False


def test_detailed_health_check():
    """测试2: 详细健康检查（包括数据库）"""
    print_section("测试2: 详细健康检查")

    response = requests.get(f"{API_V1_URL}/health/detailed")
    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print_json(data)

        # 验证必要字段
        assert "status" in data, "缺少 status 字段"
        assert "timestamp" in data, "缺少 timestamp 字段"
        assert "checks" in data, "缺少 checks 字段"
        assert "database" in data["checks"], "缺少数据库检查"

        db_check = data["checks"]["database"]
        assert "status" in db_check, "数据库检查缺少 status"
        assert db_check["status"] == "healthy", "数据库状态不健康"

        if "response_time_ms" in db_check:
            print(f"\n数据库响应时间: {db_check['response_time_ms']} ms")

        print("✅ 详细健康检查通过")
        return True
    else:
        print(f"❌ 请求失败，状态码: {response.status_code}")
        return False


def test_system_info():
    """测试3: 系统信息"""
    print_section("测试3: 系统信息")

    response = requests.get(f"{API_V1_URL}/system/info")
    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print_json(data)

        # 验证必要字段
        assert "app" in data, "缺少 app 字段"
        assert "environment" in data, "缺少 environment 字段"
        assert "runtime" in data, "缺少 runtime 字段"
        assert "api" in data, "缺少 api 字段"

        print(f"\n应用: {data['app']['name']} v{data['app']['version']}")
        print(f"Python: {data['runtime']['python_version'].split()[0]}")
        print(f"平台: {data['runtime']['platform']}")
        print(f"数据库: {data['environment']['database']}")

        print("✅ 系统信息查询通过")
        return True
    else:
        print(f"❌ 请求失败，状态码: {response.status_code}")
        return False


def test_version():
    """测试4: API版本"""
    print_section("测试4: API版本")

    response = requests.get(f"{API_V1_URL}/system/version")
    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print_json(data)

        # 验证必要字段
        assert "name" in data, "缺少 name 字段"
        assert "version" in data, "缺少 version 字段"

        print(f"\nAPI版本: {data['version']}")
        print("✅ 版本查询通过")
        return True
    else:
        print(f"❌ 请求失败，状态码: {response.status_code}")
        return False


def test_swagger_ui():
    """测试5: Swagger UI 可访问性"""
    print_section("测试5: Swagger UI 文档")

    response = requests.get(f"{BASE_URL}/docs")
    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        print("✅ Swagger UI 可访问")
        print(f"   URL: {BASE_URL}/docs")
        return True
    else:
        print(f"❌ Swagger UI 不可访问，状态码: {response.status_code}")
        return False


def test_openapi_json():
    """测试6: OpenAPI Schema"""
    print_section("测试6: OpenAPI Schema")

    response = requests.get(f"{BASE_URL}/openapi.json")
    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        data = response.json()

        # 验证OpenAPI结构
        assert "openapi" in data, "缺少 openapi 版本"
        assert "info" in data, "缺少 info 字段"
        assert "paths" in data, "缺少 paths 字段"
        assert "tags" in data, "缺少 tags 字段"

        print(f"\nOpenAPI版本: {data['openapi']}")
        print(f"API标题: {data['info']['title']}")
        print(f"API版本: {data['info']['version']}")
        print(f"\n定义的标签数量: {len(data['tags'])}")

        print("\n标签列表:")
        for tag in data["tags"]:
            print(f"  - {tag['name']}: {tag['description'][:50]}...")

        print("\n✅ OpenAPI Schema 验证通过")
        return True
    else:
        print(f"❌ 请求失败，状态码: {response.status_code}")
        return False


def test_root_endpoint():
    """测试7: 根端点"""
    print_section("测试7: 根端点")

    response = requests.get(f"{BASE_URL}/")
    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print_json(data)

        assert "message" in data, "缺少 message 字段"
        assert "version" in data, "缺少 version 字段"
        assert "docs" in data, "缺少 docs 字段"

        print("✅ 根端点测试通过")
        return True
    else:
        print(f"❌ 请求失败，状态码: {response.status_code}")
        return False


def test_legacy_health_check():
    """测试8: 旧版健康检查端点"""
    print_section("测试8: 旧版健康检查端点 (/health)")

    response = requests.get(f"{BASE_URL}/health")
    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print_json(data)

        assert "status" in data, "缺少 status 字段"
        assert data["status"] == "healthy", "服务状态不是 healthy"

        print("✅ 旧版健康检查端点正常")
        return True
    else:
        print(f"❌ 请求失败，状态码: {response.status_code}")
        return False


def main():
    print("\n" + "=" * 60)
    print("  Iteration 1.5 测试套件")
    print("  API文档与健康检查")
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

        # 执行所有测试
        results = []
        results.append(("基础健康检查", test_basic_health_check()))
        results.append(("详细健康检查", test_detailed_health_check()))
        results.append(("系统信息", test_system_info()))
        results.append(("API版本", test_version()))
        results.append(("Swagger UI", test_swagger_ui()))
        results.append(("OpenAPI Schema", test_openapi_json()))
        results.append(("根端点", test_root_endpoint()))
        results.append(("旧版健康检查", test_legacy_health_check()))

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
            print("\n✅ Iteration 1.5 功能验证完成:")
            print("   1. ✅ 基础健康检查端点")
            print("   2. ✅ 详细健康检查（数据库状态）")
            print("   3. ✅ 系统信息端点")
            print("   4. ✅ API版本查询")
            print("   5. ✅ Swagger UI 文档可访问")
            print("   6. ✅ OpenAPI Schema 完整")
            print("   7. ✅ 标签元数据配置")
            print("\n手动验证项:")
            print(f"   - 访问 Swagger UI: {BASE_URL}/docs")
            print(f"   - 访问 ReDoc: {BASE_URL}/redoc")
            print("   - 检查 API 分组是否清晰")
            print("   - 检查端点描述是否完整")
        else:
            print(f"\n⚠️ {total - passed} 个测试失败，请检查日志")

    except Exception as e:
        print(f"\n❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
