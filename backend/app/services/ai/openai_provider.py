import json
import logging
from typing import Dict, Optional, List
from openai import AsyncOpenAI
from app.services.ai.base import AIProvider
from app.core.config import settings

logger = logging.getLogger(__name__)


class OpenAIProvider(AIProvider):
    """OpenAI API 实现（使用 DALL-E 3 和 GPT-4 Vision）"""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.dalle_model = "dall-e-3"
        self.vision_model = "gpt-4-vision-preview"

    async def generate_design(
        self,
        prompt: str,
        reference_images: Optional[List[str]] = None,
        design_target: str = "10nails",
        customer_context: Optional[str] = None
    ) -> str:
        """使用 DALL-E 3 生成美甲设计图"""

        # 构建增强的提示词
        enhanced_prompt = self._build_generation_prompt(prompt, design_target, customer_context)

        logger.info("=== OpenAI generate_design 参数 ===")
        logger.info(f"  design_target    : {design_target}")
        logger.info(f"  prompt           : {prompt}")
        logger.info(f"  reference_images : {reference_images}")
        logger.info(f"  customer_context : {customer_context}")
        logger.info(f"  enhanced_prompt  :\n{enhanced_prompt}")
        logger.info("===================================")

        try:
            response = await self.client.images.generate(
                model=self.dalle_model,
                prompt=enhanced_prompt,
                size="1024x1024",
                quality="standard",
                n=1
            )

            image_url = response.data[0].url
            logger.info(f"设计生成成功: {image_url}")
            return image_url

        except Exception as e:
            logger.error(f"DALL-E 3 生成失败: {e}")
            raise

    async def refine_design(
        self,
        original_image: str,
        refinement_instruction: str,
        design_target: str = "10nails",
        customer_context: Optional[str] = None,
        original_prompt: Optional[str] = None
    ) -> str:
        """使用 GPT-4 Vision 分析原图，然后用 DALL-E 3 重新生成"""

        # 1. 使用 GPT-4 Vision 分析原图并生成新提示词
        sections = []
        if customer_context:
            sections.append(f"【客户甲型信息 - 必须严格保持一致】\n{customer_context}")
        if original_prompt:
            sections.append(f"【原始设计提示词】\n{original_prompt}")
        context_block = "\n\n".join(sections)

        analysis_prompt = f"""请分析这张美甲设计图，然后根据以下信息生成新的设计描述：

{context_block}

【本次优化指令】
{refinement_instruction}

请返回详细的设计描述（英文），用于 DALL-E 3 生成新图片。
注意：必须保持指甲形状和长度与原图一致，只按优化指令调整设计风格和细节。"""

        try:
            response = await self.client.chat.completions.create(
                model=self.vision_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": analysis_prompt},
                            {"type": "image_url", "image_url": {"url": original_image}}
                        ]
                    }
                ],
                max_tokens=500
            )

            new_prompt = response.choices[0].message.content
            logger.info(f"优化提示词生成成功")

            # 2. 使用新提示词生成设计图（保持原始 design_target + 客户甲型约束）
            return await self.generate_design(new_prompt, design_target=design_target, customer_context=customer_context)

        except Exception as e:
            logger.error(f"设计优化失败: {e}")
            raise

    async def estimate_execution(self, design_image: str) -> Dict:
        """使用 GPT-4 Vision 估算执行难度"""

        prompt = """
        请分析这张美甲设计图，估算以下信息：

        1. 预估耗时（分钟）
        2. 难度等级（简单/中等/困难）
        3. 需要的材料清单
        4. 需要的技法

        请以 JSON 格式返回：
        {
            "estimated_duration": 120,
            "difficulty_level": "中等",
            "materials": ["甲油胶-红色", "亮片", "封层"],
            "techniques": ["渐变", "贴片", "封层"]
        }
        """

        try:
            response = await self.client.chat.completions.create(
                model=self.vision_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": design_image}}
                        ]
                    }
                ],
                max_tokens=800,
                temperature=0.3
            )

            result = json.loads(response.choices[0].message.content)
            logger.info(f"执行估算完成: {result['difficulty_level']}, {result['estimated_duration']}分钟")
            return result

        except Exception as e:
            logger.error(f"执行估算失败: {e}")
            raise

    async def compare_images(
        self,
        design_image: str,
        actual_image: str,
        artist_review: Optional[str] = None,
        customer_feedback: Optional[str] = None,
        customer_satisfaction: Optional[int] = None
    ) -> Dict:
        """使用 GPT-4 Vision 进行综合对比分析"""

        # 构建增强的 prompt（包含文本上下文）
        system_prompt = "你是一位资深美甲艺术评审专家。请对比设计方案图和实际完成图，并结合美甲师的复盘内容和客户反馈，生成全面的分析报告。"

        user_prompt = self._build_comparison_prompt(
            artist_review=artist_review,
            customer_feedback=customer_feedback,
            customer_satisfaction=customer_satisfaction
        )

        logger.info(f"开始 AI 综合分析")
        logger.info(f"包含上下文: artist_review={bool(artist_review)}, customer_feedback={bool(customer_feedback)}, satisfaction={customer_satisfaction}")

        try:
            response = await self.client.chat.completions.create(
                model=self.vision_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_prompt},
                            {"type": "image_url", "image_url": {"url": design_image, "detail": "high"}},
                            {"type": "image_url", "image_url": {"url": actual_image, "detail": "high"}}
                        ]
                    }
                ],
                max_tokens=2000,
                temperature=0.3
            )

            # 解析 JSON 响应
            result = json.loads(response.choices[0].message.content)
            logger.info(f"AI 综合分析完成，相似度: {result['similarity_score']}")

            return result

        except Exception as e:
            logger.error(f"AI 对比分析失败: {e}")
            raise

    def _build_generation_prompt(self, base_prompt: str, design_target: str, customer_context: Optional[str] = None) -> str:
        """构建 DALL-E 3 生成提示词（结构化格式）"""

        target_descriptions = {
            "single": "EXACTLY 1 nail, a single nail close-up, one nail only",
            "5nails": "EXACTLY 5 nails arranged in a row, one hand, five nails total",
            "10nails": "EXACTLY 10 nails showing both hands complete, ten nails total"
        }

        target_counts = {
            "single": "1",
            "5nails": "5",
            "10nails": "10"
        }

        target_desc = target_descriptions.get(design_target, target_descriptions["10nails"])
        target_count = target_counts.get(design_target, "10")

        prompt = f"Nail art design flat lay, nails only. CRITICAL REQUIREMENT: Show EXACTLY {target_count} nail(s) — {target_desc}. The image MUST contain precisely {target_count} nail(s), no more, no less.\n\n"
        prompt += f"【Design Intent】\n{base_prompt}\n\n"
        if customer_context:
            prompt += f"【Nail Profile - MUST maintain consistency】\n{customer_context}\n\n"
        prompt += f"【Quantity Rule - STRICTLY ENFORCED】\nThe final image must show EXACTLY {target_count} nail(s). Do not add extra nails or omit any.\n\n"
        prompt += "STRICTLY NO fingers, NO hands, NO skin, NO body parts — nails only, detached and floating on a clean white background. Flat lay or top-down view. High quality, detailed, professional product photography, well-lit. No text, no labels, no annotations, no watermarks."
        return prompt

    def _build_comparison_prompt(
        self,
        artist_review: Optional[str],
        customer_feedback: Optional[str],
        customer_satisfaction: Optional[int]
    ) -> str:
        """构建包含上下文的对比分析 prompt"""

        prompt = """请对比以下两张美甲图片：
- 图片1：设计方案（预期效果）
- 图片2：实际完成图

请从以下维度进行分析：
1. **视觉对比**：颜色准确度、图案精度、细节处理、整体构图
2. **相似度评分**：0-100分（100分表示完全一致）
"""

        # 添加文本上下文
        if artist_review:
            prompt += f"\n**美甲师复盘**：\n{artist_review}\n"

        if customer_feedback:
            prompt += f"\n**客户反馈**：\n{customer_feedback}\n"

        if customer_satisfaction:
            stars = "⭐" * customer_satisfaction
            prompt += f"\n**客户满意度**：{stars} ({customer_satisfaction}/5星)\n"

        prompt += """
请结合图片和上述文本信息，返回JSON格式的分析结果：

{
    "similarity_score": 92,
    "overall_assessment": "整体完成度高，颜色还原准确，图案精度优秀。",
    "differences": {
        "color_accuracy": "颜色还原度95%，略有色差主要在渐变过渡部分",
        "pattern_precision": "图案精度90%，线条流畅细腻",
        "detail_work": "细节处理完整，亮片分布均匀",
        "composition": "整体构图协调，与设计方案高度一致"
    },
    "contextual_insights": {
        "artist_perspective": "基于美甲师提到的'时间紧张'，完成度已属优秀",
        "customer_perspective": "客户反馈与视觉分析一致，满意度评分合理",
        "satisfaction_analysis": "5星评分反映了客户对整体效果的高度认可"
    },
    "suggestions": [
        "渐变过渡可以更加自然",
        "建议预留更充足的时间以提升细节"
    ],
    "ability_scores": {
        "颜色搭配": {"score": 88, "evidence": "色彩组合协调，渐变过渡自然"},
        "图案精度": {"score": 90, "evidence": "线条精准，图案清晰"},
        "细节处理": {"score": 85, "evidence": "亮片分布均匀，边缘处理细致"},
        "整体构图": {"score": 92, "evidence": "布局合理，视觉平衡"},
        "技法运用": {"score": 87, "evidence": "多种技法熟练运用"},
        "创意表达": {"score": 80, "evidence": "忠实还原设计，执行力强"}
    }
}

**重要**：
- 如果美甲师复盘或客户反馈提到具体问题（如"颜色太深"），请在对应维度的分析中重点关注
- 如果客户满意度与视觉分析存在差异，请在 contextual_insights 中分析原因
- 所有分数必须客观公正，基于视觉证据
- 确保返回的是有效的 JSON 格式
"""

        return prompt.strip()
