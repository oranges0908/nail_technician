"""
GeminiProvider 单元测试
覆盖: GeminiProvider — mock Google GenAI 客户端
"""
import json
import os
import pytest
from unittest.mock import AsyncMock, patch, MagicMock, mock_open

from app.services.ai.gemini_provider import GeminiProvider


@pytest.fixture
def mock_genai_client():
    """Mock genai.Client"""
    client = MagicMock()
    client.aio = MagicMock()
    client.aio.models = MagicMock()
    client.aio.models.generate_content = AsyncMock()
    return client


@pytest.fixture
def provider(mock_genai_client):
    """创建 GeminiProvider 并替换 client"""
    with patch("app.services.ai.gemini_provider.genai.Client"):
        p = GeminiProvider()
        p.client = mock_genai_client
        return p


@pytest.fixture
def tmp_image(tmp_path):
    """创建临时测试图片文件"""
    img_file = tmp_path / "test.png"
    img_file.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)
    return str(img_file)


class TestLoadImagePart:
    """测试 _load_image_part"""

    def test_load_local_image(self, provider, tmp_image):
        """加载本地图片文件"""
        with patch("app.services.ai.gemini_provider.types.Part") as mock_part:
            provider._load_image_part(tmp_image)
            mock_part.from_bytes.assert_called_once()
            call_kwargs = mock_part.from_bytes.call_args.kwargs
            assert call_kwargs["mime_type"] == "image/png"

    def test_load_uploads_path(self, provider, tmp_path):
        """/uploads/ 路径转换为本地路径"""
        with patch("app.services.ai.gemini_provider.settings") as mock_settings:
            mock_settings.UPLOAD_DIR = str(tmp_path)
            img_file = tmp_path / "designs" / "test.jpg"
            img_file.parent.mkdir(parents=True, exist_ok=True)
            img_file.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 50)

            with patch("app.services.ai.gemini_provider.types.Part") as mock_part:
                provider._load_image_part("/uploads/designs/test.jpg")
                call_kwargs = mock_part.from_bytes.call_args.kwargs
                assert call_kwargs["mime_type"] == "image/jpeg"

    def test_load_missing_file_raises(self, provider):
        """加载不存在的文件抛出异常"""
        with pytest.raises(FileNotFoundError):
            provider._load_image_part("/nonexistent/image.png")


class TestGenerateDesign:
    """测试 generate_design"""

    @pytest.mark.asyncio
    async def test_generate_design_success(self, provider, mock_genai_client, tmp_path):
        """成功生成设计图返回 URL"""
        # 模拟 Gemini 返回包含图片的响应
        mock_image_data = MagicMock()
        mock_image_data.mime_type = "image/png"
        mock_image_data.data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100

        mock_part = MagicMock()
        mock_part.inline_data = mock_image_data

        mock_response = MagicMock()
        mock_response.candidates = [
            MagicMock(content=MagicMock(parts=[mock_part]))
        ]
        mock_genai_client.aio.models.generate_content.return_value = mock_response

        with patch("app.services.ai.gemini_provider.settings") as mock_settings:
            mock_settings.UPLOAD_DIR = str(tmp_path)

            result = await provider.generate_design("粉色渐变美甲")

            assert result.startswith("/uploads/designs/")
            assert result.endswith(".png")
            mock_genai_client.aio.models.generate_content.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_design_with_target(self, provider, mock_genai_client, tmp_path):
        """不同 design_target 影响提示词"""
        mock_image_data = MagicMock()
        mock_image_data.mime_type = "image/png"
        mock_image_data.data = b"\x89PNG" + b"\x00" * 50

        mock_part = MagicMock()
        mock_part.inline_data = mock_image_data

        mock_response = MagicMock()
        mock_response.candidates = [
            MagicMock(content=MagicMock(parts=[mock_part]))
        ]
        mock_genai_client.aio.models.generate_content.return_value = mock_response

        with patch("app.services.ai.gemini_provider.settings") as mock_settings:
            mock_settings.UPLOAD_DIR = str(tmp_path)

            await provider.generate_design("简约美甲", design_target="single")

            call_args = mock_genai_client.aio.models.generate_content.call_args
            contents = call_args.kwargs.get("contents") or call_args[1].get("contents")
            # 第一个元素是文本提示词
            prompt_text = contents[0]
            assert "single" in prompt_text.lower()

    @pytest.mark.asyncio
    async def test_generate_design_no_image_in_response(self, provider, mock_genai_client):
        """Gemini 未返回图片时抛出 RuntimeError"""
        mock_text_part = MagicMock()
        mock_text_part.inline_data = None

        mock_response = MagicMock()
        mock_response.candidates = [
            MagicMock(content=MagicMock(parts=[mock_text_part]))
        ]
        mock_genai_client.aio.models.generate_content.return_value = mock_response

        with pytest.raises(RuntimeError, match="Gemini 未返回图片数据"):
            await provider.generate_design("测试")

    @pytest.mark.asyncio
    async def test_generate_design_api_error(self, provider, mock_genai_client):
        """API 错误时抛出异常"""
        mock_genai_client.aio.models.generate_content.side_effect = Exception("API quota exceeded")

        with pytest.raises(Exception, match="API quota exceeded"):
            await provider.generate_design("测试")

    @pytest.mark.asyncio
    async def test_generate_design_with_reference_images(self, provider, mock_genai_client, tmp_path):
        """带参考图的设计生成"""
        mock_image_data = MagicMock()
        mock_image_data.mime_type = "image/png"
        mock_image_data.data = b"\x89PNG" + b"\x00" * 50

        mock_part = MagicMock()
        mock_part.inline_data = mock_image_data

        mock_response = MagicMock()
        mock_response.candidates = [
            MagicMock(content=MagicMock(parts=[mock_part]))
        ]
        mock_genai_client.aio.models.generate_content.return_value = mock_response

        # 创建临时参考图
        ref_img = tmp_path / "ref.png"
        ref_img.write_bytes(b"\x89PNG" + b"\x00" * 50)

        with patch("app.services.ai.gemini_provider.settings") as mock_settings:
            mock_settings.UPLOAD_DIR = str(tmp_path)
            with patch.object(provider, "_load_image_part", return_value=MagicMock()):
                result = await provider.generate_design(
                    "粉色美甲", reference_images=[str(ref_img)]
                )
                assert result.startswith("/uploads/designs/")


