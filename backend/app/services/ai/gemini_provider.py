import base64
import json
import logging
import os
from pathlib import Path
from typing import Dict, Optional, List
from google import genai
from google.genai import types
from app.services.ai.base import AIProvider
from app.core.config import settings

logger = logging.getLogger(__name__)


class GeminiProvider(AIProvider):
    """Google Gemini API 实现（使用 Imagen 3 和 Gemini 2.0 Flash）"""

    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.vision_model = "gemini-2.0-flash"
        self.image_gen_model = "gemini-2.0-flash-exp-image-generation"

    @staticmethod
    def _extract_json(text: str) -> dict:
        """从可能包含 markdown 代码块的文本中提取 JSON"""
        import re
        # 剥离 ```json ... ``` 包裹
        match = re.search(r'```(?:json)?\s*\n?(.*?)\n?\s*```', text, re.DOTALL)
        if match:
            text = match.group(1)
        return json.loads(text.strip())

    def _load_image_part(self, image_path: str) -> types.Part:
        """将本地图片路径转为 Gemini Part（读取字节）"""
        # image_path 可能是 /uploads/designs/xxx.png 格式
        if image_path.startswith("/uploads/"):
            local_path = os.path.join(settings.UPLOAD_DIR, image_path[len("/uploads/"):])
        else:
            local_path = image_path

        ext = Path(local_path).suffix.lower()
        mime_map = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}
        mime_type = mime_map.get(ext, "image/png")

        with open(local_path, "rb") as f:
            data = f.read()
        return types.Part.from_bytes(data=data, mime_type=mime_type)

    async def generate_design(
        self,
        prompt: str,
        reference_images: Optional[List[str]] = None,
        design_target: str = "10nails"
    ) -> str:
        """使用 Gemini 生成美甲设计图"""

        enhanced_prompt = self._build_generation_prompt(prompt, design_target)

        logger.info(f"生成美甲设计，目标: {design_target}")
        logger.debug(f"提示词: {enhanced_prompt}")

        try:
            # 构建内容：文本提示 + 可选的参考图
            contents: list = [enhanced_prompt]
            if reference_images:
                for img_path in reference_images:
                    try:
                        contents.append(self._load_image_part(img_path))
                    except Exception as e:
                        logger.warning(f"加载参考图失败 {img_path}: {e}")

            response = await self.client.aio.models.generate_content(
                model=self.image_gen_model,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_modalities=["TEXT", "IMAGE"],
                )
            )

            # 从响应中提取生成的图片
            import uuid
            for part in response.candidates[0].content.parts:
                if part.inline_data and part.inline_data.mime_type.startswith("image/"):
                    raw_data = part.inline_data.data

                    # Gemini 可能返回 base64 编码的字符串而非原始二进制
                    if isinstance(raw_data, (str, bytes)) and not (isinstance(raw_data, bytes) and raw_data[:4] == b'\x89PNG'):
                        try:
                            if isinstance(raw_data, bytes):
                                raw_data = raw_data.decode("ascii")
                            image_bytes = base64.b64decode(raw_data)
                        except Exception:
                            image_bytes = raw_data if isinstance(raw_data, bytes) else raw_data.encode()
                    else:
                        image_bytes = raw_data

                    filename = f"design_{uuid.uuid4().hex[:12]}.png"
                    filepath = os.path.join(settings.UPLOAD_DIR, "designs", filename)
                    os.makedirs(os.path.dirname(filepath), exist_ok=True)

                    with open(filepath, "wb") as f:
                        f.write(image_bytes)

                    image_url = f"/uploads/designs/{filename}"
                    logger.info(f"设计生成成功: {image_url}")
                    return image_url

            raise RuntimeError("Gemini 未返回图片数据")

        except Exception as e:
            logger.error(f"Gemini 图片生成失败: {e}")
            raise

    async def refine_design(
        self,
        original_image: str,
        refinement_instruction: str,
        design_target: str = "10nails"
    ) -> str:
        """使用 Gemini Vision 分析原图，然后用 Imagen 3 重新生成"""

        analysis_prompt = f"""
        请分析这张美甲设计图，然后根据以下优化指令生成新的设计描述：

        优化指令：{refinement_instruction}

        请返回详细的设计描述（英文），用于图片生成模型生成新图片。
        """

        try:
            # 1. 使用 Gemini Vision 分析原图并生成新提示词
            contents = [
                types.Part.from_text(text=analysis_prompt),
                self._load_image_part(original_image),
            ]

            response = await self.client.aio.models.generate_content(
                model=self.vision_model,
                contents=contents,
                config=types.GenerateContentConfig(
                    max_output_tokens=500,
                )
            )

            new_prompt = response.text
            logger.info("优化提示词生成成功")

            # 2. 使用新提示词生成设计图（保持原始 design_target）
            return await self.generate_design(new_prompt, design_target=design_target)

        except Exception as e:
            logger.error(f"设计优化失败: {e}")
            raise

    async def estimate_execution(self, design_image: str) -> Dict:
        """使用 Gemini Vision 估算执行难度"""

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
            contents = [
                types.Part.from_text(text=prompt),
                self._load_image_part(design_image),
            ]

            response = await self.client.aio.models.generate_content(
                model=self.vision_model,
                contents=contents,
                config=types.GenerateContentConfig(
                    max_output_tokens=800,
                    temperature=0.3,
                )
            )

            result = self._extract_json(response.text)
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
        """使用 Gemini Vision 进行综合对比分析"""

        system_prompt = "你是一位资深美甲艺术评审专家。请对比设计方案图和实际完成图，并结合美甲师的复盘内容和客户反馈，生成全面的分析报告。"

        user_prompt = self._build_comparison_prompt(
            artist_review=artist_review,
            customer_feedback=customer_feedback,
            customer_satisfaction=customer_satisfaction
        )

        logger.info("开始 AI 综合分析")
        logger.info(f"包含上下文: artist_review={bool(artist_review)}, customer_feedback={bool(customer_feedback)}, satisfaction={customer_satisfaction}")

        try:
            contents = [
                types.Part.from_text(text=user_prompt),
                self._load_image_part(design_image),
                self._load_image_part(actual_image),
            ]

            response = await self.client.aio.models.generate_content(
                model=self.vision_model,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    max_output_tokens=2000,
                    temperature=0.3,
                )
            )

            result = self._extract_json(response.text)
            logger.info(f"AI 综合分析完成，相似度: {result['similarity_score']}")
            return result

        except Exception as e:
            logger.error(f"AI 对比分析失败: {e}")
            raise

    def _build_generation_prompt(self, base_prompt: str, design_target: str) -> str:
        """构建 Imagen 3 生成提示词"""

        target_descriptions = {
            "single": "a single nail art design, close-up view",
            "5nails": "5 nails in a row showing nail art design",
            "10nails": "10 nails (both hands) showing complete nail art design"
        }

        target_desc = target_descriptions.get(design_target, target_descriptions["10nails"])

        enhanced_prompt = f"""
        Professional nail art design, {target_desc}.
        {base_prompt}

        High quality, detailed, professional photography, well-lit, white background.
        """

        return enhanced_prompt.strip()

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
