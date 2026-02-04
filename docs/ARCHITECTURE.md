# 美甲师能力成长系统 - 系统架构文档

## 架构概述

本系统采用**前后端分离**架构，前端使用Flutter构建跨平台移动应用，后端使用FastAPI提供RESTful API服务，通过AI代理层集成第三方AI能力。

### 架构原则

1. **分层解耦**：UI层、业务层、数据层、AI服务层清晰分离
2. **AI可替换**：通过抽象代理层，支持未来切换不同AI服务
3. **数据驱动**：所有能力分析基于真实服务数据
4. **移动优先**：针对移动端场景优化交互和性能
5. **简化部署**：单租户架构，降低运维复杂度

## 系统架构图

### 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Flutter Mobile App                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Presentation Layer                       │   │
│  │  ┌──────────┬──────────┬──────────┬─────────────┐    │   │
│  │  │客户管理  │智能设计  │服务记录  │能力中心     │    │   │
│  │  │Screens   │Screens   │Screens   │Screens      │    │   │
│  │  └──────────┴──────────┴──────────┴─────────────┘    │   │
│  └──────────────────────┬───────────────────────────────┘   │
│  ┌──────────────────────┴───────────────────────────────┐   │
│  │           State Management Layer (Provider)           │   │
│  │  Customer│Design│Service│Ability Providers            │   │
│  └──────────────────────┬───────────────────────────────┘   │
│  ┌──────────────────────┴───────────────────────────────┐   │
│  │               Service Layer (API Calls)               │   │
│  │  CustomerService│DesignService│AnalysisService        │   │
│  └──────────────────────┬───────────────────────────────┘   │
│  ┌──────────────────────┴───────────────────────────────┐   │
│  │          Data Layer (Models + Local Cache)            │   │
│  └───────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST API (JSON)
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Backend                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │               API Gateway Layer                       │   │
│  │  [JWT Auth] [CORS] [Rate Limit] [Error Handler]      │   │
│  └──────────────────────┬───────────────────────────────┘   │
│  ┌──────────────────────┴───────────────────────────────┐   │
│  │              API Routes (v1)                          │   │
│  │  /customers│/designs│/services│/analysis│/abilities   │   │
│  └──────────────────────┬───────────────────────────────┘   │
│  ┌──────────────────────┴───────────────────────────────┐   │
│  │            Business Service Layer                     │   │
│  │  CustomerService                                      │   │
│  │  DesignService ────→ [调用AI代理层]                  │   │
│  │  ServiceRecordService                                 │   │
│  │  AnalysisService ───→ [调用AI代理层]                 │   │
│  │  AbilityService                                       │   │
│  └──────────────────────┬───────────────────────────────┘   │
│  ┌──────────────────────┴───────────────────────────────┐   │
│  │         ORM Layer (SQLAlchemy Models)                 │   │
│  └──────────────────────┬───────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         ↓
        ┌────────────────┴───────────────┐
        ↓                                 ↓
┌──────────────────┐            ┌─────────────────────┐
│   Data Storage   │            │  AI Service Layer   │
│  ┌─────────────┐ │            │  ┌───────────────┐  │
│  │ PostgreSQL  │ │            │  │ AI Provider   │  │
│  │ (业务数据)  │ │            │  │   Factory     │  │
│  │             │ │            │  └───────┬───────┘  │
│  │ - users     │ │            │          ↓          │
│  │ - customers │ │            │  ┌───────────────┐  │
│  │ - designs   │ │            │  │OpenAI Provider│  │
│  │ - services  │ │            │  │               │  │
│  │ - abilities │ │            │  │- DALL-E 3     │  │
│  └─────────────┘ │            │  │- GPT-4 Vision │  │
│  ┌─────────────┐ │            │  └───────┬───────┘  │
│  │   Redis     │ │            │          ↓          │
│  │ (缓存队列)  │ │            │  ┌───────────────┐  │
│  │             │ │            │  │ 百度AI (预留) │  │
│  │ - Sessions  │ │            │  │ 其他AI (预留) │  │
│  │ - AI Cache  │ │            │  └───────────────┘  │
│  └─────────────┘ │            └─────────────────────┘
│  ┌─────────────┐ │
│  │ Local Files │ │
│  │ (图片存储)  │ │
│  │             │ │
│  │ uploads/    │ │
│  │ - nails/    │ │
│  │ - designs/  │ │
│  │ - actuals/  │ │
│  └─────────────┘ │
└──────────────────┘
```

## 核心架构设计

### 1. 前端架构（Flutter）

#### 分层设计

```
lib/
├── config/              # 配置层
│   ├── api_config.dart       # API端点配置
│   ├── app_config.dart       # 应用全局配置
│   └── theme_config.dart     # 主题配置
│
├── models/              # 数据模型层
│   ├── customer.dart
│   ├── customer_profile.dart
│   ├── design_plan.dart
│   ├── service_record.dart
│   ├── comparison_result.dart
│   └── ability_data.dart
│
├── services/            # 服务层（API调用）
│   ├── api_service.dart      # Dio HTTP客户端封装
│   ├── customer_service.dart
│   ├── design_service.dart
│   ├── service_service.dart
│   ├── analysis_service.dart
│   └── storage_service.dart  # SharedPreferences封装
│
├── providers/           # 状态管理层（Provider）
│   ├── auth_provider.dart
│   ├── customer_provider.dart
│   ├── design_provider.dart
│   ├── service_provider.dart
│   └── ability_provider.dart
│
├── screens/             # 页面层
│   ├── customer/
│   ├── design/
│   ├── service/
│   └── ability/
│
├── widgets/             # 组件层
│   ├── common/
│   ├── customer/
│   ├── design/
│   └── charts/
│
├── routes/              # 路由层
│   └── app_router.dart
│
└── utils/               # 工具层
    ├── constants.dart
    ├── validators.dart
    └── helpers.dart
