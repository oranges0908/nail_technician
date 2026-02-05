"""
AI Provider 测试

测试 Iteration 3.1 和 3.2 的所有功能：
1. AIProvider 抽象接口定义
2. OpenAI Provider 实现
3. AI Provider Factory 工厂模式
4. 4个核心方法（generate_design, refine_design, estimate_execution, compare_images）

运行前确保:
1. .env 文件中配置了 OPENAI_API_KEY
2. AI_PROVIDER=openai

注意：
- 由于涉及真实的 OpenAI API 调用，此测试使用 Mock 模拟
- 真实 API 调用需要注释掉 @patch 装饰器
"""
import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.ai.base import AIProvider
from app.services.ai.openai_provider import OpenAIProvider
from app.services.ai.factory import AIProviderFactory


# ==================== 测试1: AIProvider 抽象接口 ====================

def test_abstract_interface():
    """测试1: 验证 AIProvider 是抽象类，不能直接实例化"""
    print("\n" + "=" * 60)
    print("  测试1: AIProvider 抽象接口")
    print("=" * 60)

    with pytest.raises(TypeError):
        # 抽象类不能直接实例化
        provider = AIProvider()

    print("✅ AIProvider 是抽象类，无法直接实例化")


def test_abstract_methods():
    """测试2: 验证抽象方法的定义"""
    print("\n" + "=" * 60)
    print("  测试2: AIProvider 抽象方法定义")
    print("=" * 60)

    # 检查4个抽象方法是否存在
    abstract_methods = [
        'generate_design',
        'refine_design',
        'estimate_execution',
        'compare_images'
    ]

    for method_name in abstract_methods:
        assert hasattr(AIProvider, method_name), f"缺少抽象方法: {method_name}"
        print(f"✅ 抽象方法存在: {method_name}")

    print(f"\n✅ 所有4个抽象方法定义完整")


# ==================== 测试3: AIProviderFactory 工厂模式 ====================

def test_factory_openai():
    """测试3: Factory 创建 OpenAI Provider"""
    print("\n" + "=" * 60)
    print("  测试3: AIProviderFactory 创建 OpenAI Provider")
    print("=" * 60)

    # 重置单例
    AIProviderFactory.reset()

    # 创建 OpenAI Provider
    provider = AIProviderFactory.get_provider("openai")

    assert provider is not None, "Provider 创建失败"
    assert isinstance(provider, OpenAIProvider), f"类型错误: {type(provider)}"
    assert isinstance(provider, AIProvider), "不是 AIProvider 子类"

    print(f"✅ 成功创建 OpenAI Provider: {type(provider).__name__}")


def test_factory_singleton():
    """测试4: Factory 单例模式"""
    print("\n" + "=" * 60)
    print("  测试4: AIProviderFactory 单例模式")
    print("=" * 60)

    # 重置单例
    AIProviderFactory.reset()

    # 多次获取应该返回同一个实例
    provider1 = AIProviderFactory.get_provider("openai")
    provider2 = AIProviderFactory.get_provider("openai")

    assert provider1 is provider2, "不是单例模式"

    print(f"✅ 单例模式验证通过: provider1 is provider2")


def test_factory_unsupported_provider():
    """测试5: Factory 不支持的 Provider"""
    print("\n" + "=" * 60)
    print("  测试5: AIProviderFactory 不支持的 Provider")
    print("=" * 60)

    # 重置单例
    AIProviderFactory.reset()

    with pytest.raises(ValueError) as exc_info:
        AIProviderFactory.get_provider("unknown_provider")

    assert "不支持的 AI Provider 类型" in str(exc_info.value)

    print(f"✅ 正确拒绝不支持的 Provider: {exc_info.value}")


# ==================== 测试6-9: OpenAI Provider 核心方法（Mock） ====================

@pytest.mark.asyncio
@patch('app.services.ai.openai_provider.AsyncOpenAI')
async def test_generate_design_mock(mock_openai):
    """测试6: generate_design 方法（Mock）"""
    print("\n" + "=" * 60)
    print("  测试6: OpenAI Provider - generate_design（Mock）")
    print("=" * 60)

    # 配置 Mock
    mock_response = MagicMock()
    mock_response.data = [MagicMock(url="https://example.com/design.png")]

    mock_client = MagicMock()
    mock_client.images.generate = AsyncMock(return_value=mock_response)
    mock_openai.return_value = mock_client

    # 重置并创建 Provider
    AIProviderFactory.reset()
    provider = OpenAIProvider()

    # 调用方法
    result = await provider.generate_design(
        prompt="红色渐变美甲，带金色亮片",
        design_target="10nails"
    )

    assert result == "https://example.com/design.png"
    assert mock_client.images.generate.called, "generate 方法未被调用"

    # 验证调用参数
    call_args = mock_client.images.generate.call_args
    assert call_args.kwargs['model'] == "dall-e-3"
    assert call_args.kwargs['size'] == "1024x1024"
    assert "红色渐变美甲" in call_args.kwargs['prompt'] or "Professional nail art" in call_args.kwargs['prompt']

    print(f"✅ generate_design 方法测试通过")
    print(f"   生成的图片 URL: {result}")


