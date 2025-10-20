# 元视角模式 - 实施计划与最佳实践

## 📋 文档信息

| 项目 | 内容 |
|------|------|
| 功能名称 | 元视角模式 (Meta-View Mode) - 实施计划 |
| 版本 | v1.0.0 |
| 文档状态 | 实施阶段 |
| 创建日期 | 2025-10-20 |

---

## 🎯 一、实施总览

### 1.1 项目目标

将"元视角模式"从设计稿转化为可交付的产品功能,分为**MVP阶段**和**完整版阶段**,确保每个阶段都能独立交付并验证价值。

### 1.2 实施原则

1. **MVP优先**: 先实现核心功能,快速验证用户价值
2. **增量开发**: 每个阶段都是可工作的产品
3. **质量保证**: 每个模块都要经过充分测试
4. **文档同步**: 代码和文档同步更新
5. **性能监控**: 从第一行代码开始就关注性能

---

## 📅 二、详细实施计划

### Phase 1: MVP (最小可行产品) - Week 1-2

#### 目标
验证核心功能和技术可行性,快速交付可用原型

#### 范围

**后端**:
- ✅ 数据库表结构 (meta_analyses)
- ✅ MetaAnalysisService (作者意图 + 时效性分析)
- ✅ API 路由 (analyze + get)
- ✅ LLM Prompt工程 (基础版)

**前端**:
- ✅ useMetaView composable (基础状态管理)
- ✅ MetaViewTrigger 组件 (👓按钮)
- ✅ MetaInfoPanel 组件 (滑出面板)
- ✅ MetaInfoCard 组件 (通用卡片)
- ✅ 作者意图卡片
- ✅ 时效性卡片
- ✅ 论证结构透镜 (基础高亮)

**不包含**:
- ❌ 潜在偏见检测
- ❌ 知识缺口提示
- ❌ 作者立场透镜
- ❌ 用户反馈机制

#### Week 1 详细任务

**Day 1-2: 后端基础**
```
Day 1:
□ 创建数据库迁移脚本
□ 实现 MetaAnalysis 模型
□ 编写基础的元信息分析 Prompt
□ 测试 OpenAI API 连接

Day 2:
□ 实现 MetaAnalysisService.analyze_article()
□ 实现作者意图分析逻辑
□ 实现时效性评估逻辑
□ 单元测试 (service层)
```

**Day 3-4: 后端API**
```
Day 3:
□ 创建 /api/v1/meta-analysis/analyze 端点
□ 创建 /api/v1/meta-analysis/{article_id} 端点
□ 异步处理逻辑
□ 错误处理和重试机制

Day 4:
□ API 集成测试
□ 性能测试 (响应时间)
□ 文档生成 (Swagger)
□ Postman 测试集
```

**Day 5-7: 前端核心组件**
```
Day 5:
□ 创建 useMetaView.ts composable
□ 定义 TypeScript 接口
□ 实现基础状态管理
□ API 调用封装

Day 6:
□ 实现 MetaViewTrigger.vue (👓按钮)
□ 实现 MetaInfoPanel.vue (滑出面板)
□ 实现 MetaInfoCard.vue (通用卡片)
□ 实现滑出动画

Day 7:
□ 实现作者意图卡片
□ 实现时效性卡片
□ 视觉调整 (颜色、间距、字体)
□ 响应式适配
```

**Day 8-10: 思维透镜 (论证结构)**
```
Day 8:
□ 实现 ThinkingLensService (后端)
□ 论证结构分析 Prompt
□ /api/v1/thinking-lens/apply 端点
□ 单元测试

Day 9:
□ 创建 useThinkingLens.ts composable
□ 实现高亮渲染算法
□ 实现 ThinkingLensSwitcher.vue 组件
□ 测试高亮位置准确性

Day 10:
□ 集成到阅读页面
□ 端到端测试
□ 性能优化 (大文章测试)
□ Bug 修复
```

#### Week 2 详细任务