```

#### 状态管理策略

使用**Provider模式**进行状态管理：

- **本地状态**：Widget内部使用`setState`
- **共享状态**：跨页面数据使用`ChangeNotifierProvider`
- **全局状态**：认证状态、用户信息使用`MultiProvider`

#### 数据流向

```
User Interaction (Screen)
       ↓
Provider (State Management)
       ↓
Service (API Call)
       ↓
API Response
       ↓
Model (Data Parsing)
       ↓
Provider (Notify Listeners)
       ↓
UI Update (Screen Rebuild)
```

### 2. 后端架构（FastAPI）

#### 分层设计

```
backend/app/
├── core/                # 核心配置层
│   ├── config.py             # 应用配置（Pydantic Settings）
│   ├── security.py           # JWT认证、密码加密
│   └── file_upload.py        # 文件上传工具
│
├── db/                  # 数据库配置层
│   └── database.py           # SQLAlchemy配置、get_db依赖
│
├── models/              # ORM模型层（SQLAlchemy）
│   ├── user.py
│   ├── customer.py
│   ├── customer_profile.py
│   ├── design_plan.py
│   ├── service_record.py
│   ├── comparison_result.py
│   ├── ability_dimension.py
│   ├── ability_record.py
│   └── inspiration_image.py
│
├── schemas/             # 数据验证层（Pydantic）
│   ├── user.py
│   ├── customer.py
│   ├── design.py
│   ├── service.py
│   ├── analysis.py
│   └── ability.py
│
├── services/            # 业务逻辑层
│   ├── ai/
│   │   ├── base.py           # AI Provider抽象基类
│   │   ├── openai_provider.py
│   │   ├── baidu_provider.py  # 预留
│   │   └── factory.py         # AI Provider工厂
│   ├── customer_service.py
│   ├── design_service.py
│   ├── service_record_service.py
│   ├── analysis_service.py
│   └── ability_service.py
│
└── api/                 # API路由层
    └── v1/
        ├── __init__.py       # 路由注册
        ├── auth.py
        ├── customers.py
        ├── designs.py
        ├── services.py
        ├── analysis.py
        └── inspirations.py
```

#### 依赖注入

FastAPI的依赖注入机制：

```python
# 数据库会话依赖
@app.get("/customers/{id}")
async def get_customer(
    id: int,
    db: Session = Depends(get_db),  # 自动注入数据库会话
    current_user: User = Depends(get_current_user)  # 自动注入当前用户
):
    customer = CustomerService.get_customer(db, id, current_user.id)
    return customer
```

#### API版本控制

所有API路由统一使用`/api/v1`前缀：

```python
# app/main.py
from app.api.v1 import api_router

