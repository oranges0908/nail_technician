import logging
from typing import Optional
from app.services.ai.base import AIProvider
from app.services.ai.openai_provider import OpenAIProvider
from app.core.config import settings

logger = logging.getLogger(__name__)


class AIProviderFactory:
    """AI Provider 工厂 - 根据配置创建 AI 提供商实例"""

    _instance: Optional[AIProvider] = None

    @classmethod
    def get_provider(cls, provider_type: Optional[str] = None) -> AIProvider:
        """
        获取 AI Provider 实例（单例模式）

        Args:
            provider_type: AI 提供商类型（openai/baidu/alibaba等），默认从配置读取

        Returns:
            AIProvider 实例

        Raises:
            ValueError: 不支持的 AI 提供商类型
        """

        if cls._instance is not None:
            return cls._instance

        # 从配置读取提供商类型
        if provider_type is None:
            provider_type = settings.AI_PROVIDER.lower()

        logger.info(f"初始化 AI Provider: {provider_type}")

        # 根据类型创建实例
        if provider_type == "openai":
            cls._instance = OpenAIProvider()
        elif provider_type == "baidu":
            # TODO: 实现百度 AI Provider
            raise NotImplementedError("百度 AI Provider 尚未实现")
        elif provider_type == "alibaba":
            # TODO: 实现阿里云 AI Provider
            raise NotImplementedError("阿里云 AI Provider 尚未实现")
        else:
            raise ValueError(f"不支持的 AI Provider 类型: {provider_type}")

        logger.info(f"AI Provider 初始化成功: {provider_type}")
        return cls._instance

    @classmethod
    def reset(cls):
        """重置单例实例（主要用于测试）"""
        cls._instance = None