**Day 11-12: 集成与测试**
```
Day 11:
□ 完整流程测试 (触发 -> 分析 -> 显示 -> 透镜)
□ 边界情况测试 (无网络、API失败、超时)
□ 性能测试 (3000字、5000字、10000字文章)
□ 浏览器兼容性测试 (Chrome, Firefox, Safari)

Day 12:
□ 移动端适配测试
□ 用户体验优化
□ 加载状态优化
□ 错误提示优化
```

**Day 13-14: 文档与发布准备**
```
Day 13:
□ 编写 API 文档
□ 编写前端组件使用文档
□ 编写用户使用指南
□ 录制功能演示视频

Day 14:
□ 代码 Review
□ 修复发现的问题
□ 准备演示环境
□ MVP 验收
```

#### MVP 验收标准

**功能验收**:
- [x] 用户点击👓图标,元信息面板滑出
- [x] 显示作者意图和时效性两张卡片
- [x] 卡片显示置信度指示器
- [x] 用户可以激活论证结构透镜
- [x] 激活后文章中的主张和证据被高亮
- [x] 高亮颜色正确,悬停有反馈

**性能验收**:
- [x] 元信息分析平均耗时 < 8秒 (5000字文章)
- [x] 高亮渲染流畅 (>30 FPS)
- [x] API 成功率 > 90%

**质量验收**:
- [x] 无 P0/P1 严重bug
- [x] 单元测试覆盖率 > 60%
- [x] 代码 Review 通过

---

### Phase 2: 功能完善 - Week 3-4

#### 目标
补全所有设计功能,达到生产就绪状态

#### 范围

**后端**:
- ✅ 潜在偏见检测
- ✅ 知识缺口提示
- ✅ 作者立场透镜
- ✅ 用户反馈 API
- ✅ Prompt 优化

**前端**:
- ✅ 潜在偏见卡片
- ✅ 知识缺口卡片
- ✅ 作者立场透镜
- ✅ 用户反馈按钮
- ✅ 移动端完整适配
- ✅ 动画和交互优化

#### Week 3 详细任务

**Day 15-16: 潜在偏见检测**
```
Day 15:
□ 编写偏见检测 Prompt
□ 实现 detect_bias() 方法
□ 测试各种偏见类型识别
□ API 集成

Day 16:
□ 实现偏见卡片组件
□ 可视化偏见严重程度
□ 显示具体案例
□ 测试和优化
```

**Day 17-18: 知识缺口提示**
```
Day 17:
□ 编写知识缺口 Prompt
□ 实现 identify_knowledge_gaps() 方法
□ 测试前置知识识别
□ API 集成

Day 18:
□ 实现知识缺口卡片
□ 设计交互方式
□ 关联概念推荐
□ 测试
```

**Day 19-21: 作者立场透镜**
```
Day 19:
□ 编写作者立场 Prompt
□ 实现 apply_stance_lens() 方法
□ 测试主观/客观识别
□ API 集成

Day 20:
□ 实现作者立场透镜 UI
□ 高亮颜色调整
□ 透镜切换动画
□ 测试

Day 21:
□ 优化高亮算法
□ 处理跨标签高亮
□ 性能优化
□ 边界测试
```

#### Week 4 详细任务

**Day 22-23: 用户反馈机制**
```
Day 22:
□ 创建 meta_view_feedback 表
□ 实现反馈 API
□ 统计分析逻辑
□ 后台数据看板

Day 23:
□ 实现反馈按钮 UI
□ 反馈提交逻辑
□ 成功提示
□ 测试
```

**Day 24-25: 移动端适配**
```
Day 24:
□ 面板从底部滑出 (移动端)
□ 卡片横向滑动
□ 触摸手势优化
□ 字体大小调整

Day 25:
□ iOS Safari 测试
□ Android Chrome 测试
□ 响应式断点调整
□ 性能优化
```

