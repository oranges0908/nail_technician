# 美甲师能力成长系统 - 技术实现文档

## 技术栈详情

### 前端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Flutter | 3.16+ | 跨平台UI框架 |
| Dart | 3.2+ | 编程语言 |
| Provider | ^6.1.1 | 状态管理 |
| Dio | ^5.4.0 | HTTP客户端 |
| image_picker | ^1.0.7 | 拍照/选图 |
| image_cropper | ^5.0.1 | 图片裁剪 |
| fl_chart | ^0.66.2 | 数据可视化（雷达图、折线图） |
| cached_network_image | ^3.3.1 | 图片缓存 |
| shared_preferences | ^2.2.2 | 本地存储 |
| go_router | ^13.0.0 | 路由导航 |
| json_serializable | ^6.7.1 | JSON序列化 |

### 后端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.11+ | 编程语言 |
| FastAPI | 0.109.0 | Web框架 |
| SQLAlchemy | 2.0.25 | ORM |
| Pydantic | 2.5.3 | 数据验证 |
| PostgreSQL | 15+ | 关系数据库 |
| Redis | 7+ | 缓存和任务队列 |
| Alembic | 最新 | 数据库迁移 |
| OpenAI Python SDK | 1.12.0 | AI服务集成 |
| Pillow | 10.2.0 | 图片处理 |
| python-jose | 最新 | JWT处理 |
| passlib | 最新 | 密码加密 |

### 三方服务

| 服务 | 用途 | 成本估算 |
|------|------|----------|
| OpenAI API | 设计生成（DALL-E 3）、图像分析（GPT-4 Vision） | $0.01-0.04/次 |

## 核心技术实现

### 1. AI Prompt工程

#### 设计生成Prompt构建（增强版）

```python
# app/services/design_service.py

class DesignService:

    @staticmethod
    def _build_design_prompt(
        customer_profile: CustomerProfile,
        inspiration_desc: str,
        custom_prompt: str = None,
        design_target: str = "single"
    ) -> str:
        """构建AI设计生成的提示词（支持自定义提示词和生成目标）"""

        # 根据生成目标设定基础提示
        target_prompts = {
            "single": "Generate a realistic nail art design photograph focusing on a single nail. ",
            "5nails": "Generate a realistic nail art design photograph showing 5 nails on one hand. ",
            "10nails": "Generate a realistic nail art design photograph showing all 10 nails on both hands. "
        }

        base_prompt = target_prompts.get(design_target, target_prompts["single"])

        # 添加客户甲型信息
        if customer_profile.nail_shape:
            base_prompt += f"Nail shape: {customer_profile.nail_shape}. "

        # 添加颜色偏好
        if customer_profile.color_preferences:
            colors = ", ".join(customer_profile.color_preferences[:3])  # 最多3个颜色
            base_prompt += f"Preferred colors: {colors}. "

        # 添加风格偏好
        if customer_profile.style_preferences:
            styles = ", ".join(customer_profile.style_preferences)
            base_prompt += f"Style: {styles}. "

        # 添加灵感描述
        base_prompt += f"\n\nDesign inspiration: {inspiration_desc}. "

        # **新增：自定义提示词**
        if custom_prompt:
            base_prompt += f"\n\nAdditional requirements: {custom_prompt}. "

        # 添加质量要求
        base_prompt += (
            "\n\nRequirements:\n"
            "- Realistic, high-quality photograph style\n"
            "- Professional nail art work\n"
            "- Clear focus on nails\n"
            "- Suitable for actual execution by nail artist\n"
            "- Incorporate customer's preferred colors and style"
        )

        # 添加生成目标的具体要求
        if design_target == "10nails":
            base_prompt += (
                "\n- Show both hands with all 10 nails visible\n"
                "- Ensure left and right hands are coordinated\n"
                "- May have accent nails with different designs"
            )
        elif design_target == "5nails":
            base_prompt += (
                "\n- Show one hand with all 5 nails visible\n"
                "- Thumb may have accent design\n"
                "- Other 4 fingers should be coordinated"
            )

        # 添加禁忌提醒
        if customer_profile.prohibitions:
            prohibitions = ", ".join(customer_profile.prohibitions)
            base_prompt += f"\n\nAvoid: {prohibitions}"

        return base_prompt

    @staticmethod
    async def generate_design(
        customer_id: int,
        inspiration_image_id: int,
        custom_prompt: str = None,
        design_target: str = "single",
        db: Session,
        user_id: int
    ) -> DesignPlan:
        """生成设计方案（增强版：支持自定义提示词和生成目标）"""

        # 1. 加载客户档案
        customer = db.query(Customer).filter_by(
            id=customer_id,
            user_id=user_id
        ).first()
        if not customer:
            raise ValueError("Customer not found")

        customer_profile = customer.profile

        # 2. 加载灵感图（这里简化，实际可以提取图片描述）
        inspiration = db.query(InspirationImage).filter_by(
            id=inspiration_image_id
        ).first()
        inspiration_desc = "elegant floral design with pastel colors"  # 简化

        # 3. 构建prompt（包含自定义提示词和生成目标）
        prompt = DesignService._build_design_prompt(
            customer_profile,
            inspiration_desc,
            custom_prompt=custom_prompt,
            design_target=design_target
        )

        # 4. 调用AI生成
        ai_provider = AIProviderFactory.get_provider()
        image_url = await ai_provider.generate_design(
            prompt=prompt,
            reference_images=[inspiration.image_path],
            design_target=design_target
        )

        # 5. 下载并保存图片
        local_path = await DesignService._download_and_save_image(
            image_url,
            f"design_{customer_id}_{int(time.time())}.jpg"
        )

        # 6. 调用AI评估落地信息
        estimation = await ai_provider.estimate_execution(image_url)

        # 7. 创建设计方案记录
        design_plan = DesignPlan(
            user_id=user_id,
            customer_id=customer_id,
            inspiration_image_ids=[inspiration_image_id],
            ai_prompt=prompt,
            custom_prompt=custom_prompt,
            design_target=design_target,
            generated_image_path=local_path,
            design_description=f"AI generated design for {customer.name}",
            estimated_duration_min=estimation.get("duration_min"),
            estimated_duration_max=estimation.get("duration_max"),
            material_list=estimation.get("materials", []),
            version=1
        )
        db.add(design_plan)
        db.commit()
        db.refresh(design_plan)

        return design_plan

    @staticmethod
    async def refine_design(
        design_id: int,
        refinement_instruction: str,
        db: Session,
        user_id: int
    ) -> DesignPlan:
        """微调已有设计方案"""

        # 1. 加载原设计
        original_design = db.query(DesignPlan).filter_by(
            id=design_id,
            user_id=user_id
        ).first()
        if not original_design:
            raise ValueError("Design not found")

        # 2. 获取原设计图片URL
        original_image_url = f"http://localhost:8000/uploads/{original_design.generated_image_path}"

        # 3. 调用AI微调
        ai_provider = AIProviderFactory.get_provider()
        refined_image_url = await ai_provider.refine_design(
            original_image=original_image_url,
            refinement_instruction=refinement_instruction
        )

        # 4. 下载并保存新图片
        local_path = await DesignService._download_and_save_image(
            refined_image_url,
            f"design_refined_{design_id}_{int(time.time())}.jpg"
        )

        # 5. 重新评估落地信息
        estimation = await ai_provider.estimate_execution(refined_image_url)

        # 6. 创建新版本设计记录（保留原设计关系）
        refined_design = DesignPlan(
            user_id=user_id,
            customer_id=original_design.customer_id,
            inspiration_image_ids=original_design.inspiration_image_ids,
            ai_prompt=original_design.ai_prompt,
            custom_prompt=original_design.custom_prompt,
            design_target=original_design.design_target,
            generated_image_path=local_path,
            design_description=f"Refined version: {refinement_instruction}",
            parent_design_id=design_id,  # 关联父设计
            refinement_prompt=refinement_instruction,
            estimated_duration_min=estimation.get("duration_min"),
            estimated_duration_max=estimation.get("duration_max"),
            material_list=estimation.get("materials", []),
            version=original_design.version + 1
        )
        db.add(refined_design)
        db.commit()
        db.refresh(refined_design)

        return refined_design

    @staticmethod
    async def get_design_with_estimation(
        design_id: int,
        db: Session,
        user_id: int
    ) -> Dict:
        """获取设计方案及其落地评估信息"""

        design = db.query(DesignPlan).filter_by(
            id=design_id,
            user_id=user_id
        ).first()

        if not design:
            raise ValueError("Design not found")

        return {
            "design": design,
            "estimation": {
                "duration_range": f"{design.estimated_duration_min}-{design.estimated_duration_max} 分钟",
                "materials": design.material_list,
                "version": design.version,
                "is_refined": design.parent_design_id is not None
            }
        }
```