@pytest.mark.asyncio
@patch('app.services.ai.openai_provider.AsyncOpenAI')
async def test_refine_design_mock(mock_openai):
    """测试7: refine_design 方法（Mock）"""
    print("\n" + "=" * 60)
    print("  测试7: OpenAI Provider - refine_design（Mock）")
    print("=" * 60)

    # 配置 Mock（两次调用：GPT-4 Vision 分析 + DALL-E 3 生成）
    mock_vision_response = MagicMock()
    mock_vision_response.choices = [
        MagicMock(message=MagicMock(content="Red gradient nail art with more glitter"))
    ]

    mock_dalle_response = MagicMock()
    mock_dalle_response.data = [MagicMock(url="https://example.com/refined_design.png")]

    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_vision_response)
    mock_client.images.generate = AsyncMock(return_value=mock_dalle_response)
    mock_openai.return_value = mock_client

    # 创建 Provider
    provider = OpenAIProvider()

    # 调用方法
    result = await provider.refine_design(
        original_image="https://example.com/original.png",
        refinement_instruction="增加更多亮片"
    )

    assert result == "https://example.com/refined_design.png"
    assert mock_client.chat.completions.create.called, "Vision API 未被调用"
    assert mock_client.images.generate.called, "DALL-E 未被调用"

    print(f"✅ refine_design 方法测试通过")
    print(f"   优化后的图片 URL: {result}")


@pytest.mark.asyncio
@patch('app.services.ai.openai_provider.AsyncOpenAI')
async def test_estimate_execution_mock(mock_openai):
    """测试8: estimate_execution 方法（Mock）"""
    print("\n" + "=" * 60)
    print("  测试8: OpenAI Provider - estimate_execution（Mock）")
    print("=" * 60)

    # 配置 Mock
    mock_response_content = json.dumps({
        "estimated_duration": 90,
        "difficulty_level": "中等",
        "materials": ["甲油胶-红色", "亮片", "封层"],
        "techniques": ["渐变", "贴片"]
    })

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content=mock_response_content))
    ]

    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
    mock_openai.return_value = mock_client

    # 创建 Provider
    provider = OpenAIProvider()

    # 调用方法
    result = await provider.estimate_execution(
        design_image="https://example.com/design.png"
    )

    assert result["estimated_duration"] == 90
    assert result["difficulty_level"] == "中等"
    assert len(result["materials"]) == 3
    assert len(result["techniques"]) == 2

    print(f"✅ estimate_execution 方法测试通过")
    print(f"   预估耗时: {result['estimated_duration']} 分钟")
    print(f"   难度等级: {result['difficulty_level']}")


@pytest.mark.asyncio
@patch('app.services.ai.openai_provider.AsyncOpenAI')
async def test_compare_images_mock(mock_openai):
    """测试9: compare_images 方法（Mock）"""
    print("\n" + "=" * 60)
    print("  测试9: OpenAI Provider - compare_images（Mock）")
    print("=" * 60)

    # 配置 Mock
    mock_response_content = json.dumps({
        "similarity_score": 88,
        "overall_assessment": "整体完成度高，颜色还原准确",
        "differences": {
            "color_accuracy": "颜色还原度90%",
            "pattern_precision": "图案精度85%",
            "detail_work": "细节处理完整",
            "composition": "整体构图协调"
        },
        "contextual_insights": {
            "artist_perspective": "基于美甲师提到的时间紧张，完成度已属优秀",
            "customer_perspective": "客户反馈与视觉分析一致",
            "satisfaction_analysis": "5星评分反映了客户的高度认可"
        },
        "suggestions": ["渐变过渡可以更加自然"],
        "ability_scores": {
            "颜色搭配": {"score": 88, "evidence": "色彩组合协调"},
            "图案精度": {"score": 85, "evidence": "线条精准"},
            "细节处理": {"score": 90, "evidence": "细节完整"},
            "整体构图": {"score": 92, "evidence": "布局合理"},
            "技法运用": {"score": 87, "evidence": "技法熟练"},
            "创意表达": {"score": 80, "evidence": "忠实还原"}
        }
    })

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content=mock_response_content))
    ]

    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
    mock_openai.return_value = mock_client

    # 创建 Provider
    provider = OpenAIProvider()

    # 调用方法（包含上下文信息）
    result = await provider.compare_images(
        design_image="https://example.com/design.png",
        actual_image="https://example.com/actual.png",
        artist_review="时间有点紧张，但整体效果满意",
        customer_feedback="非常喜欢，颜色很漂亮",
        customer_satisfaction=5
    )

    assert result["similarity_score"] == 88
    assert "整体完成度高" in result["overall_assessment"]
    assert "differences" in result
    assert "contextual_insights" in result  # 上下文洞察
    assert len(result["ability_scores"]) == 6  # 6个能力维度

    # 验证调用参数（确保包含了上下文信息）
    call_args = mock_client.chat.completions.create.call_args
    messages = call_args.kwargs['messages']
    user_content = messages[1]['content'][0]['text']

    assert "时间有点紧张" in user_content or "美甲师复盘" in user_content
    assert "非常喜欢" in user_content or "客户反馈" in user_content

    print(f"✅ compare_images 方法测试通过（上下文感知）")
    print(f"   相似度评分: {result['similarity_score']}")
    print(f"   能力维度数量: {len(result['ability_scores'])}")
    print(f"   包含上下文洞察: {bool(result.get('contextual_insights'))}")