**Day 26-28: 优化与打磨**
```
Day 26:
□ Prompt 调优 (基于真实数据)
□ 提升分析准确性
□ 降低误报率
□ A/B 测试准备

Day 27:
□ 性能优化 (缓存、压缩)
□ 错误处理完善
□ 用户引导优化
□ 动画流畅度提升

Day 28:
□ 完整测试
□ Bug 修复
□ 文档更新
□ 发布准备
```

#### 完整版验收标准

**功能验收**:
- [x] 显示全部4张元信息卡片
- [x] 支持2个思维透镜切换
- [x] 用户可以提交反馈
- [x] 移动端体验完整

**性能验收**:
- [x] 元信息分析平均耗时 < 5秒 (P95)
- [x] 高亮渲染 >60 FPS
- [x] API 成功率 > 95%
- [x] 前端 bundle 增加 < 50KB

**质量验收**:
- [x] 单元测试覆盖率 > 70%
- [x] 集成测试通过
- [x] 无 P0/P1 bug
- [x] 代码 Review 通过
- [x] 文档完整

---

## 🏗️ 三、技术实现细节

### 3.1 后端实现

#### 3.1.1 数据库模型

```python
# backend/app/models/models.py

class MetaAnalysis(Base):
    """元信息分析表"""
    __tablename__ = "meta_analyses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(Integer, ForeignKey("articles.id"), unique=True, nullable=False, index=True)

    # 作者意图分析
    author_intent = Column(JSON, nullable=False)
    # {
    #   "primary": "inform|persuade|entertain|provoke",
    #   "confidence": 0.85,
    #   "description": "...",
    #   "indicators": ["...", "..."]
    # }

    # 时效性评估
    timeliness_score = Column(Float, nullable=False)
    timeliness_analysis = Column(JSON, nullable=False)
    # {
    #   "category": "evergreen",
    #   "decay_rate": "low",
    #   "best_before": null,
    #   "context_dependencies": []
    # }

    # 潜在偏见检测
    bias_analysis = Column(JSON, nullable=False)
    # {
    #   "detected": false,
    #   "types": [],
    #   "severity": "low",
    #   "examples": [],
    #   "overall_balance": "balanced"
    # }

    # 知识缺口提示
    knowledge_gaps = Column(JSON, nullable=False)
    # {
    #   "prerequisites": ["..."],
    #   "assumptions": ["..."],
    #   "missing_context": ["..."],
    #   "related_concepts": ["..."]
    # }

    # 原始 LLM 响应
    raw_llm_response = Column(Text, nullable=True)

    # 分析质量指标
    analysis_quality = Column(JSON, nullable=True)
    # {
    #   "confidence_score": 0.88,
    #   "processing_time_ms": 3500,
    #   "llm_model": "gpt-4o",
    #   "prompt_version": "v1.0"
    # }

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    article = relationship("Article", back_populates="meta_analysis")
    thinking_lens_results = relationship("ThinkingLensResult", back_populates="meta_analysis", cascade="all, delete-orphan")
    feedbacks = relationship("MetaViewFeedback", back_populates="meta_analysis", cascade="all, delete-orphan")


class ThinkingLensResult(Base):
    """思维透镜结果表"""
    __tablename__ = "thinking_lens_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    meta_analysis_id = Column(Integer, ForeignKey("meta_analyses.id"), nullable=False, index=True)
    lens_type = Column(String(50), nullable=False)  # 'argument_structure' | 'author_stance'

    # 高亮数据
    highlights = Column(JSON, nullable=False)
    # [
    #   {
    #     "start": 50,
    #     "end": 120,
    #     "text": "...",
    #     "category": "claim",
    #     "color": "#dbeafe",
    #     "tooltip": "..."
    #   }
    # ]

    # 注释和统计
    annotations = Column(JSON, nullable=True)
    # {
    #   "summary": "...",
    #   "key_insights": ["...", "..."],
    #   "statistics": {...}
    # }

    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    meta_analysis = relationship("MetaAnalysis", back_populates="thinking_lens_results")
    feedbacks = relationship("MetaViewFeedback", back_populates="lens_result", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_meta_lens', 'meta_analysis_id', 'lens_type'),
        UniqueConstraint('meta_analysis_id', 'lens_type', name='uq_meta_lens')
    )


class MetaViewFeedback(Base):
    """用户反馈表"""
    __tablename__ = "meta_view_feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    meta_analysis_id = Column(Integer, ForeignKey("meta_analyses.id"), nullable=True)
    lens_result_id = Column(Integer, ForeignKey("thinking_lens_results.id"), nullable=True)

    feedback_type = Column(String(50), nullable=False)  # 'meta_info_card' | 'lens_highlight' | 'overall'
    rating = Column(Integer, nullable=True)  # 1-5
    comment = Column(Text, nullable=True)
    feedback_data = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # 关系
    user = relationship("User")
    meta_analysis = relationship("MetaAnalysis", back_populates="feedbacks")
    lens_result = relationship("ThinkingLensResult", back_populates="feedbacks")
```