#### 图像对比分析Prompt

```python
# app/services/analysis_service.py

class AnalysisService:

    @staticmethod
    def _build_comparison_prompt() -> str:
        """构建图像对比分析的提示词"""
        return """
You are an expert nail artist analyzing the quality of work.

Compare the two nail art images:
- Image 1: Design plan (what was intended)
- Image 2: Actual result (what was achieved)

Analyze and provide a JSON response with the following structure:
{
    "similarity_score": <0-100>,
    "overall_assessment": "<brief overall comment>",
    "differences": {
        "color_accuracy": "<analysis of color matching>",
        "pattern_precision": "<analysis of pattern accuracy>",
        "detail_work": "<analysis of detail execution>",
        "composition": "<analysis of overall composition>"
    },
    "skills_demonstrated": [
        "<skill 1>",
        "<skill 2>",
        ...
    ],
    "suggestions": [
        "<improvement suggestion 1>",
        "<improvement suggestion 2>",
        ...
    ]
}

Be specific, constructive, and focus on technical aspects.
Rate similarity_score considering: color match (30%), pattern accuracy (30%), detail quality (20%), overall composition (20%).
"""

    @staticmethod
    async def compare_design_and_actual(
        service_record_id: int,
        db: Session,
        user_id: int
    ) -> ComparisonResult:
        """对比设计图和实际完成图"""

        # 1. 加载服务记录
        service_record = db.query(ServiceRecord).filter_by(
            id=service_record_id,
            user_id=user_id
        ).first()
        if not service_record:
            raise ValueError("Service record not found")

        design_plan = service_record.design_plan
        if not design_plan:
            raise ValueError("No design plan associated")

        # 2. 构建图片URL（转换本地路径为可访问URL）
        design_image_url = f"http://localhost:8000/uploads/{design_plan.generated_image_path}"
        actual_image_url = f"http://localhost:8000/uploads/{service_record.actual_image_path}"

        # 3. 调用AI对比
        ai_provider = AIProviderFactory.get_provider()
        analysis_result = await ai_provider.compare_images(
            design_image=design_image_url,
            actual_image=actual_image_url
        )

        # 4. 保存对比结果
        comparison = ComparisonResult(
            service_record_id=service_record_id,
            similarity_score=analysis_result['similarity_score'],
            differences=analysis_result['differences'],
            suggestions=analysis_result['suggestions']
        )
        db.add(comparison)

        # 5. 触发能力评分更新
        await AbilityService.update_ability_from_comparison(
            user_id=user_id,
            service_record_id=service_record_id,
            analysis_result=analysis_result,
            db=db
        )

        db.commit()
        db.refresh(comparison)

        return comparison
```

### 2. 能力评分算法

#### 从AI分析结果提取能力评分