# ==================== 测试10: 上下文感知分析验证 ====================

@pytest.mark.asyncio
@patch('app.services.ai.openai_provider.AsyncOpenAI')
async def test_contextual_analysis(mock_openai):
    """测试10: 验证上下文感知分析（Iteration 3.2 的核心特性）"""
    print("\n" + "=" * 60)
    print("  测试10: 上下文感知分析验证")
    print("=" * 60)

    mock_response_content = json.dumps({
        "similarity_score": 85,
        "overall_assessment": "整体完成度优秀",
        "differences": {
            "color_accuracy": "颜色还原度92%",
            "pattern_precision": "图案精度88%",
            "detail_work": "细节处理完整",
            "composition": "整体构图协调"
        },
        "contextual_insights": {
            "artist_perspective": "美甲师提到的'客户手型不适合长指甲'得到了体现，设计做了适当调整",
            "customer_perspective": "客户反馈'比想象中更好看'说明调整是成功的",
            "satisfaction_analysis": "4星评分可能因为调整后与原设计有差异，但实际效果更佳"
        },
        "suggestions": ["建议在方案阶段就考虑客户手型"],
        "ability_scores": {
            "颜色搭配": {"score": 90, "evidence": "色彩协调"},
            "图案精度": {"score": 88, "evidence": "精准执行"},
            "细节处理": {"score": 92, "evidence": "细节完整"},
            "整体构图": {"score": 85, "evidence": "适应性调整"},
            "技法运用": {"score": 87, "evidence": "技法熟练"},
            "创意表达": {"score": 90, "evidence": "灵活应变"}
        }
    })

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content=mock_response_content))
    ]

    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
    mock_openai.return_value = mock_client

    provider = OpenAIProvider()

    # 调用方法（提供丰富的上下文）
    result = await provider.compare_images(
        design_image="https://example.com/design.png",
        actual_image="https://example.com/actual.png",
        artist_review="客户手型不太适合长指甲，做了适当调整",
        customer_feedback="比想象中更好看！",
        customer_satisfaction=4
    )

    # 验证上下文洞察存在且有意义
    assert "contextual_insights" in result
    insights = result["contextual_insights"]

    assert "artist_perspective" in insights
    assert "customer_perspective" in insights
    assert "satisfaction_analysis" in insights

    # 验证洞察内容提到了复盘和反馈
    assert len(insights["artist_perspective"]) > 0
    assert len(insights["customer_perspective"]) > 0
    assert len(insights["satisfaction_analysis"]) > 0

    print(f"✅ 上下文感知分析验证通过")
    print(f"   美甲师视角洞察: {insights['artist_perspective'][:50]}...")
    print(f"   客户视角洞察: {insights['customer_perspective'][:50]}...")
    print(f"   满意度分析: {insights['satisfaction_analysis'][:50]}...")


# ==================== 主函数 ====================

def print_section(title: str):
    """打印分隔标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  Iteration 3.1 & 3.2 测试套件")
    print("  AI Provider 抽象层")
    print("=" * 60)
    print("\n使用 pytest 运行: pytest test_ai_providers.py -v")
    print("=" * 60)

    # 使用 pytest 运行测试
    pytest.main([__file__, "-v", "-s"])