**更新 Article 模型**:
```python
# 在 Article 模型中添加
class Article(Base):
    # ... 现有字段 ...

    # 新增关系
    meta_analysis = relationship("MetaAnalysis", back_populates="article", uselist=False, cascade="all, delete-orphan")
```

#### 3.1.2 服务层实现

```python
# backend/app/services/meta_analysis_service.py

from openai import OpenAI
from sqlalchemy.orm import Session
from app.models.models import MetaAnalysis
from app.config import settings
import json
from datetime import datetime
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class MetaAnalysisService:
    def __init__(self, db: Session):
        self.db = db
        self.client = OpenAI(api_key=settings.openai_api_key)

    async def analyze_article(
        self,
        article_id: int,
        title: str,
        author: str,
        publish_date: str,
        content: str,
        language: str = "zh",
        force_reanalyze: bool = False
    ) -> Dict:
        """
        元信息分析主方法

        Args:
            article_id: 文章ID
            title: 文章标题
            author: 作者
            publish_date: 发布日期
            content: 文章内容
            language: 语言 (zh/en)
            force_reanalyze: 是否强制重新分析

        Returns:
            元信息分析结果
        """

        # 检查缓存
        if not force_reanalyze:
            existing = self.db.query(MetaAnalysis).filter(
                MetaAnalysis.article_id == article_id
            ).first()

            if existing:
                logger.info(f"使用缓存的元信息分析: article_id={article_id}")
                return self._format_response(existing)

        # 执行分析
        logger.info(f"开始元信息分析: article_id={article_id}")
        start_time = datetime.utcnow()

        try:
            # 调用 LLM
            llm_result = await self._call_llm_for_meta_analysis(
                title=title,
                author=author,
                publish_date=publish_date,
                content=content,
                language=language
            )

            processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)

            # 保存到数据库
            meta_analysis = MetaAnalysis(
                article_id=article_id,
                author_intent=llm_result['author_intent'],
                timeliness_score=llm_result['timeliness']['score'],
                timeliness_analysis=llm_result['timeliness'],
                bias_analysis=llm_result['bias'],
                knowledge_gaps=llm_result['knowledge_gaps'],
                raw_llm_response=json.dumps(llm_result, ensure_ascii=False),
                analysis_quality={
                    "confidence_score": llm_result['author_intent']['confidence'],
                    "processing_time_ms": processing_time,
                    "llm_model": "gpt-4o",
                    "prompt_version": "v1.0"
                }
            )

            self.db.add(meta_analysis)
            self.db.commit()
            self.db.refresh(meta_analysis)

            logger.info(f"元信息分析完成: article_id={article_id}, 耗时={processing_time}ms")

            return self._format_response(meta_analysis)

        except Exception as e:
            logger.error(f"元信息分析失败: article_id={article_id}, error={str(e)}")
            self.db.rollback()
            raise

    async def _call_llm_for_meta_analysis(
        self,
        title: str,
        author: str,
        publish_date: str,
        content: str,
        language: str
    ) -> Dict:
        """调用 LLM 进行元信息分析"""

        # 限制内容长度，避免超出 token 限制
        max_content_length = 5000 if language == "zh" else 10000
        truncated_content = content[:max_content_length]

        # 构建 Prompt
        system_prompt = self._get_meta_analysis_system_prompt()
        user_prompt = self._get_meta_analysis_user_prompt(
            title=title,
            author=author,
            publish_date=publish_date,
            content=truncated_content,
            language=language
        )

        # 调用 OpenAI API
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=2000
        )

        # 解析响应
        result = json.loads(response.choices[0].message.content)

        # 验证结构
        self._validate_llm_result(result)

        return result

    def _validate_llm_result(self, result: Dict):
        """验证 LLM 输出结构"""
        required_keys = ['author_intent', 'timeliness', 'bias', 'knowledge_gaps']

        for key in required_keys:
            if key not in result:
                raise ValueError(f"LLM 输出缺少必需字段: {key}")

        # 验证作者意图
        if result['author_intent']['primary'] not in ['inform', 'persuade', 'entertain', 'provoke']:
            raise ValueError(f"无效的作者意图类型: {result['author_intent']['primary']}")

        # 验证置信度
        if not 0 <= result['author_intent']['confidence'] <= 1:
            raise ValueError(f"置信度必须在0-1之间: {result['author_intent']['confidence']}")

        # 验证时效性分数
        if not 0 <= result['timeliness']['score'] <= 1:
            raise ValueError(f"时效性分数必须在0-1之间: {result['timeliness']['score']}")

    def _get_meta_analysis_system_prompt(self) -> str:
        """获取元信息分析的系统 Prompt"""
        return """
你是一位专业的文本分析专家，擅长识别文章的元信息。

你的任务是分析用户提供的文章，并以JSON格式输出结构化的元信息分析结果。

# 分析维度

1. **作者意图 (author_intent)**
   - primary: "inform" (告知), "persuade" (说服), "entertain" (娱乐), "provoke" (激发思考)
   - confidence: 0.0-1.0
   - description: 100字以内的详细说明
   - indicators: 3-5个关键识别依据

2. **时效性 (timeliness)**
   - score: 0.0-1.0 (0=永恒, 1=高度时效敏感)
   - category: "timeless", "evergreen", "time-sensitive", "breaking"
   - decay_rate: "low", "medium", "high"
   - best_before: ISO 8601日期或null
   - context_dependencies: 影响时效性的关键因素列表

3. **潜在偏见 (bias)**
   - detected: true/false
   - types: ["confirmation_bias", "political_bias", "cultural_bias", "selection_bias"]
   - severity: "low", "medium", "high"
   - examples: [{text, type, explanation}]
   - overall_balance: "balanced", "slightly_biased", "heavily_biased"

4. **知识缺口 (knowledge_gaps)**
   - prerequisites: 前置知识列表
   - assumptions: 隐含假设列表
   - missing_context: 缺失背景列表
   - related_concepts: 相关概念列表

# 输出格式

严格按照以下JSON schema输出：

{
  "author_intent": {
    "primary": "inform|persuade|entertain|provoke",
    "confidence": float,
    "description": "string",
    "indicators": ["string"]
  },
  "timeliness": {
    "score": float,
    "category": "timeless|evergreen|time-sensitive|breaking",
    "decay_rate": "low|medium|high",
    "best_before": "ISO 8601 or null",
    "context_dependencies": ["string"]
  },
  "bias": {
    "detected": boolean,
    "types": ["string"],
    "severity": "low|medium|high",
    "examples": [{"text": "string", "type": "string", "explanation": "string"}],
    "overall_balance": "balanced|slightly_biased|heavily_biased"
  },
  "knowledge_gaps": {
    "prerequisites": ["string"],
    "assumptions": ["string"],
    "missing_context": ["string"],
    "related_concepts": ["string"]
  }
}

# 注意事项

- 分析要客观、中立
- 不确定时降低置信度
- 偏见检测要谨慎
- 所有列表字段至少1个元素，最多5个
"""

    def _get_meta_analysis_user_prompt(
        self,
        title: str,
        author: str,
        publish_date: str,
        content: str,
        language: str
    ) -> str:
        """构建用户 Prompt"""
        return f"""
请分析以下文章的元信息：

---
标题：{title}
作者：{author}
发布时间：{publish_date}
语言：{language}

正文：
{content}
---

请按照系统提示中的JSON schema输出分析结果。
"""

    def _format_response(self, meta_analysis: MetaAnalysis) -> Dict:
        """格式化响应"""
        return {
            "id": meta_analysis.id,
            "article_id": meta_analysis.article_id,
            "author_intent": meta_analysis.author_intent,
            "timeliness_score": meta_analysis.timeliness_score,
            "timeliness_analysis": meta_analysis.timeliness_analysis,
            "bias_analysis": meta_analysis.bias_analysis,
            "knowledge_gaps": meta_analysis.knowledge_gaps,
            "analysis_quality": meta_analysis.analysis_quality,
            "created_at": meta_analysis.created_at.isoformat(),
            "updated_at": meta_analysis.updated_at.isoformat()
        }

    def get_meta_analysis(self, article_id: int) -> Optional[Dict]:
        """获取元信息分析结果"""
        meta_analysis = self.db.query(MetaAnalysis).filter(
            MetaAnalysis.article_id == article_id
        ).first()

        if not meta_analysis:
            return None

        return self._format_response(meta_analysis)
```

