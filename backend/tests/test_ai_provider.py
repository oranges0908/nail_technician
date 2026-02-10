"""
AI Provider 单元测试
覆盖: OpenAIProvider — mock OpenAI 客户端
"""
import json
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.ai.openai_provider import OpenAIProvider


@pytest.fixture
def mock_openai_client():
    """Mock AsyncOpenAI 客户端"""
    return AsyncMock()


@pytest.fixture
def provider(mock_openai_client):
    """创建 OpenAIProvider 并替换 client"""
    with patch("app.services.ai.openai_provider.AsyncOpenAI"):
        p = OpenAIProvider()
        p.client = mock_openai_client
        return p


class TestGenerateDesign:
    """测试 generate_design"""

    @pytest.mark.asyncio
    async def test_generate_design_success(self, provider, mock_openai_client):
        """成功生成设计图返回 URL"""
        mock_response = MagicMock()
        mock_response.data = [MagicMock(url="https://example.com/design.png")]
        mock_openai_client.images.generate.return_value = mock_response

        result = await provider.generate_design("粉色渐变美甲")
        assert result == "https://example.com/design.png"
        mock_openai_client.images.generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_design_with_target(self, provider, mock_openai_client):
        """不同 design_target 生成不同提示词"""
        mock_response = MagicMock()
        mock_response.data = [MagicMock(url="https://example.com/single.png")]
        mock_openai_client.images.generate.return_value = mock_response

        result = await provider.generate_design("简约美甲", design_target="single")
        assert result == "https://example.com/single.png"

        # 验证提示词包含 single nail 描述
        call_args = mock_openai_client.images.generate.call_args
        assert "single" in call_args.kwargs["prompt"].lower()

    @pytest.mark.asyncio
    async def test_generate_design_api_error(self, provider, mock_openai_client):
        """API 错误时抛出异常"""
        mock_openai_client.images.generate.side_effect = Exception("API rate limit")

        with pytest.raises(Exception, match="API rate limit"):
            await provider.generate_design("测试")


class TestRefineDesign:
    """测试 refine_design"""

    @pytest.mark.asyncio
    async def test_refine_design_success(self, provider, mock_openai_client):
        """成功优化设计"""
        # Mock GPT-4 Vision 分析
        vision_response = MagicMock()
        vision_response.choices = [
            MagicMock(message=MagicMock(content="Refined nail art with more glitter"))
        ]
        mock_openai_client.chat.completions.create.return_value = vision_response

        # Mock DALL-E 重新生成
        dalle_response = MagicMock()
        dalle_response.data = [MagicMock(url="https://example.com/refined.png")]
        mock_openai_client.images.generate.return_value = dalle_response

        result = await provider.refine_design(
            "https://example.com/original.png", "增加更多亮片"
        )
        assert result == "https://example.com/refined.png"


class TestEstimateExecution:
    """测试 estimate_execution"""

    @pytest.mark.asyncio
    async def test_estimate_execution_success(self, provider, mock_openai_client):
        """成功估算执行难度"""
        estimation = {
            "estimated_duration": 120,
            "difficulty_level": "困难",
            "materials": ["甲油胶", "亮片"],
            "techniques": ["渐变", "贴片"],
        }
        vision_response = MagicMock()
        vision_response.choices = [
            MagicMock(message=MagicMock(content=json.dumps(estimation)))
        ]
        mock_openai_client.chat.completions.create.return_value = vision_response

        result = await provider.estimate_execution("https://example.com/design.png")
        assert result["estimated_duration"] == 120
        assert result["difficulty_level"] == "困难"


class TestCompareImages:
    """测试 compare_images"""

    @pytest.mark.asyncio
    async def test_compare_images_success(self, provider, mock_openai_client):
        """成功对比分析"""
        comparison = {
            "similarity_score": 90,
            "differences": {"color_accuracy": "颜色准确度95%"},
            "suggestions": ["渐变过渡可更自然"],
        }
        vision_response = MagicMock()
        vision_response.choices = [
            MagicMock(message=MagicMock(content=json.dumps(comparison)))
        ]
        mock_openai_client.chat.completions.create.return_value = vision_response

        result = await provider.compare_images(
            "https://example.com/design.png",
            "https://example.com/actual.png",
            artist_review="整体完成度高",
            customer_satisfaction=5,
        )
        assert result["similarity_score"] == 90

    @pytest.mark.asyncio
    async def test_compare_images_api_error(self, provider, mock_openai_client):
        """API 错误时抛出异常"""
        mock_openai_client.chat.completions.create.side_effect = Exception("Timeout")

        with pytest.raises(Exception, match="Timeout"):
            await provider.compare_images(
                "https://example.com/design.png",
                "https://example.com/actual.png",
            )