```python
# app/services/ability_service.py

class AbilityService:

    # 能力维度与AI分析结果的映射关系
    DIMENSION_MAPPING = {
        "颜色搭配": "color_accuracy",
        "图案精度": "pattern_precision",
        "细节处理": "detail_work",
        "整体构图": "composition"
    }

    @staticmethod
    async def update_ability_from_comparison(
        user_id: int,
        service_record_id: int,
        analysis_result: dict,
        db: Session
    ):
        """根据AI对比分析更新能力评分"""

        base_score = analysis_result['similarity_score']
        differences = analysis_result['differences']
        skills = analysis_result.get('skills_demonstrated', [])

        # 加载所有能力维度
        dimensions = db.query(AbilityDimension).all()

        for dimension in dimensions:
            # 计算该维度的得分
            score = AbilityService._calculate_dimension_score(
                dimension.name,
                base_score,
                differences,
                skills
            )

            # 构建评分依据
            evidence = AbilityService._build_evidence(
                dimension.name,
                differences,
                skills
            )

            # 创建能力记录
            ability_record = AbilityRecord(
                user_id=user_id,
                service_record_id=service_record_id,
                dimension_id=dimension.id,
                score=score,
                evidence=evidence
            )
            db.add(ability_record)

        db.commit()

    @staticmethod
    def _calculate_dimension_score(
        dimension_name: str,
        base_score: int,
        differences: dict,
        skills: list
    ) -> int:
        """计算单个能力维度的得分"""

        # 获取对应的AI分析字段
        analysis_key = AbilityService.DIMENSION_MAPPING.get(dimension_name)

        if not analysis_key:
            return base_score  # 无映射关系，使用基准分

        # 从差异分析中提取文本
        diff_text = differences.get(analysis_key, "")

        # 基于关键词调整分数
        score_adjustment = 0

        # 正面关键词 -> 加分
        positive_keywords = ["excellent", "precise", "accurate", "perfect", "well-done"]
        for keyword in positive_keywords:
            if keyword in diff_text.lower():
                score_adjustment += 5

        # 负面关键词 -> 减分
        negative_keywords = ["deviation", "inaccurate", "rough", "poor", "needs improvement"]
        for keyword in negative_keywords:
            if keyword in diff_text.lower():
                score_adjustment -= 5

        # 技能体现 -> 加分
        dimension_related_skills = AbilityService._get_related_skills(dimension_name)
        for skill in skills:
            if any(related in skill.lower() for related in dimension_related_skills):
                score_adjustment += 10
                break

        # 最终得分
        final_score = base_score + score_adjustment
        return max(0, min(100, final_score))  # 限制在0-100范围

    @staticmethod
    def _get_related_skills(dimension_name: str) -> list:
        """获取与能力维度相关的技能关键词"""
        skill_mapping = {
            "颜色搭配": ["color", "matching", "palette", "harmony"],
            "图案精度": ["pattern", "precision", "accuracy", "detail"],
            "细节处理": ["detail", "fine work", "delicate"],
            "整体构图": ["composition", "balance", "layout"],
            "技法运用": ["technique", "skill", "method"],
            "创意表达": ["creativity", "originality", "unique"]
        }
        return skill_mapping.get(dimension_name, [])

    @staticmethod
    def _build_evidence(
        dimension_name: str,
        differences: dict,
        skills: list
    ) -> dict:
        """构建评分依据JSON"""
        analysis_key = AbilityService.DIMENSION_MAPPING.get(dimension_name)
        return {
            "analysis": differences.get(analysis_key, ""),
            "skills_demonstrated": [s for s in skills if any(
                keyword in s.lower()
                for keyword in AbilityService._get_related_skills(dimension_name)
            )]
        }
```

#### 能力雷达图数据生成

```python
# app/services/ability_service.py

class AbilityService:

    @staticmethod
    def get_ability_radar_data(user_id: int, db: Session) -> dict:
        """获取能力雷达图数据"""

        # 1. 获取所有能力维度
        dimensions = db.query(AbilityDimension).all()

        # 2. 计算每个维度的最新平均分（最近10次服务）
        radar_data = []

        for dimension in dimensions:
            # 查询最近10次该维度的评分
            recent_scores = db.query(AbilityRecord.score).filter(
                AbilityRecord.user_id == user_id,
                AbilityRecord.dimension_id == dimension.id
            ).order_by(
                AbilityRecord.recorded_at.desc()
            ).limit(10).all()

            if recent_scores:
                avg_score = sum(s[0] for s in recent_scores) / len(recent_scores)
            else:
                avg_score = 0

            radar_data.append({
                "dimension": dimension.name,
                "score": round(avg_score, 1),
                "count": len(recent_scores)
            })

        # 3. 计算综合评分
        overall_score = sum(d['score'] for d in radar_data) / len(radar_data) if radar_data else 0

        return {
            "dimensions": radar_data,
            "overall_score": round(overall_score, 1),
            "total_services": db.query(ServiceRecord).filter_by(
                user_id=user_id,
                status='completed'
            ).count()
        }

    @staticmethod
    def get_growth_trend(user_id: int, dimension_id: int, db: Session) -> list:
        """获取某个能力维度的成长曲线数据"""

        # 按月统计平均分
        from sqlalchemy import func, extract

        results = db.query(
            extract('year', AbilityRecord.recorded_at).label('year'),
            extract('month', AbilityRecord.recorded_at).label('month'),
            func.avg(AbilityRecord.score).label('avg_score')
        ).filter(
            AbilityRecord.user_id == user_id,
            AbilityRecord.dimension_id == dimension_id
        ).group_by(
            'year', 'month'
        ).order_by(
            'year', 'month'
        ).all()

        return [
            {
                "period": f"{int(r.year)}-{int(r.month):02d}",
                "score": round(r.avg_score, 1)
            }
            for r in results
        ]

    @staticmethod
    def get_strength_and_weakness(user_id: int, db: Session) -> dict:
        """获取擅长和待提升的能力领域"""

        radar_data = AbilityService.get_ability_radar_data(user_id, db)
        dimensions = radar_data['dimensions']

        # 按分数排序
        sorted_dims = sorted(dimensions, key=lambda x: x['score'], reverse=True)

        return {
            "strengths": sorted_dims[:3],  # 前3个擅长领域
            "weaknesses": sorted_dims[-3:] if len(sorted_dims) >= 3 else sorted_dims  # 后3个待提升
        }
```

### 3. 文件上传和处理

#### 文件上传接口

