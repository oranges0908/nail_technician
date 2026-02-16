from abc import ABC, abstractmethod
from typing import Dict, Optional, List


class AIProvider(ABC):
    """AI Provider 抽象基类 - 定义所有 AI 功能的接口"""

    @abstractmethod
    async def generate_design(
        self,
        prompt: str,
        reference_images: Optional[List[str]] = None,
        design_target: str = "10nails",
        customer_context: Optional[str] = None
    ) -> str:
        """
        生成美甲设计图

        Args:
            prompt: AI 生成提示词
            reference_images: 参考图片 URL 列表
            design_target: 设计目标（single/5nails/10nails）
            customer_context: 客户甲型和偏好信息，用于约束AI生成保持一致性

        Returns:
            生成的设计图 URL
        """
        pass

    @abstractmethod
    async def refine_design(
        self,
        original_image: str,
        refinement_instruction: str,
        design_target: str = "10nails",
        customer_context: Optional[str] = None,
        original_prompt: Optional[str] = None
    ) -> str:
        """
        迭代优化设计图

        Args:
            original_image: 原始设计图 URL
            refinement_instruction: 优化指令（自然语言）
            design_target: 设计目标（single/5nails/10nails），保持与原设计一致
            customer_context: 客户甲型和偏好信息，用于约束AI生成保持一致性
            original_prompt: 原始设计提示词，用于迭代优化时保持设计意图一致性

        Returns:
            优化后的设计图 URL
        """
        pass

    @abstractmethod
    async def estimate_execution(
        self,
        design_image: str
    ) -> Dict:
        """
        估算设计执行难度和时间

        Args:
            design_image: 设计图 URL

        Returns:
            {
                "estimated_duration": 120,  # 分钟
                "difficulty_level": "中等",
                "materials": ["甲油胶-红色", "亮片", "封层"],
                "techniques": ["渐变", "贴片", "封层"]
            }
        """
        pass

    @abstractmethod
    async def compare_images(
        self,
        design_image: str,
        actual_image: str,
        artist_review: Optional[str] = None,
        customer_feedback: Optional[str] = None,
        customer_satisfaction: Optional[int] = None
    ) -> Dict:
        """
        对比设计图和实际图，生成综合分析报告

        Args:
            design_image: 设计方案图片 URL
            actual_image: 实际完成图片 URL
            artist_review: 美甲师复盘内容（可选）
            customer_feedback: 客户反馈（可选）
            customer_satisfaction: 客户满意度评分 1-5（可选）

        Returns:
            {
                "similarity_score": 0-100,
                "overall_assessment": "综合评价",
                "differences": {
                    "color_accuracy": "颜色分析...",
                    "pattern_precision": "图案分析...",
                    "detail_work": "细节分析...",
                    "composition": "构图分析..."
                },
                "contextual_insights": {
                    "artist_perspective": "基于美甲师复盘的洞察",
                    "customer_perspective": "基于客户反馈的洞察",
                    "satisfaction_analysis": "满意度与视觉效果的关联分析"
                },
                "suggestions": ["改进建议1", "改进建议2"],
                "ability_scores": {
                    "颜色搭配": {"score": 85, "evidence": "..."},
                    "图案精度": {"score": 78, "evidence": "..."},
                    "细节处理": {"score": 82, "evidence": "..."},
                    "整体构图": {"score": 88, "evidence": "..."},
                    "技法运用": {"score": 80, "evidence": "..."},
                    "创意表达": {"score": 75, "evidence": "..."}
                }
            }
        """
        pass