#### 3.1.3 API 路由

```python
# backend/app/api/meta_analysis.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.meta_analysis_service import MetaAnalysisService
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class AnalyzeRequest(BaseModel):
    article_id: int
    title: str
    author: str
    publish_date: str
    full_text: str
    language: str = "zh"
    force_reanalyze: bool = False


@router.post("/api/v1/meta-analysis/analyze")
async def analyze_article(
    request: AnalyzeRequest,
    db: Session = Depends(get_db)
):
    """
    触发元信息分析

    Args:
        request: 分析请求
        db: 数据库会话

    Returns:
        元信息分析结果
    """
    service = MetaAnalysisService(db)

    try:
        result = await service.analyze_article(
            article_id=request.article_id,
            title=request.title,
            author=request.author,
            publish_date=request.publish_date,
            content=request.full_text,
            language=request.language,
            force_reanalyze=request.force_reanalyze
        )

        return {
            "status": "success",
            "message": "分析完成",
            "meta_analysis": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/v1/meta-analysis/{article_id}")
async def get_meta_analysis(
    article_id: int,
    db: Session = Depends(get_db)
):
    """
    获取元信息分析结果

    Args:
        article_id: 文章ID
        db: 数据库会话

    Returns:
        元信息分析结果或null
    """
    service = MetaAnalysisService(db)
    result = service.get_meta_analysis(article_id)

    if result is None:
        return {
            "exists": False,
            "meta_analysis": None
        }

    return {
        "exists": True,
        "meta_analysis": result
    }
```