```python
# app/api/v1/upload.py

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.core.file_upload import save_upload_file
from app.core.security import get_current_user

router = APIRouter()

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    category: str = "general",  # nails, inspirations, designs, actuals
    current_user: User = Depends(get_current_user)
):
    """上传文件"""

    # 验证文件类型
    allowed_types = ["image/jpeg", "image/png", "image/jpg"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed: {allowed_types}"
        )

    # 验证文件大小（10MB）
    file_size = 0
    content = await file.read()
    file_size = len(content)
    await file.seek(0)  # 重置文件指针

    if file_size > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(
            status_code=400,
            detail="File size exceeds 10MB limit"
        )

    # 保存文件
    try:
        file_path = await save_upload_file(
            file=file,
            category=category,
            user_id=current_user.id
        )
        return {
            "file_path": file_path,
            "file_size": file_size,
            "content_type": file.content_type
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")
```

#### 文件保存工具

```python
# app/core/file_upload.py

import os
import uuid
import aiofiles
from fastapi import UploadFile
from app.core.config import settings

async def save_upload_file(
    file: UploadFile,
    category: str,
    user_id: int
) -> str:
    """保存上传的文件到本地"""

    # 生成文件名
    file_ext = os.path.splitext(file.filename)[1]  # .jpg
    unique_filename = f"{category}_{user_id}_{uuid.uuid4().hex}{file_ext}"

    # 确定保存目录
    upload_dir = os.path.join(settings.UPLOAD_DIR, category)
    os.makedirs(upload_dir, exist_ok=True)

    # 完整路径
    file_path = os.path.join(upload_dir, unique_filename)

    # 异步保存文件
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)

    # 返回相对路径（用于数据库存储和URL访问）
    relative_path = os.path.join(category, unique_filename)
    return relative_path

def get_file_url(file_path: str) -> str:
    """将文件路径转换为可访问的URL"""
    return f"{settings.BASE_URL}/uploads/{file_path}"
```

#### 图片压缩和处理

```python
# app/core/image_processing.py

from PIL import Image
import os

def compress_image(
    input_path: str,
    output_path: str = None,
    max_size: tuple = (1024, 1024),
    quality: int = 85
):
    """压缩图片"""

    if output_path is None:
        output_path = input_path

    with Image.open(input_path) as img:
        # 转换为RGB（如果是RGBA）
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')

        # 按比例缩放
        img.thumbnail(max_size, Image.Resampling.LANCZOS)

        # 保存
        img.save(output_path, 'JPEG', quality=quality, optimize=True)

    return output_path

def create_thumbnail(
    input_path: str,
    output_path: str,
    size: tuple = (200, 200)
):
    """创建缩略图"""

    with Image.open(input_path) as img:
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')

        img.thumbnail(size, Image.Resampling.LANCZOS)
        img.save(output_path, 'JPEG', quality=80)

    return output_path
```

### 4. 数据库操作最佳实践

#### 使用SQLAlchemy会话

```python
# 推荐：使用依赖注入
@router.get("/customers/{customer_id}")
async def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),  # 自动管理session生命周期
    current_user: User = Depends(get_current_user)
):
    customer = db.query(Customer).filter_by(
        id=customer_id,
        user_id=current_user.id
    ).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return customer
    # session会自动关闭
```

#### 批量操作优化

```python
# 不推荐：N+1查询问题
customers = db.query(Customer).filter_by(user_id=user_id).all()
for customer in customers:
    profile = customer.profile  # 每次都会触发一次查询

# 推荐：使用joinedload预加载关联数据
from sqlalchemy.orm import joinedload

customers = db.query(Customer).options(
    joinedload(Customer.profile)
).filter_by(user_id=user_id).all()

for customer in customers:
    profile = customer.profile  # 不会触发额外查询
```

#### 事务处理

```python
from sqlalchemy.exc import SQLAlchemyError

@router.post("/services/{service_id}/complete")
async def complete_service(
    service_id: int,
    actual_image: UploadFile,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # 开始事务
        service_record = db.query(ServiceRecord).filter_by(
            id=service_id,
            user_id=current_user.id
        ).with_for_update().first()  # 行锁

        if not service_record:
            raise HTTPException(status_code=404, detail="Service not found")

        # 上传图片
        file_path = await save_upload_file(actual_image, "actuals", current_user.id)

        # 更新服务记录
        service_record.actual_image_path = file_path
        service_record.status = "completed"
        service_record.completed_at = datetime.utcnow()

        # 触发AI分析
        comparison = await AnalysisService.compare_design_and_actual(
            service_id, db, current_user.id
        )

        # 提交事务
        db.commit()
        db.refresh(service_record)

        return {
            "service_record": service_record,
            "comparison": comparison
        }

    except SQLAlchemyError as e:
        db.rollback()  # 回滚
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
```

### 5. 异步任务处理（Celery）

#### Celery配置

```python
# app/core/celery_app.py

from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "nail_tasks",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)
```

#### 异步任务示例

```python
# app/tasks/ai_tasks.py

from app.core.celery_app import celery_app
from app.services.ai.factory import AIProviderFactory
from app.db.database import SessionLocal

@celery_app.task(name="generate_design_async")
def generate_design_async(
    customer_id: int,
    inspiration_id: int,
    user_id: int
):
    """异步生成设计（避免阻塞API响应）"""

    db = SessionLocal()
    try:
        # 执行设计生成
        design_plan = await DesignService.generate_design(
            customer_id=customer_id,
            inspiration_image_id=inspiration_id,
            db=db,
            user_id=user_id
        )

        return {
            "status": "success",
            "design_id": design_plan.id
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
    finally:
        db.close()

@celery_app.task(name="analyze_comparison_async")
def analyze_comparison_async(service_record_id: int, user_id: int):
    """异步执行AI对比分析"""

    db = SessionLocal()
    try:
        comparison = await AnalysisService.compare_design_and_actual(
            service_record_id=service_record_id,
            db=db,
            user_id=user_id
        )

        return {
            "status": "success",
            "comparison_id": comparison.id
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
    finally:
        db.close()
```

#### API中调用异步任务（增强版）