app.include_router(api_router, prefix="/api/v1")
```

未来升级到v2时，可保持v1向后兼容。

### 3. AI代理层架构（关键设计）

#### 为什么需要AI代理层？

1. **可替换性**：当前使用OpenAI，未来可能切换到百度、阿里等国内AI服务
2. **成本控制**：可根据不同场景选择不同成本的AI服务
3. **容错性**：主AI服务故障时，自动降级到备用服务
4. **统一接口**：业务层无需关心底层AI实现细节

#### 设计模式：抽象工厂 + 策略模式

```python
# app/services/ai/base.py
from abc import ABC, abstractmethod
from typing import List, Dict, Optional

class AIProvider(ABC):
    """AI服务抽象基类"""

    @abstractmethod
    async def generate_design(
        self,
        prompt: str,
        reference_images: List[str],
        design_target: str = "single",  # single/5nails/10nails
        **kwargs
    ) -> str:
        """生成设计图，返回图片URL"""
        pass

    @abstractmethod
    async def refine_design(
        self,
        original_image: str,
        refinement_instruction: str,
        **kwargs
    ) -> str:
        """微调设计图，返回新图片URL"""
        pass

    @abstractmethod
    async def estimate_execution(
        self,
        design_image: str
    ) -> Dict:
        """评估设计落地信息
        返回格式：
        {
            "duration_min": 90,
            "duration_max": 120,
            "materials": [
                {"name": "浅粉色甲油", "amount": "适量", "type": "polish"},
                {"name": "金箔", "amount": "少量", "type": "decoration"}
            ],
            "complexity": "medium"  # low/medium/high
        }
        """
        pass

    @abstractmethod
    async def analyze_image(
        self,
        image_url: str,
        analysis_type: str
    ) -> Dict:
        """分析单张图片"""
        pass

    @abstractmethod
    async def compare_images(
        self,
        design_image: str,
        actual_image: str
    ) -> Dict:
        """对比两张图片，返回差异分析"""
        pass
```

```python
# app/services/ai/openai_provider.py
import openai
from app.services.ai.base import AIProvider

class OpenAIProvider(AIProvider):
    """OpenAI实现"""

    def __init__(self, api_key: str):
        self.client = openai.AsyncOpenAI(api_key=api_key)

    async def generate_design(self, prompt: str, reference_images: List[str], design_target: str = "single", **kwargs):
        """使用DALL-E 3生成设计"""
        # 根据生成目标调整prompt
        target_prompts = {
            "single": "Generate a single nail art design focusing on one nail.",
            "5nails": "Generate a complete nail art design for 5 nails on one hand.",
            "10nails": "Generate a complete nail art design for 10 nails on both hands."
        }
        full_prompt = f"{target_prompts.get(design_target, '')} {prompt}"

        response = await self.client.images.generate(
            model="dall-e-3",
            prompt=full_prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        return response.data[0].url

    async def refine_design(self, original_image: str, refinement_instruction: str, **kwargs):
        """微调设计（使用GPT-4 Vision + DALL-E 3）"""
        # 1. 使用GPT-4 Vision分析原设计
        analysis_prompt = f"""
        Analyze this nail art design and describe it in detail.
        Then apply this modification: {refinement_instruction}

        Provide a new detailed prompt for generating the refined design.
        """

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": analysis_prompt},
                    {"type": "image_url", "image_url": {"url": original_image}}
                ]
            }
        ]

        vision_response = await self.client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=messages,
            max_tokens=500
        )

        refined_prompt = vision_response.choices[0].message.content

        # 2. 使用新prompt生成微调后的设计
        design_response = await self.client.images.generate(
            model="dall-e-3",
            prompt=refined_prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )

        return design_response.data[0].url

    async def estimate_execution(self, design_image: str) -> Dict:
        """使用GPT-4 Vision评估设计落地信息"""
        estimation_prompt = """
        You are a professional nail artist. Analyze this nail art design and provide:
        1. Estimated time to complete (min and max in minutes)
        2. List of materials needed (nail polish colors, decorations, etc.)
        3. Complexity level (low/medium/high)

        Respond in JSON format:
        {
            "duration_min": <minutes>,
            "duration_max": <minutes>,
            "materials": [
                {"name": "<material name>", "amount": "<amount>", "type": "polish|decoration|tool"}
            ],
            "complexity": "low|medium|high",
            "notes": "<any additional notes>"
        }
        """

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": estimation_prompt},
                    {"type": "image_url", "image_url": {"url": design_image}}
                ]
            }
        ]

        response = await self.client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=messages,
            max_tokens=800
        )

        import json
        return json.loads(response.choices[0].message.content)

    async def compare_images(self, design_image: str, actual_image: str):
        """使用GPT-4 Vision对比图片"""
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": self._build_comparison_prompt()},
                    {"type": "image_url", "image_url": {"url": design_image}},
                    {"type": "image_url", "image_url": {"url": actual_image}}
                ]
            }
        ]
        response = await self.client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=messages,
            max_tokens=1000
        )
        return self._parse_comparison_result(response.choices[0].message.content)
