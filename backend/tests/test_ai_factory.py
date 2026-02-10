"""
AI Provider Factory 测试
覆盖: AIProviderFactory — singleton 模式、provider 选择、reset
"""
import pytest
from unittest.mock import patch

from app.services.ai.factory import AIProviderFactory
from app.services.ai.openai_provider import OpenAIProvider


@pytest.fixture(autouse=True)
def reset_factory():
    """每个测试前后重置 factory singleton"""
    AIProviderFactory.reset()
    yield
    AIProviderFactory.reset()


class TestAIProviderFactory:
    """AI Provider 工厂测试"""

    @patch("app.services.ai.factory.OpenAIProvider")
    def test_get_openai_provider(self, mock_openai_cls):
        """AI_PROVIDER=openai 时返回 OpenAIProvider 实例"""
        mock_instance = mock_openai_cls.return_value

        provider = AIProviderFactory.get_provider("openai")
        assert provider is mock_instance
        mock_openai_cls.assert_called_once()

    def test_unknown_provider_raises(self):
        """未知 provider 类型抛出 ValueError"""
        with pytest.raises(ValueError, match="不支持的 AI Provider"):
            AIProviderFactory.get_provider("unknown_provider")

    def test_unimplemented_provider_raises(self):
        """尚未实现的 provider 抛出 NotImplementedError"""
        with pytest.raises(NotImplementedError):
            AIProviderFactory.get_provider("baidu")

    @patch("app.services.ai.factory.OpenAIProvider")
    def test_singleton_pattern(self, mock_openai_cls):
        """多次调用返回同一实例（单例）"""
        p1 = AIProviderFactory.get_provider("openai")
        p2 = AIProviderFactory.get_provider("openai")
        assert p1 is p2
        # OpenAIProvider 只被实例化一次
        mock_openai_cls.assert_called_once()

    @patch("app.services.ai.factory.OpenAIProvider")
    def test_reset_clears_singleton(self, mock_openai_cls):
        """reset 后重新创建实例"""
        from unittest.mock import MagicMock
        instance1 = MagicMock()
        instance2 = MagicMock()
        mock_openai_cls.side_effect = [instance1, instance2]

        p1 = AIProviderFactory.get_provider("openai")
        AIProviderFactory.reset()
        p2 = AIProviderFactory.get_provider("openai")
        assert p1 is not p2
        assert mock_openai_cls.call_count == 2