```python
# app/api/v1/designs.py

from app.tasks.ai_tasks import generate_design_async, refine_design_async
from pydantic import BaseModel

class DesignGenerateRequest(BaseModel):
    customer_id: int
    inspiration_id: int
    custom_prompt: str = None
    design_target: str = "single"  # single/5nails/10nails

class DesignRefineRequest(BaseModel):
    design_id: int
    refinement_instruction: str

@router.post("/generate")
async def generate_design_endpoint(
    request: DesignGenerateRequest,
    current_user: User = Depends(get_current_user)
):
    """触发AI设计生成（异步，支持自定义提示词和生成目标）"""

    # 提交到Celery任务队列
    task = generate_design_async.delay(
        customer_id=request.customer_id,
        inspiration_id=request.inspiration_id,
        custom_prompt=request.custom_prompt,
        design_target=request.design_target,
        user_id=current_user.id
    )

    return {
        "task_id": task.id,
        "status": "pending",
        "message": "Design generation started. Check status with task_id."
    }

@router.post("/refine")
async def refine_design_endpoint(
    request: DesignRefineRequest,
    current_user: User = Depends(get_current_user)
):
    """触发AI设计微调（异步）"""

    # 提交到Celery任务队列
    task = refine_design_async.delay(
        design_id=request.design_id,
        refinement_instruction=request.refinement_instruction,
        user_id=current_user.id
    )

    return {
        "task_id": task.id,
        "status": "pending",
        "message": "Design refinement started. Check status with task_id."
    }

@router.get("/{design_id}/estimation")
async def get_design_estimation(
    design_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取设计的落地评估信息"""

    result = await DesignService.get_design_with_estimation(
        design_id=design_id,
        db=db,
        user_id=current_user.id
    )

    return result

@router.get("/{design_id}/versions")
async def get_design_versions(
    design_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取设计的所有版本（原始设计 + 微调版本）"""

    # 查找原始设计
    design = db.query(DesignPlan).filter_by(
        id=design_id,
        user_id=current_user.id
    ).first()

    if not design:
        raise HTTPException(status_code=404, detail="Design not found")

    # 如果这是微调版本，找到根设计
    root_design_id = design.parent_design_id or design_id

    # 查找所有版本（包括根设计和所有微调版本）
    all_versions = db.query(DesignPlan).filter(
        (DesignPlan.id == root_design_id) |
        (DesignPlan.parent_design_id == root_design_id)
    ).order_by(DesignPlan.version.asc()).all()

    return {
        "root_design_id": root_design_id,
        "versions": all_versions,
        "total_versions": len(all_versions)
    }

@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """查询任务状态"""

    from celery.result import AsyncResult

    task = AsyncResult(task_id, app=celery_app)

    if task.state == 'PENDING':
        response = {
            "state": task.state,
            "status": "Task is waiting..."
        }
    elif task.state == 'SUCCESS':
        response = {
            "state": task.state,
            "result": task.result
        }
    elif task.state == 'FAILURE':
        response = {
            "state": task.state,
            "error": str(task.info)
        }
    else:
        response = {
            "state": task.state
        }

    return response
```

### 6. 前端关键实现

#### API Service封装

```dart
// lib/services/api_service.dart

import 'package:dio/dio.dart';
import 'package:nail_app/config/api_config.dart';
import 'package:nail_app/services/storage_service.dart';

class ApiService {
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;

  late Dio _dio;

  ApiService._internal() {
    _dio = Dio(BaseOptions(
      baseUrl: ApiConfig.baseUrl,
      connectTimeout: ApiConfig.timeout,
      receiveTimeout: ApiConfig.timeout,
    ));

    // 添加拦截器
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        // 添加JWT token
        final token = await StorageService().getToken();
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        return handler.next(options);
      },
      onError: (error, handler) {
        // 统一错误处理
        if (error.response?.statusCode == 401) {
          // Token过期，跳转登录
          // NavigationService.pushNamedAndRemoveUntil('/login');
        }
        return handler.next(error);
      },
    ));
  }

  Dio get dio => _dio;
}
```

#### 设计生成服务（增强版）

```dart
// lib/services/design_service.dart

import 'package:dio/dio.dart';
import 'package:nail_app/models/design_plan.dart';
import 'package:nail_app/services/api_service.dart';

class DesignService {
  final Dio _dio = ApiService().dio;

  Future<Map<String, dynamic>> generateDesign({
    required int customerId,
    required int inspirationId,
    String? customPrompt,
    String designTarget = 'single',  // single/5nails/10nails
  }) async {
    try {
      final response = await _dio.post(
        '/designs/generate',
        data: {
          'customer_id': customerId,
          'inspiration_id': inspirationId,
          'custom_prompt': customPrompt,
          'design_target': designTarget,
        },
      );

      return response.data;
    } on DioException catch (e) {
      throw Exception('Failed to generate design: ${e.message}');
    }
  }

  Future<Map<String, dynamic>> refineDesign({
    required int designId,
    required String refinementInstruction,
  }) async {
    try {
      final response = await _dio.post(
        '/designs/refine',
        data: {
          'design_id': designId,
          'refinement_instruction': refinementInstruction,
        },
      );

      return response.data;
    } on DioException catch (e) {
      throw Exception('Failed to refine design: ${e.message}');
    }
  }

  Future<Map<String, dynamic>> getDesignEstimation(int designId) async {
    try {
      final response = await _dio.get('/designs/$designId/estimation');
      return response.data;
    } catch (e) {
      throw Exception('Failed to get design estimation: $e');
    }
  }

  Future<List<DesignPlan>> getDesignVersions(int designId) async {
    try {
      final response = await _dio.get('/designs/$designId/versions');
      final versions = (response.data['versions'] as List)
          .map((v) => DesignPlan.fromJson(v))
          .toList();
      return versions;
    } catch (e) {
      throw Exception('Failed to get design versions: $e');
    }
  }

  Future<String> getTaskStatus(String taskId) async {
    try {
      final response = await _dio.get('/designs/tasks/$taskId');
      return response.data['state'];
    } catch (e) {
      throw Exception('Failed to get task status: $e');
    }
  }

  Future<DesignPlan> getDesignById(int designId) async {
    try {
      final response = await _dio.get('/designs/$designId');
      return DesignPlan.fromJson(response.data);
    } catch (e) {
      throw Exception('Failed to get design: $e');
    }
  }
}
```