```

```python
# app/services/ai/factory.py
from app.services.ai.base import AIProvider
from app.services.ai.openai_provider import OpenAIProvider
from app.core.config import settings

class AIProviderFactory:
    """AI Provider工厂"""

    _instances = {}  # 单例缓存

    @classmethod
    def get_provider(cls, provider_type: str = None) -> AIProvider:
        """获取AI Provider实例"""
        if provider_type is None:
            provider_type = settings.AI_PROVIDER  # 从配置读取默认provider

        if provider_type not in cls._instances:
            if provider_type == "openai":
                cls._instances[provider_type] = OpenAIProvider(
                    api_key=settings.OPENAI_API_KEY
                )
            elif provider_type == "baidu":
                # 未来实现
                raise NotImplementedError("Baidu AI Provider not implemented yet")
            else:
                raise ValueError(f"Unknown AI provider: {provider_type}")

        return cls._instances[provider_type]
```

#### 业务层调用示例

```python
# app/services/design_service.py
from app.services.ai.factory import AIProviderFactory

class DesignService:

    @staticmethod
    async def generate_design_plan(
        customer_profile: dict,
        inspiration_images: List[str],
        db: Session
    ):
        # 构建AI prompt
        prompt = DesignService._build_prompt(customer_profile)

        # 通过工厂获取AI Provider（无需关心具体实现）
        ai_provider = AIProviderFactory.get_provider()

        # 调用AI生成设计
        design_image_url = await ai_provider.generate_design(
            prompt=prompt,
            reference_images=inspiration_images
        )

        # 保存设计方案
        design_plan = DesignPlan(...)
        db.add(design_plan)
        db.commit()

        return design_plan