class TestRefineDesign:
    """测试 refine_design"""

    @pytest.mark.asyncio
    async def test_refine_design_success(self, provider, mock_genai_client, tmp_path):
        """成功优化设计"""
        # Mock Vision 分析返回文本
        vision_response = MagicMock()
        vision_response.text = "Refined nail art with extra glitter and gradient"

        # Mock 图片生成返回图片
        mock_image_data = MagicMock()
        mock_image_data.mime_type = "image/png"
        mock_image_data.data = b"\x89PNG" + b"\x00" * 50

        mock_img_part = MagicMock()
        mock_img_part.inline_data = mock_image_data

        gen_response = MagicMock()
        gen_response.candidates = [
            MagicMock(content=MagicMock(parts=[mock_img_part]))
        ]

        mock_genai_client.aio.models.generate_content.side_effect = [
            vision_response, gen_response
        ]

        with patch("app.services.ai.gemini_provider.settings") as mock_settings:
            mock_settings.UPLOAD_DIR = str(tmp_path)
            with patch.object(provider, "_load_image_part", return_value=MagicMock()):
                result = await provider.refine_design(
                    "/uploads/designs/original.png", "增加更多亮片"
                )
                assert result.startswith("/uploads/designs/")
                assert mock_genai_client.aio.models.generate_content.call_count == 2


class TestEstimateExecution:
    """测试 estimate_execution"""

    @pytest.mark.asyncio
    async def test_estimate_execution_success(self, provider, mock_genai_client):
        """成功估算执行难度"""
        estimation = {
            "estimated_duration": 120,
            "difficulty_level": "困难",
            "materials": ["甲油胶", "亮片"],
            "techniques": ["渐变", "贴片"],
        }
        mock_response = MagicMock()
        mock_response.text = json.dumps(estimation)
        mock_genai_client.aio.models.generate_content.return_value = mock_response

        with patch.object(provider, "_load_image_part", return_value=MagicMock()):
            result = await provider.estimate_execution("/uploads/designs/test.png")

        assert result["estimated_duration"] == 120
        assert result["difficulty_level"] == "困难"
        assert "甲油胶" in result["materials"]
        assert "渐变" in result["techniques"]

    @pytest.mark.asyncio
    async def test_estimate_execution_invalid_json(self, provider, mock_genai_client):
        """返回非 JSON 时抛出异常"""
        mock_response = MagicMock()
        mock_response.text = "This is not valid JSON"
        mock_genai_client.aio.models.generate_content.return_value = mock_response

        with patch.object(provider, "_load_image_part", return_value=MagicMock()):
            with pytest.raises(json.JSONDecodeError):
                await provider.estimate_execution("/uploads/designs/test.png")