#### Provider状态管理（增强版）

```dart
// lib/providers/design_provider.dart

import 'package:flutter/foundation.dart';
import 'package:nail_app/models/design_plan.dart';
import 'package:nail_app/services/design_service.dart';

class DesignProvider with ChangeNotifier {
  final DesignService _designService = DesignService();

  bool _isGenerating = false;
  bool _isRefining = false;
  String? _currentTaskId;
  DesignPlan? _currentDesign;
  Map<String, dynamic>? _currentEstimation;
  List<DesignPlan>? _designVersions;
  String? _error;

  bool get isGenerating => _isGenerating;
  bool get isRefining => _isRefining;
  DesignPlan? get currentDesign => _currentDesign;
  Map<String, dynamic>? get currentEstimation => _currentEstimation;
  List<DesignPlan>? get designVersions => _designVersions;
  String? get error => _error;

  Future<void> generateDesign({
    required int customerId,
    required int inspirationId,
    String? customPrompt,
    String designTarget = 'single',
  }) async {
    _isGenerating = true;
    _error = null;
    _currentEstimation = null;
    notifyListeners();

    try {
      // 1. 提交生成任务
      final result = await _designService.generateDesign(
        customerId: customerId,
        inspirationId: inspirationId,
        customPrompt: customPrompt,
        designTarget: designTarget,
      );

      _currentTaskId = result['task_id'];

      // 2. 轮询任务状态
      await _pollTaskStatus();

    } catch (e) {
      _error = e.toString();
      _isGenerating = false;
      notifyListeners();
    }
  }

  Future<void> refineDesign({
    required int designId,
    required String refinementInstruction,
  }) async {
    _isRefining = true;
    _error = null;
    notifyListeners();

    try {
      // 1. 提交微调任务
      final result = await _designService.refineDesign(
        designId: designId,
        refinementInstruction: refinementInstruction,
      );

      _currentTaskId = result['task_id'];

      // 2. 轮询任务状态
      await _pollTaskStatus(isRefinement: true);

    } catch (e) {
      _error = e.toString();
      _isRefining = false;
      notifyListeners();
    }
  }

  Future<void> loadDesignEstimation(int designId) async {
    try {
      _currentEstimation = await _designService.getDesignEstimation(designId);
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> loadDesignVersions(int designId) async {
    try {
      _designVersions = await _designService.getDesignVersions(designId);
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> _pollTaskStatus({bool isRefinement = false}) async {
    if (_currentTaskId == null) return;

    while (true) {
      await Future.delayed(Duration(seconds: 2));

      try {
        final status = await _designService.getTaskStatus(_currentTaskId!);

        if (status == 'SUCCESS') {
          // 任务成功，加载设计详情
          // （简化，实际应从task result中获取design_id）
          if (isRefinement) {
            _isRefining = false;
          } else {
            _isGenerating = false;
          }
          notifyListeners();
          break;
        } else if (status == 'FAILURE') {
          _error = isRefinement
              ? 'Design refinement failed'
              : 'Design generation failed';
          if (isRefinement) {
            _isRefining = false;
          } else {
            _isGenerating = false;
          }
          notifyListeners();
          break;
        }
        // PENDING状态继续轮询
      } catch (e) {
        _error = e.toString();
        if (isRefinement) {
          _isRefining = false;
        } else {
          _isGenerating = false;
        }
        notifyListeners();
        break;
      }
    }
  }

  void clearError() {
    _error = null;
    notifyListeners();
  }
}
```

#### 能力雷达图Widget

```dart
// lib/widgets/charts/radar_chart_widget.dart

import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';

class AbilityRadarChart extends StatelessWidget {
  final List<RadarDataPoint> dataPoints;

  const AbilityRadarChart({Key? key, required this.dataPoints}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return RadarChart(
      RadarChartData(
        radarShape: RadarShape.polygon,
        tickCount: 5,
        ticksTextStyle: TextStyle(color: Colors.grey, fontSize: 10),
        tickBorderData: BorderSide(color: Colors.grey.shade300),
        gridBorderData: BorderSide(color: Colors.grey.shade300, width: 1),
        radarBorderData: BorderSide(color: Colors.black, width: 2),
        titlePositionPercentageOffset: 0.2,
        getTitle: (index, angle) {
          return RadarChartTitle(
            text: dataPoints[index].label,
            angle: angle,
          );
        },
        dataSets: [
          RadarDataSet(
            fillColor: Colors.blue.withOpacity(0.3),
            borderColor: Colors.blue,
            borderWidth: 2,
            dataEntries: dataPoints.map((point) {
              return RadarEntry(value: point.value);
            }).toList(),
          ),
        ],
      ),
    );
  }
}

class RadarDataPoint {
  final String label;
  final double value;

  RadarDataPoint({required this.label, required this.value});
}
```

### 7. 前端UI组件示例（新功能）

#### 设计生成页面示例