**注册路由**:
```python
# backend/app/main.py

from app.api import meta_analysis

app.include_router(meta_analysis.router, tags=["meta-analysis"])
```

---

### 3.2 前端实现

#### 3.2.1 Composable: useMetaView

```typescript
// frontend/app/composables/useMetaView.ts

export interface AuthorIntent {
  primary: 'inform' | 'persuade' | 'entertain' | 'provoke'
  confidence: number
  description: string
  indicators: string[]
}

export interface TimelinessAnalysis {
  score: number
  category: 'timeless' | 'evergreen' | 'time-sensitive' | 'breaking'
  decay_rate: 'low' | 'medium' | 'high'
  best_before: string | null
  context_dependencies: string[]
}

export interface BiasExample {
  text: string
  type: string
  explanation: string
}

export interface BiasAnalysis {
  detected: boolean
  types: string[]
  severity: 'low' | 'medium' | 'high'
  examples: BiasExample[]
  overall_balance: 'balanced' | 'slightly_biased' | 'heavily_biased'
}

export interface KnowledgeGaps {
  prerequisites: string[]
  assumptions: string[]
  missing_context: string[]
  related_concepts: string[]
}

export interface MetaAnalysisData {
  id: number
  article_id: number
  author_intent: AuthorIntent
  timeliness_score: number
  timeliness_analysis: TimelinessAnalysis
  bias_analysis: BiasAnalysis
  knowledge_gaps: KnowledgeGaps
  analysis_quality: {
    confidence_score: number
    processing_time_ms: number
    llm_model: string
    prompt_version: string
  }
  created_at: string
  updated_at: string
}

export const useMetaView = () => {
  const config = useRuntimeConfig()

  // 状态
  const isMetaViewActive = useState<boolean>('meta-view-active', () => false)
  const metaAnalysisData = useState<MetaAnalysisData | null>('meta-analysis-data', () => null)
  const isAnalyzing = useState<boolean>('meta-view-analyzing', () => false)
  const analysisError = useState<string | null>('meta-view-error', () => null)

  /**
   * 触发元信息分析
   */
  const analyzeArticle = async (
    articleId: number,
    title: string,
    author: string,
    publishDate: string,
    fullText: string,
    language: string = 'zh',
    forceReanalyze: boolean = false
  ) => {
    isAnalyzing.value = true
    analysisError.value = null

    try {
      const response = await $fetch<{ status: string; meta_analysis: MetaAnalysisData }>(
        `${config.public.apiBase}/api/v1/meta-analysis/analyze`,
        {
          method: 'POST',
          body: {
            article_id: articleId,
            title,
            author,
            publish_date: publishDate,
            full_text: fullText,
            language,
            force_reanalyze: forceReanalyze
          }
        }
      )

      metaAnalysisData.value = response.meta_analysis
      console.log('✅ 元信息分析完成')

    } catch (error) {
      console.error('❌ 元信息分析失败:', error)
      analysisError.value = error instanceof Error ? error.message : '分析失败'
      throw error
    } finally {
      isAnalyzing.value = false
    }
  }

  /**
   * 获取已有的元信息分析结果
   */
  const fetchMetaAnalysis = async (articleId: number) => {
    try {
      const response = await $fetch<{ exists: boolean; meta_analysis: MetaAnalysisData | null }>(
        `${config.public.apiBase}/api/v1/meta-analysis/${articleId}`
      )

      if (response.exists && response.meta_analysis) {
        metaAnalysisData.value = response.meta_analysis
        return true
      }

      return false

    } catch (error) {
      console.error('❌ 获取元信息失败:', error)
      return false
    }
  }

  /**
   * 切换元视角模式
   */
  const toggleMetaView = async () => {
    isMetaViewActive.value = !isMetaViewActive.value

    // 如果激活且没有数据，触发分析
    if (isMetaViewActive.value && !metaAnalysisData.value && !isAnalyzing.value) {
      // 需要从外部传入文章信息
      // 这里只是切换状态，实际分析由外部组件触发
    }
  }

  /**
   * 关闭元视角
   */
  const closeMetaView = () => {
    isMetaViewActive.value = false
  }

  /**
   * 清空数据
   */
  const clearMetaAnalysis = () => {
    metaAnalysisData.value = null
    analysisError.value = null
  }

  return {
    // 状态
    isMetaViewActive: readonly(isMetaViewActive),
    metaAnalysisData: readonly(metaAnalysisData),
    isAnalyzing: readonly(isAnalyzing),
    analysisError: readonly(analysisError),

    // 方法
    analyzeArticle,
    fetchMetaAnalysis,
    toggleMetaView,
    closeMetaView,
    clearMetaAnalysis
  }
}
```

---

**由于文档已经很长,我将分为两部分创建。现在继续创建第二部分实施计划文档...**

---

**文档版本**: 1.0.0 (Part 1)
**最后更新**: 2025-10-20
**维护者**: InsightReader Team