class TestCompareImages:
    """测试 compare_images"""

    @pytest.mark.asyncio
    async def test_compare_images_success(self, provider, mock_genai_client):
        """成功对比分析"""
        comparison = {
            "similarity_score": 90,
            "overall_assessment": "整体完成度高",
            "differences": {"color_accuracy": "颜色准确度95%"},
            "contextual_insights": {
                "artist_perspective": "完成度优秀",
                "customer_perspective": "客户满意",
                "satisfaction_analysis": "5星评分合理",
            },
            "suggestions": ["渐变过渡可更自然"],
            "ability_scores": {
                "颜色搭配": {"score": 88, "evidence": "色彩协调"},
            },
        }
        mock_response = MagicMock()
        mock_response.text = json.dumps(comparison)
        mock_genai_client.aio.models.generate_content.return_value = mock_response

        with patch.object(provider, "_load_image_part", return_value=MagicMock()):
            result = await provider.compare_images(
                "/uploads/designs/design.png",
                "/uploads/designs/actual.png",
                artist_review="整体完成度高",
                customer_satisfaction=5,
            )

        assert result["similarity_score"] == 90
        assert "suggestions" in result
        assert "ability_scores" in result

    @pytest.mark.asyncio
    async def test_compare_images_minimal(self, provider, mock_genai_client):
        """仅传设计图和实际图（无额外上下文）"""
        comparison = {
            "similarity_score": 75,
            "differences": {"color_accuracy": "色差明显"},
            "suggestions": ["提升颜色准确度"],
        }
        mock_response = MagicMock()
        mock_response.text = json.dumps(comparison)
        mock_genai_client.aio.models.generate_content.return_value = mock_response

        with patch.object(provider, "_load_image_part", return_value=MagicMock()):
            result = await provider.compare_images(
                "/uploads/designs/design.png",
                "/uploads/designs/actual.png",
            )

        assert result["similarity_score"] == 75

    @pytest.mark.asyncio
    async def test_compare_images_api_error(self, provider, mock_genai_client):
        """API 错误时抛出异常"""
        mock_genai_client.aio.models.generate_content.side_effect = Exception("Timeout")

        with patch.object(provider, "_load_image_part", return_value=MagicMock()):
            with pytest.raises(Exception, match="Timeout"):
                await provider.compare_images(
                    "/uploads/designs/design.png",
                    "/uploads/designs/actual.png",
                )


class TestBuildGenerationPrompt:
    """测试 _build_generation_prompt"""

    def test_default_target(self, provider):
        """默认目标是 10nails"""
        prompt = provider._build_generation_prompt("粉色美甲", "10nails")
        assert "10 nails" in prompt.lower() or "both hands" in prompt.lower()

    def test_single_target(self, provider):
        """single 目标"""
        prompt = provider._build_generation_prompt("渐变美甲", "single")
        assert "single" in prompt.lower()

    def test_5nails_target(self, provider):
        """5nails 目标"""
        prompt = provider._build_generation_prompt("法式美甲", "5nails")
        assert "5 nails" in prompt.lower()

    def test_unknown_target_fallback(self, provider):
        """未知目标回退到 10nails"""
        prompt = provider._build_generation_prompt("美甲", "unknown")
        assert "10 nails" in prompt.lower() or "both hands" in prompt.lower()

    def test_base_prompt_included(self, provider):
        """用户提示词包含在结果中"""
        prompt = provider._build_generation_prompt("cherry blossom nails", "single")
        assert "cherry blossom nails" in prompt


class TestBuildComparisonPrompt:
    """测试 _build_comparison_prompt"""

    def test_basic_prompt(self, provider):
        """基础对比提示词"""
        prompt = provider._build_comparison_prompt(None, None, None)
        assert "设计方案" in prompt
        assert "实际完成图" in prompt

    def test_with_artist_review(self, provider):
        """包含美甲师复盘"""
        prompt = provider._build_comparison_prompt("时间紧张", None, None)
        assert "时间紧张" in prompt
        assert "美甲师复盘" in prompt

    def test_with_customer_feedback(self, provider):
        """包含客户反馈"""
        prompt = provider._build_comparison_prompt(None, "非常满意", None)
        assert "非常满意" in prompt
        assert "客户反馈" in prompt

    def test_with_satisfaction(self, provider):
        """包含客户满意度"""
        prompt = provider._build_comparison_prompt(None, None, 4)
        assert "4" in prompt
        assert "⭐" in prompt

    def test_with_all_context(self, provider):
        """包含所有上下文"""
        prompt = provider._build_comparison_prompt("完成度高", "很喜欢", 5)
        assert "完成度高" in prompt
        assert "很喜欢" in prompt
        assert "5" in prompt


class TestFactoryGeminiIntegration:
    """测试 Factory 能正确创建 GeminiProvider"""

    def test_factory_creates_gemini(self):
        """AI_PROVIDER=gemini 时返回 GeminiProvider 实例"""
        from app.services.ai.factory import AIProviderFactory

        AIProviderFactory.reset()
        with patch("app.services.ai.factory.GeminiProvider") as mock_cls:
            mock_instance = mock_cls.return_value
            provider = AIProviderFactory.get_provider("gemini")
            assert provider is mock_instance
            mock_cls.assert_called_once()
        AIProviderFactory.reset()