```dart
// lib/screens/design/design_generate_screen.dart

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:nail_app/providers/design_provider.dart';

class DesignGenerateScreen extends StatefulWidget {
  final int customerId;
  final int inspirationId;

  const DesignGenerateScreen({
    Key? key,
    required this.customerId,
    required this.inspirationId,
  }) : super(key: key);

  @override
  State<DesignGenerateScreen> createState() => _DesignGenerateScreenState();
}

class _DesignGenerateScreenState extends State<DesignGenerateScreen> {
  final TextEditingController _customPromptController = TextEditingController();
  String _selectedTarget = 'single';

  @override
  Widget build(BuildContext context) {
    final designProvider = Provider.of<DesignProvider>(context);

    return Scaffold(
      appBar: AppBar(title: Text('生成设计方案')),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 生成目标选择
            Text('生成目标', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: _buildTargetButton('单指甲', 'single'),
                ),
                SizedBox(width: 8),
                Expanded(
                  child: _buildTargetButton('5指（单手）', '5nails'),
                ),
                SizedBox(width: 8),
                Expanded(
                  child: _buildTargetButton('10指（双手）', '10nails'),
                ),
              ],
            ),

            SizedBox(height: 24),

            // 自定义提示词输入
            Text('自定义提示词（可选）', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            SizedBox(height: 8),
            TextField(
              controller: _customPromptController,
              maxLines: 3,
              decoration: InputDecoration(
                hintText: '例如：增加金色点缀、颜色更亮一些...',
                border: OutlineInputBorder(),
              ),
            ),

            SizedBox(height: 32),

            // 生成按钮
            SizedBox(
              width: double.infinity,
              height: 48,
              child: ElevatedButton(
                onPressed: designProvider.isGenerating
                    ? null
                    : () => _generateDesign(designProvider),
                child: designProvider.isGenerating
                    ? Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          ),
                          SizedBox(width: 12),
                          Text('生成中...'),
                        ],
                      )
                    : Text('生成设计'),
              ),
            ),

            // 错误提示
            if (designProvider.error != null)
              Padding(
                padding: EdgeInsets.only(top: 16),
                child: Text(
                  designProvider.error!,
                  style: TextStyle(color: Colors.red),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildTargetButton(String label, String value) {
    final isSelected = _selectedTarget == value;
    return OutlinedButton(
      onPressed: () {
        setState(() {
          _selectedTarget = value;
        });
      },
      style: OutlinedButton.styleFrom(
        backgroundColor: isSelected ? Colors.blue : Colors.transparent,
        foregroundColor: isSelected ? Colors.white : Colors.blue,
      ),
      child: Text(label),
    );
  }

  Future<void> _generateDesign(DesignProvider provider) async {
    await provider.generateDesign(
      customerId: widget.customerId,
      inspirationId: widget.inspirationId,
      customPrompt: _customPromptController.text.trim().isEmpty
          ? null
          : _customPromptController.text.trim(),
      designTarget: _selectedTarget,
    );

    if (provider.error == null && provider.currentDesign != null) {
      // 生成成功，跳转到设计详情页
      Navigator.pushReplacementNamed(
        context,
        '/design/detail',
        arguments: provider.currentDesign!.id,
      );
    }
  }

  @override
  void dispose() {
    _customPromptController.dispose();
    super.dispose();
  }
}
```

#### 设计微调对话框

```dart
// lib/widgets/design/design_refine_dialog.dart

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:nail_app/providers/design_provider.dart';

class DesignRefineDialog extends StatefulWidget {
  final int designId;

  const DesignRefineDialog({Key? key, required this.designId}) : super(key: key);

  @override
  State<DesignRefineDialog> createState() => _DesignRefineDialogState();
}

class _DesignRefineDialogState extends State<DesignRefineDialog> {
  final TextEditingController _instructionController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    final designProvider = Provider.of<DesignProvider>(context);

    return AlertDialog(
      title: Text('微调设计'),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('请描述您希望调整的内容：'),
          SizedBox(height: 12),
          TextField(
            controller: _instructionController,
            maxLines: 3,
            decoration: InputDecoration(
              hintText: '例如：颜色调亮20%、增加金色点缀...',
              border: OutlineInputBorder(),
            ),
          ),
          if (designProvider.error != null)
            Padding(
              padding: EdgeInsets.only(top: 12),
              child: Text(
                designProvider.error!,
                style: TextStyle(color: Colors.red, fontSize: 12),
              ),
            ),
        ],
      ),
      actions: [
        TextButton(
          onPressed: designProvider.isRefining ? null : () => Navigator.pop(context),
          child: Text('取消'),
        ),
        ElevatedButton(
          onPressed: designProvider.isRefining
              ? null
              : () => _refineDesign(designProvider),
          child: designProvider.isRefining
              ? SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : Text('微调'),
        ),
      ],
    );
  }

  Future<void> _refineDesign(DesignProvider provider) async {
    final instruction = _instructionController.text.trim();
    if (instruction.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('请输入调整指令')),
      );
      return;
    }

    await provider.refineDesign(
      designId: widget.designId,
      refinementInstruction: instruction,
    );

    if (provider.error == null) {
      Navigator.pop(context);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('设计微调成功！')),
      );
    }
  }

  @override
  void dispose() {
    _instructionController.dispose();
    super.dispose();
  }
}
```

#### 落地评估展示组件

```dart
// lib/widgets/design/design_estimation_card.dart

import 'package:flutter/material.dart';

class DesignEstimationCard extends StatelessWidget {
  final Map<String, dynamic> estimation;

  const DesignEstimationCard({Key? key, required this.estimation}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final design = estimation['design'];
    final estimationData = estimation['estimation'];

    return Card(
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 标题
            Row(
              children: [
                Icon(Icons.assessment, color: Colors.blue),
                SizedBox(width: 8),
                Text(
                  '落地评估',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            Divider(height: 24),

            // 耗时评估
            _buildEstimationRow(
              icon: Icons.timer,
              label: '预估耗时',
              value: estimationData['duration_range'],
            ),

            SizedBox(height: 12),

            // 用料清单
            _buildMaterialsList(estimationData['materials']),

            SizedBox(height: 12),

            // 版本信息
            if (estimationData['is_refined'])
              Chip(
                label: Text('微调版本 v${estimationData['version']}'),
                backgroundColor: Colors.orange.shade100,
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildEstimationRow({
    required IconData icon,
    required String label,
    required String value,
  }) {
    return Row(
      children: [
        Icon(icon, size: 20, color: Colors.grey[600]),
        SizedBox(width: 8),
        Text(
          '$label: ',
          style: TextStyle(fontWeight: FontWeight.w500),
        ),
        Text(value),
      ],
    );
  }

  Widget _buildMaterialsList(List<dynamic> materials) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(Icons.palette, size: 20, color: Colors.grey[600]),
            SizedBox(width: 8),
            Text(
              '用料清单:',
              style: TextStyle(fontWeight: FontWeight.w500),
            ),
          ],
        ),
        SizedBox(height: 8),
        ...materials.map((material) {
          final name = material['name'];
          final amount = material['amount'];
          final type = material['type'];

          IconData typeIcon;
          Color typeColor;

          switch (type) {
            case 'polish':
              typeIcon = Icons.opacity;
              typeColor = Colors.pink;
              break;
            case 'decoration':
              typeIcon = Icons.star;
              typeColor = Colors.amber;
              break;
            case 'tool':
              typeIcon = Icons.build;
              typeColor = Colors.grey;
              break;
            default:
              typeIcon = Icons.circle;
              typeColor = Colors.blue;
          }

          return Padding(
            padding: EdgeInsets.only(left: 28, bottom: 4),
            child: Row(
              children: [
                Icon(typeIcon, size: 16, color: typeColor),
                SizedBox(width: 8),
                Text('$name ($amount)'),
              ],
            ),
          );
        }).toList(),
      ],
    );
  }
}
```