```

### 4. 数据库架构

#### 数据库选择：PostgreSQL

- **优点**：功能完整、性能优秀、支持JSON字段、适合生产环境
- **开发环境**：可使用SQLite简化配置

#### 核心表设计

##### 1. users（美甲师）

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

##### 2. customers（客户档案）

```sql
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_customers_user_id ON customers(user_id);
```

##### 3. customer_profiles（客户详细档案）

```sql
CREATE TABLE customer_profiles (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER UNIQUE REFERENCES customers(id) ON DELETE CASCADE,
    nail_shape VARCHAR(50),         -- 甲型：almond/square/oval等
    nail_size VARCHAR(20),          -- 甲床大小：small/medium/large
    nail_condition VARCHAR(50),     -- 指甲状态：healthy/brittle等
    color_preferences JSONB,        -- 颜色偏好 ["#FF69B4", "#FFB6C1"]
    style_preferences JSONB,        -- 风格偏好 ["minimalist", "elegant"]
    prohibitions JSONB,             -- 禁忌 ["glitter", "long"]
    profile_images JSONB,           -- 档案图片 ["path1", "path2"]
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

##### 4. inspiration_images（灵感图库）

```sql
CREATE TABLE inspiration_images (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    image_path VARCHAR(500) NOT NULL,
    tags JSONB,                     -- 标签 ["floral", "pink", "spring"]
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_inspiration_user_id ON inspiration_images(user_id);
```

##### 5. design_plans（设计方案 - 增强版）

```sql
CREATE TABLE design_plans (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    customer_id INTEGER REFERENCES customers(id) ON DELETE SET NULL,
    inspiration_image_ids JSONB,    -- 关联的灵感图ID [1, 2, 3]
    ai_prompt TEXT,                 -- AI提示词（自动生成）
    custom_prompt TEXT,             -- 用户自定义提示词
    design_target VARCHAR(20) DEFAULT 'single',  -- 生成目标: single/5nails/10nails
    generated_image_path VARCHAR(500),  -- 生成的设计图路径
    design_description TEXT,        -- 方案描述
    parent_design_id INTEGER REFERENCES design_plans(id) ON DELETE SET NULL,  -- 父设计ID（用于微调版本）
    refinement_prompt TEXT,         -- 微调指令
    estimated_duration_min INTEGER, -- 预估耗时（分钟）- 最小值
    estimated_duration_max INTEGER, -- 预估耗时（分钟）- 最大值
    material_list JSONB,            -- 用料清单 [{"name": "浅粉色甲油", "amount": "适量"}]
    version INTEGER DEFAULT 1,      -- 版本号（用于微调迭代）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_design_plans_user_id ON design_plans(user_id);
CREATE INDEX idx_design_plans_customer_id ON design_plans(customer_id);
CREATE INDEX idx_design_plans_parent_id ON design_plans(parent_design_id);
```

##### 6. service_records（服务记录）

```sql
CREATE TABLE service_records (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    customer_id INTEGER REFERENCES customers(id) ON DELETE SET NULL,
    design_plan_id INTEGER REFERENCES design_plans(id) ON DELETE SET NULL,
    service_date DATE NOT NULL,
    service_duration INTEGER,       -- 服务时长（分钟）
    actual_image_path VARCHAR(500), -- 实际完成图路径
    notes TEXT,
    status VARCHAR(20) DEFAULT 'pending',  -- pending/completed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE INDEX idx_service_records_user_id ON service_records(user_id);
CREATE INDEX idx_service_records_customer_id ON service_records(customer_id);
```

##### 7. comparison_results（对比分析结果）

```sql
CREATE TABLE comparison_results (
    id SERIAL PRIMARY KEY,
    service_record_id INTEGER UNIQUE REFERENCES service_records(id) ON DELETE CASCADE,
    similarity_score INTEGER CHECK (similarity_score >= 0 AND similarity_score <= 100),
    differences JSONB,              -- 差异点 {"color": "略有偏差", "pattern": "精度高"}
    suggestions JSONB,              -- 改进建议 ["注意颜色过渡", "细节可更精细"]
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

##### 8. ability_dimensions（能力维度定义）

```sql
CREATE TABLE ability_dimensions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,      -- 能力名称
    description TEXT,                        -- 能力描述
    weight DECIMAL(3, 2) DEFAULT 1.0,       -- 权重（用于综合评分）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 初始化数据
INSERT INTO ability_dimensions (name, description) VALUES
('颜色搭配', '色彩组合的协调性和创意'),
('图案精度', '图案绘制的精确度和细腻度'),
('细节处理', '细节的完整度和精致度'),
('整体构图', '设计的整体美感和平衡'),
('技法运用', '美甲技法的熟练度和多样性'),
('创意表达', '设计的创新性和独特性');
```

##### 9. ability_records（能力评分记录）

```sql
CREATE TABLE ability_records (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    service_record_id INTEGER REFERENCES service_records(id) ON DELETE CASCADE,
    dimension_id INTEGER REFERENCES ability_dimensions(id) ON DELETE CASCADE,
    score INTEGER CHECK (score >= 0 AND score <= 100),
    evidence JSONB,                 -- 评分依据（从AI分析提取）
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ability_records_user_id ON ability_records(user_id);
CREATE INDEX idx_ability_records_dimension_id ON ability_records(dimension_id);
```

#### 数据库关系图

```
users (1) ──────< customers (N)
              │
              └──────< customer_profiles (1)
              │
              └──────< service_records (N)
                          │
                          ├──────< comparison_results (1)
                          └──────< ability_records (N)

users (1) ──────< design_plans (N)
              │
              └──────> customers (N) [外键关联]

users (1) ──────< inspiration_images (N)

ability_dimensions (1) ──────< ability_records (N)
```

### 5. 文件存储架构

#### 存储方案：本地文件系统（MVP）

```
backend/uploads/
├── nails/              # 客户甲型照片
│   ├── customer_1_profile_1.jpg
│   └── customer_2_profile_1.jpg
├── inspirations/       # 灵感图
│   ├── inspiration_1.jpg
│   └── inspiration_2.jpg
├── designs/            # AI生成的设计图
│   ├── design_1.jpg
│   └── design_2.jpg
└── actuals/            # 实际完成图
    ├── service_1_actual.jpg
    └── service_2_actual.jpg
```

#### 文件命名规则

- 客户档案图：`customer_{customer_id}_profile_{timestamp}.jpg`
- 灵感图：`inspiration_{id}_{timestamp}.jpg`
- 设计图：`design_{design_id}_{timestamp}.jpg`
- 完成图：`service_{service_id}_actual_{timestamp}.jpg`

#### 文件访问

- **上传**：POST `/api/v1/upload`，返回文件路径
- **访问**：通过FastAPI静态文件服务：`http://localhost:8000/uploads/designs/design_1.jpg`

```python
# app/main.py
from fastapi.staticfiles import StaticFiles

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
```

#### 未来扩展：对象存储

Post-MVP可迁移到云对象存储（阿里云OSS、腾讯云COS）：
- CDN加速
- 更高可靠性
- 支持图片处理（缩略图、水印）

### 6. 缓存架构（Redis）

#### 缓存策略

1. **AI生成结果缓存**（成本优化）
   - Key: `ai:design:{prompt_hash}`
   - TTL: 7天
   - 相同prompt避免重复调用AI

2. **用户Session缓存**
   - Key: `session:{user_id}`
   - TTL: 30分钟

3. **能力数据缓存**
   - Key: `ability:{user_id}:latest`
   - TTL: 1小时
   - 减少复杂查询

#### Redis数据结构

```python
# AI缓存示例
redis.set(
    f"ai:design:{hash_prompt(prompt)}",
    json.dumps({"image_url": "...", "generated_at": "..."}),
    ex=7*24*3600  # 7天
)

# 能力数据缓存
redis.hset(
    f"ability:{user_id}:latest",
    mapping={
        "color_matching": 85,
        "pattern_precision": 78,
        "detail_work": 90,
        # ...
    }
)
redis.expire(f"ability:{user_id}:latest", 3600)  # 1小时
```

## 部署架构

### 开发环境

```
┌─────────────────┐
│  Flutter App    │ ← 开发者电脑
│  (Hot Reload)   │
└────────┬────────┘
         ↓ HTTP
┌─────────────────┐
│ FastAPI Backend │ ← 本地运行 (uvicorn --reload)
│ SQLite Database │
│ Redis (Docker)  │
└─────────────────┘
```

### 生产环境（单服务器部署）

```
┌───────────────────────────────────────┐
│           Nginx (反向代理)             │
│  SSL证书、静态文件、负载均衡            │
└───────────┬───────────────────────────┘
            ↓
┌───────────────────────────────────────┐
│      Docker Compose 编排               │
│  ┌─────────────────────────────────┐  │
│  │  FastAPI Container (Gunicorn)   │  │
│  │  - 4 workers                    │  │
│  └─────────────────────────────────┘  │
│  ┌─────────────────────────────────┐  │
│  │  PostgreSQL Container           │  │
│  │  - Volume持久化                 │  │
│  └─────────────────────────────────┘  │
│  ┌─────────────────────────────────┐  │
│  │  Redis Container                │  │
│  └─────────────────────────────────┘  │
└───────────────────────────────────────┘
```

### Docker Compose配置

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend/uploads:/app/uploads
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/nail_db
      - REDIS_HOST=redis
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=nail_db
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass

  redis:
    image: redis:7
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

## 扩展性考虑

### 横向扩展

1. **后端无状态设计**：所有状态存储在数据库/Redis，支持多实例部署
2. **数据库读写分离**：高并发时可配置PostgreSQL主从复制
3. **CDN加速**：图片迁移到对象存储+CDN
4. **AI服务解耦**：AI调用可独立部署为微服务

### 多租户改造

如果未来支持多美甲师（SaaS模式），需要：
1. 所有表添加`tenant_id`字段
2. 行级数据隔离（RLS）
3. 配额管理（每租户AI调用次数限制）
4. 独立的文件存储空间

## 安全架构

### 1. 认证和授权

- **JWT Token**：Access Token（30分钟） + Refresh Token（7天）
- **密码加密**：bcrypt哈希存储
- **API鉴权**：所有业务接口需要Bearer Token

### 2. 数据安全

- **SQL注入防护**：使用SQLAlchemy ORM
- **XSS防护**：前端输入验证 + 后端转义
- **文件上传安全**：
  - 文件类型白名单（jpg、png）
  - 文件大小限制（10MB）
  - 文件名随机化

### 3. API安全

- **CORS配置**：限制允许的来源
- **Rate Limiting**：Redis实现每IP限流
- **HTTPS**：生产环境强制SSL

## 监控和日志

### 日志策略

```python
# app/core/logging.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

# 关键操作记录
logger.info(f"User {user_id} generated design for customer {customer_id}")
logger.warning(f"AI API call failed, retrying...")
logger.error(f"Database error: {error}")
```

### 监控指标

- **性能指标**：API响应时间、数据库查询时间
- **业务指标**：AI调用次数、成功率、成本
- **错误监控**：异常捕获、错误率追踪
