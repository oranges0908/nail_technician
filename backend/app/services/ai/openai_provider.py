import json
import logging
import os
import uuid
import httpx
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
        self.vision_model = "gpt-4o"

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

        logger.info("=== OpenAI generate_design params ===")
        logger.info(f"  design_target    : {design_target}")
        logger.info(f"  prompt           : {prompt}")
        logger.info(f"  reference_images : {reference_images}")
        logger.info(f"  customer_context : {customer_context}")
        logger.info(f"  enhanced_prompt  :\n{enhanced_prompt}")
        logger.info("=====================================")

        try:
            response = await self.client.images.generate(
                model=self.dalle_model,
                prompt=enhanced_prompt,
                size="1024x1024",
                quality="hd",
                n=1
            )

            cdn_url = response.data[0].url
            logger.info(f"DALL-E 3 generation successful, downloading image: {cdn_url[:80]}...")

            # 下载图片并保存到本地，避免临时 CDN URL 过期
            async with httpx.AsyncClient(timeout=60) as http:
                img_resp = await http.get(cdn_url)
                img_resp.raise_for_status()

            filename = f"design_{uuid.uuid4().hex[:12]}.png"
            filepath = os.path.join(settings.UPLOAD_DIR, "designs", filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "wb") as f:
                f.write(img_resp.content)

            local_path = f"/uploads/designs/{filename}"
            logger.info(f"Image saved locally: {local_path}")
            return local_path

        except Exception as e:
            logger.error(f"DALL-E 3 generation failed: {e}")
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
            sections.append(f"[Customer Nail Profile - MUST maintain consistency]\n{customer_context}")
        if original_prompt:
            sections.append(f"[Original Design Prompt]\n{original_prompt}")
        context_block = "\n\n".join(sections)

        analysis_prompt = f"""Please analyze this nail design image and generate a new design description based on the following information:

{context_block}

[Refinement instruction for this iteration]
{refinement_instruction}

Please return a detailed design description (in English) to be used by DALL-E 3 to generate a new image.
Note: Maintain the nail shape and length consistent with the original image, only adjust design style and details according to the refinement instruction."""

        try:
            # 构建图片内容：本地路径转 base64，HTTP URL 直接使用
            if original_image.startswith("/uploads/"):
                import base64
                local_path = os.path.join(settings.UPLOAD_DIR, original_image[len("/uploads/"):])
                with open(local_path, "rb") as f:
                    b64_data = base64.b64encode(f.read()).decode("utf-8")
                image_content = {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64_data}"}}
            else:
                image_content = {"type": "image_url", "image_url": {"url": original_image}}

            response = await self.client.chat.completions.create(
                model=self.vision_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": analysis_prompt},
                            image_content,
                        ]
                    }
                ],
                max_tokens=500
            )

            new_prompt = response.choices[0].message.content
            logger.info(f"Refined prompt generated successfully")

            # 2. 使用新提示词生成设计图（保持原始 design_target + 客户甲型约束）
            return await self.generate_design(new_prompt, design_target=design_target, customer_context=customer_context)

        except Exception as e:
            logger.error(f"Design refinement failed: {e}")
            raise

    async def estimate_execution(self, design_image: str) -> Dict:
        """使用 GPT-4 Vision 估算执行难度"""

        prompt = """
        Please analyze this nail design image and estimate the following:

        1. Estimated duration (minutes)
        2. Difficulty level (easy/medium/hard)
        3. Required materials list
        4. Required techniques

        Please return in JSON format:
        {
            "estimated_duration": 120,
            "difficulty_level": "medium",
            "materials": ["gel polish - red", "glitter", "top coat"],
            "techniques": ["gradient", "extension", "top coat"]
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
            logger.info(f"Execution estimation complete: {result['difficulty_level']}, {result['estimated_duration']} minutes")
            return result

        except Exception as e:
            logger.error(f"Execution estimation failed: {e}")
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
        system_prompt = "You are a senior nail art assessment expert. Please compare the design reference image and the actual completed photo, incorporating the nail artist's review and customer feedback to generate a comprehensive analysis report."

        user_prompt = self._build_comparison_prompt(
            artist_review=artist_review,
            customer_feedback=customer_feedback,
            customer_satisfaction=customer_satisfaction
        )

        logger.info(f"Starting AI comprehensive analysis")
        logger.info(f"Context included: artist_review={bool(artist_review)}, customer_feedback={bool(customer_feedback)}, satisfaction={customer_satisfaction}")

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
            logger.info(f"AI comprehensive analysis complete, similarity: {result['similarity_score']}")

            return result

        except Exception as e:
            logger.error(f"AI comparison analysis failed: {e}")
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
        prompt += "STRICTLY NO fingers, NO hands, NO skin, NO body parts — nails only, detached and floating on a clean white background. Flat lay or top-down view. High quality, detailed, professional product photography, well-lit. CRITICAL: ZERO TEXT on the image — no Chinese characters, no English letters, no numbers, no symbols, no written prompts, no calligraphy, no captions, no descriptions. Pure visual nail art only. Do not write or render any text element anywhere in the image."
        return prompt

    def _build_comparison_prompt(
        self,
        artist_review: Optional[str],
        customer_feedback: Optional[str],
        customer_satisfaction: Optional[int]
    ) -> str:
        """构建包含上下文的对比分析 prompt"""

        prompt = """Please compare the following two nail images:
- Image 1: Design reference (expected result)
- Image 2: Actual completed photo

Please analyze from the following dimensions:
1. **Visual comparison**: color accuracy, pattern precision, detail work, overall composition
2. **Similarity score**: 0-100 (100 = perfect match)
"""

        if artist_review:
            prompt += f"\n**Artist Review**:\n{artist_review}\n"

        if customer_feedback:
            prompt += f"\n**Customer Feedback**:\n{customer_feedback}\n"

        if customer_satisfaction:
            stars = "⭐" * customer_satisfaction
            prompt += f"\n**Customer Satisfaction**: {stars} ({customer_satisfaction}/5 stars)\n"

        prompt += """
Please combine the images and the above text information to return a JSON analysis result:

{
    "similarity_score": 92,
    "overall_assessment": "High overall completion, accurate color reproduction, excellent pattern precision.",
    "differences": {
        "color_accuracy": "Color accuracy 95%, slight color difference mainly in gradient transitions",
        "pattern_precision": "Pattern precision 90%, smooth and delicate lines",
        "detail_work": "Complete detail work, even glitter distribution",
        "composition": "Overall composition is harmonious, highly consistent with design reference"
    },
    "contextual_insights": {
        "artist_perspective": "Given the artist mentioned 'time pressure', the completion level is already excellent",
        "customer_perspective": "Customer feedback aligns with visual analysis, satisfaction score is reasonable",
        "satisfaction_analysis": "5-star rating reflects customer's high appreciation of the overall result"
    },
    "suggestions": [
        "Gradient transitions could be more natural",
        "Recommend allowing more time to improve details"
    ],
    "ability_scores": {
        "color_matching": {"score": 88, "evidence": "Color combination is harmonious, gradient transitions are natural"},
        "pattern_precision": {"score": 90, "evidence": "Lines are precise, patterns are clear"},
        "detail_work": {"score": 85, "evidence": "Glitter distribution is even, edges are handled delicately"},
        "composition": {"score": 92, "evidence": "Layout is balanced, visually well-proportioned"},
        "technique_application": {"score": 87, "evidence": "Multiple techniques applied skillfully"},
        "creative_expression": {"score": 80, "evidence": "Faithful reproduction of design, strong execution"}
    },
    "customer_updates": {
        "colors": ["Color preferences extracted from actual photo and feedback, e.g. pink, nude"],
        "styles": ["Style tags from this service, e.g. French, gradient, minimalist"],
        "notes": ["Special customer preferences or notes, e.g. dislikes glitter, prefers short nails"]
    },
    "skill_updates": {
        "strengths": ["Skills that stood out this session, e.g. natural gradient transitions"],
        "improvements": ["Skills to improve, e.g. top coat leveling"],
        "insights": ["Key insights from this service"],
        "next_suggestions": ["Improvement suggestions for next service"]
    }
}

**Important**:
- If the artist review or customer feedback mentions specific issues (e.g. "color too dark"), focus on those in the corresponding dimension analysis
- If customer satisfaction differs from visual analysis, explain the reason in contextual_insights
- customer_updates should be extracted from visual analysis + artist review + customer feedback combined, for updating customer preference profile
- skill_updates should summarize the nail artist's skill growth data based on this service's performance
- All scores must be objective and based on visual evidence
- Ensure the response is valid JSON format
"""

        return prompt.strip()