### 8. 环境配置

#### 后端环境变量（.env）

```bash
# 应用配置
APP_NAME=Nail
APP_VERSION=1.0.0
DEBUG=True
HOST=0.0.0.0
PORT=8000

# 数据库
DATABASE_URL=postgresql://user:password@localhost:5432/nail_db
# 开发环境可用SQLite
# DATABASE_URL=sqlite:///./nail.db

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# JWT
SECRET_KEY=your-secret-key-change-in-production-please-use-long-random-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# OpenAI
OPENAI_API_KEY=sk-your-api-key-here
AI_PROVIDER=openai

# 文件上传
UPLOAD_DIR=uploads
MAX_UPLOAD_SIZE=10485760  # 10MB
BASE_URL=http://localhost:8000

# CORS
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8080"]
```

#### 前端API配置

```dart
// lib/config/api_config.dart

class ApiConfig {
  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://localhost:8000/api/v1',
  );

  static const Duration timeout = Duration(seconds: 60);

  // API端点
  static const String loginEndpoint = '/auth/login';
  static const String customersEndpoint = '/customers';
  static const String designsEndpoint = '/designs';
  static const String servicesEndpoint = '/services';
  static const String analysisEndpoint = '/analysis';
  static const String uploadEndpoint = '/upload';
}
```

### 8. 测试策略

#### 后端单元测试

```python
# backend/tests/test_design_service.py

import pytest
from app.services.design_service import DesignService

@pytest.mark.asyncio
async def test_generate_design(db_session, test_customer, test_inspiration):
    """测试设计生成"""

    design_plan = await DesignService.generate_design(
        customer_id=test_customer.id,
        inspiration_image_id=test_inspiration.id,
        db=db_session,
        user_id=test_customer.user_id
    )

    assert design_plan is not None
    assert design_plan.customer_id == test_customer.id
    assert design_plan.generated_image_path is not None

def test_build_design_prompt(test_customer_profile):
    """测试Prompt构建"""

    prompt = DesignService._build_design_prompt(
        customer_profile=test_customer_profile,
        inspiration_desc="Elegant floral design"
    )

    assert "Nail shape" in prompt
    assert "Preferred colors" in prompt
    assert "floral design" in prompt
```

#### 前端Widget测试

```dart
// test/widgets/radar_chart_test.dart

import 'package:flutter_test/flutter_test.dart';
import 'package:nail_app/widgets/charts/radar_chart_widget.dart';

void main() {
  testWidgets('Radar chart displays data points', (WidgetTester tester) async {
    final dataPoints = [
      RadarDataPoint(label: '颜色搭配', value: 85.0),
      RadarDataPoint(label: '图案精度', value: 78.0),
      RadarDataPoint(label: '细节处理', value: 90.0),
    ];

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: AbilityRadarChart(dataPoints: dataPoints),
        ),
      ),
    );

    // 验证图表渲染
    expect(find.byType(RadarChart), findsOneWidget);
  });
}
```

### 9. 性能优化

#### 数据库查询优化

```python
# 使用索引
CREATE INDEX idx_service_records_user_date ON service_records(user_id, service_date DESC);

# 使用分页
@router.get("/services")
async def list_services(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    services = db.query(ServiceRecord).filter_by(
        user_id=current_user.id
    ).order_by(
        ServiceRecord.service_date.desc()
    ).offset(skip).limit(limit).all()

    return services
```

#### 前端图片缓存

```dart
// 使用cached_network_image
CachedNetworkImage(
  imageUrl: 'http://localhost:8000/uploads/designs/design_1.jpg',
  placeholder: (context, url) => CircularProgressIndicator(),
  errorWidget: (context, url, error) => Icon(Icons.error),
  cacheKey: 'design_1',
  maxHeightDiskCache: 1000,
  maxWidthDiskCache: 1000,
)
```

#### AI成本优化

```python
# 缓存AI结果
import hashlib
import json

def get_ai_cache_key(prompt: str) -> str:
    return hashlib.md5(prompt.encode()).hexdigest()

async def generate_design_with_cache(prompt: str):
    cache_key = f"ai:design:{get_ai_cache_key(prompt)}"

    # 尝试从Redis获取缓存
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    # 调用AI生成
    result = await ai_provider.generate_design(prompt)

    # 缓存结果（7天）
    await redis_client.setex(
        cache_key,
        7 * 24 * 3600,
        json.dumps(result)
    )

    return result
```

## 开发工具和流程

### 代码质量工具

```bash
# 后端
black .                # 代码格式化
flake8                 # 代码检查
mypy app              # 类型检查
pytest                # 运行测试

# 前端
flutter format .       # 代码格式化
flutter analyze        # 静态分析
flutter test          # 运行测试
```

### Git工作流

```bash
# 功能分支
git checkout -b feature/ai-design-generation

# 提交代码
git add .
git commit -m "feat: implement AI design generation"

# 合并到main
git checkout main
git merge feature/ai-design-generation
```

### 数据库迁移

```bash
# 创建迁移
alembic revision --autogenerate -m "Add comparison_results table"

# 应用迁移
alembic upgrade head

# 回滚
alembic downgrade -1
```
