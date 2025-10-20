# InsightReader 统一深度分析引擎 (Unified Deep Analysis Engine)

## 文档版本

- **版本号**: 1.0
- **创建日期**: 2025-10-20
- **状态**: 设计阶段

---

## 目录

1. [愿景与战略转向](#愿景与战略转向)
2. [核心架构设计](#核心架构设计)
3. [UI/UX 交互设计](#uiux-交互设计)
4. [AI 功能规格](#ai-功能规格)
5. [数据模型设计](#数据模型设计)
6. [技术实现方案](#技术实现方案)
7. [实施路线图](#实施路线图)
8. [风险评估与应对](#风险评估与应对)
9. [成功指标](#成功指标)

---

## 愿景与战略转向

### 核心理念

这是一次**产品核心架构的范式转移**：

**从**: "按需、即时、低质量"的分析模型
**到**: "预先、整体、高质量"的分析模型

我们选择用一次性的、可控的前期投入（API 成本与处理延迟），来换取整个产品生态（洞察火花、元视角、认知仪表盘）长期、一致、高质量的数据基石。

### 战略目标

#### 1. 根除"鸡肋"体验
- 彻底抛弃基于传统 NLP 和关键词匹配的、不准确的"火花"识别
- 确保每一个呈现给用户的"火花"都经过顶级 LLM 的深度语义理解
- 具备真正的洞察价值

#### 2. 建立"单一数据源" (Single Source of Truth)
- 创建唯一的、结构化的"文章深度分析报告"
- 一旦生成，成为驱动所有 AI 功能的数据中枢
- 确保体验的一致性和可扩展性

#### 3. 追求极致价值
- 目标不再是"标注一些东西"
- 而是**"只标注那些最值得被探索的东西"**

### 战略权衡

| 维度 | 旧模式 | 新模式 |
|------|--------|--------|
| **质量** | 低（NLP 关键词） | 高（GPT-4 深度语义） |
| **成本** | 低（几乎免费） | 中（每篇文章 $0.05-0.20） |
| **响应速度** | 即时 | 延迟 5-30 秒 |
| **数据复用** | 无 | 高（一次分析，处处使用） |
| **可扩展性** | 低 | 高（统一数据源） |
| **用户体验** | 混乱、不准确 | 精准、惊喜 |

---

## 核心架构设计

### 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         用户层 (User Layer)                      │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │  阅读文章    │    │  洞察火花    │    │  元视角      │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ SSE (Server-Sent Events) 实时通知
                              │
┌─────────────────────────────────────────────────────────────────┐
│                       前端层 (Frontend)                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  • 文章渲染器 (带句子级 DOM ID)                          │   │
│  │  • SSE 实时通知监听器                                    │   │
│  │  • 洞察火花渲染引擎                                       │   │
│  │  • 等待状态 UI (脉冲动画)                                │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ REST API
                              │
┌─────────────────────────────────────────────────────────────────┐
│                      后端 API 层 (Backend API)                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  POST /api/v1/articles/save-with-analysis                │   │
│  │  GET  /api/v1/articles/{id}/analysis-report              │   │
│  │  GET  /api/v1/articles/{id}/analysis-status              │   │
│  │  GET  /api/v1/sse/analysis-notifications (SSE)           │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │
┌─────────────────────────────────────────────────────────────────┐
│                    异步任务队列 (Task Queue)                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Celery / RQ / Dramatiq                                  │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐         │   │
│  │  │  Worker 1  │  │  Worker 2  │  │  Worker N  │         │   │
│  │  └────────────┘  └────────────┘  └────────────┘         │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │
┌─────────────────────────────────────────────────────────────────┐
│                   AI 分析服务 (Analysis Service)                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  • 文章预处理 (清洗、分句)                               │   │
│  │  • LLM 调用 (GPT-4o / Gemini)                            │   │
│  │  • JSON 报告生成                                         │   │
│  │  • 报告验证与后处理                                      │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │
┌─────────────────────────────────────────────────────────────────┐
│                      数据持久层 (Database)                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  PostgreSQL (JSONB 字段)                                 │   │
│  │  ┌────────────────┐  ┌────────────────┐                 │   │
│  │  │  articles      │  │  analysis_     │                 │   │
│  │  │  表            │  │  reports 表    │                 │   │
│  │  └────────────────┘  └────────────────┘                 │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 核心工作流程

#### 阶段 1: 文章保存与任务入队 (0-1 秒)

```
用户提交文章 URL
    ↓
后端接收请求
    ↓
1. 保存文章到数据库 (状态: pending_analysis)
2. 将分析任务放入异步队列
3. 立即返回 article_id
    ↓
前端加载干净的阅读界面
```

#### 阶段 2: 后台深度分析 (5-30 秒)

```
Worker 从队列获取任务
    ↓
调用 AI 分析服务
    ↓
1. 文章预处理 (清洗、分句、生成 DOM 路径映射)
2. 调用 LLM (GPT-4o) 执行统一分析 Prompt
3. 解析 LLM 返回的 JSON
4. 验证并后处理数据
    ↓
保存分析报告到数据库
    ↓
更新文章状态 (status: analyzed)
    ↓
通过 SSE 通知前端
```

#### 阶段 3: 洞察呈现 (< 1 秒)

```
前端收到 SSE 事件通知
    ↓
请求分析报告 API
    ↓
获取 JSON 报告
    ↓
渲染洞察火花 (渐显动画)
```

---

## UI/UX 交互设计

### 设计原则：拥抱延迟的艺术

我们不隐藏延迟，而是将延迟**转化为期待与惊喜**。

### 交互时间线

#### 0-1 秒: 初始状态

**视觉呈现**:
- 用户保存文章后，立即进入干净、纯粹、无任何"火花"的阅读界面
- 用户的核心阅读体验不受任何影响

**设计要点**:
- 快速加载原文
- 无 Loading 遮罩阻挡阅读
- 界面干净简洁

#### 1-30 秒: 处理中状态

**视觉提示**:

1. **状态指示器**
   - 位置: 右上角元视角图标 `🧠`
   - 动画: 柔和的脉冲动画或扫描光效
   ```css
   @keyframes pulse-scan {
     0%, 100% { opacity: 0.6; transform: scale(1); }
     50% { opacity: 1; transform: scale(1.05); }
   }
   ```

2. **悬停提示**
   - 文案: "正在为您深度分析文章，高价值洞察即将呈现..."
   - 风格: Glassmorphism 浮层
   - 显示预计时间: "预计还需 15 秒"

3. **进度指示（可选）**
   - 如果分析超过 10 秒，显示阶段提示:
     - "正在理解文章核心概念..."
     - "正在分析论证结构..."
     - "正在提炼关键洞察..."

**设计要点**:
- 微妙、不打扰阅读
- 信息透明、管理预期
- 将等待从"卡顿"变成"期待"

#### 30+ 秒: 完成状态

**视觉呈现**:

1. **魔法般的浮现**
   - 所有洞察火花以**渐显动画**同时出现
   - 从上到下依次浮现（瀑布流效果）
   ```javascript
   sparks.forEach((spark, index) => {
     setTimeout(() => {
       spark.style.animation = 'fade-in-up 0.6s ease-out forwards'
     }, index * 50) // 50ms 延迟
   })
   ```

2. **完成通知**
   - 位置: 右下角 Toast
   - 文案: "✨ 已为您发现 12 个高价值洞察点"
   - 交互: 点击可展开洞察列表

3. **图标状态变化**
   - 元视角图标从"扫描中"变为"已完成"
   - 颜色从灰色变为品牌色

**设计要点**:
- 惊喜感、仪式感
- 强化"AI 智慧注入"的感知
- 提供洞察概览

### 异常状态处理

#### 分析失败

**触发条件**:
- LLM API 调用失败
- 超时（超过 60 秒）
- 解析错误

**视觉呈现**:
- 状态指示器变为警告色
- 悬停提示: "分析遇到问题，您仍可正常阅读。点击重试"
- 提供"重新分析"按钮

#### 部分成功

**触发条件**:
- LLM 返回了数据但部分字段缺失

**视觉呈现**:
- 正常渲染可用的火花
- 在设置中显示: "本文部分洞察功能不可用"

---

## AI 功能规格

### 统一分析 Prompt 设计

#### Prompt 结构

```markdown
# 角色定义

你是一名世界级的跨学科研究分析师，拥有深厚的批判性思维能力和教育心理学背景。你的任务是帮助读者深度理解文章，发现最值得探索的知识点。

# 任务目标

对以下文章进行全面的深度分析，并严格按照指定的 JSON Schema 返回结果。

# 文章内容

"""
{article_content}
"""

# 分析维度

## 1. 元信息分析 (meta_info)

分析以下维度:
- **author_stance**: 作者立场（客观/主观/批判性/辩护性）
- **writing_intent**: 写作意图（教育/说服/娱乐/记录）
- **emotional_tone**: 情感基调（中性/激昂/冷静/讽刺）
- **target_audience**: 目标读者（专业人士/普通大众/学生）
- **timeliness**: 时效性（时效性强/长期有效）

## 2. 核心概念提炼 (concept_sparks)

**严格标准**：
- 仅选择理解本文**核心论点**所必需的概念
- 概念必须是**读者可能陌生**的专业术语或抽象概念
- 数量限制: **3-7 个**
- 质量优先于数量：宁缺毋滥

对于每个概念，提供：
- `text`: 概念原文（精确匹配文章中的文字）
- `sentence_index`: 该概念所在的句子索引（从 0 开始）
- `importance_score`: 重要性评分（1-10）
- `explanation_hint`: 点击后生成卡片的提示词

**示例**：
```json
{
  "text": "元信息",
  "sentence_index": 5,
  "importance_score": 9,
  "explanation_hint": "用一个日常生活中的例子解释'元信息'的概念，并说明它为何重要。"
}
```

## 3. 论证结构分析 (argument_sparks)

识别文章中的关键论证元素：
- **核心观点句** (claim): 作者的主要论点
- **支撑证据句** (evidence): 数据、案例、引用
- **关键转折句** (transition): "然而"、"事实上"等转折

对于每个论证点，提供：
- `type`: claim / evidence / transition
- `text`: 句子原文
- `sentence_index`: 句子索引
- `role_description`: 在论证中的作用

## 4. 知识图谱节点 (knowledge_graph_nodes)

提取 5-10 个可以构建知识网络的核心概念。

## 5. 文章摘要与标签

- `summary`: 150 字左右的核心摘要
- `tags`: 3-5 个主题标签

# 输出格式

严格按照以下 JSON Schema 返回结果（使用 JSON Mode）:

```json
{
  "meta_info": { ... },
  "concept_sparks": [ ... ],
  "argument_sparks": [ ... ],
  "knowledge_graph_nodes": [ ... ],
  "summary": "...",
  "tags": [ ... ]
}
```

# 质量要求

1. **精准性**: 所有引用的文本必须与原文完全一致
2. **可定位性**: sentence_index 必须准确
3. **价值导向**: 只标注真正有价值的内容
4. **结构化**: 严格遵守 JSON Schema
```

### JSON Schema 定义

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["meta_info", "concept_sparks", "summary", "tags"],
  "properties": {
    "meta_info": {
      "type": "object",
      "properties": {
        "author_stance": { "type": "string" },
        "writing_intent": { "type": "string" },
        "emotional_tone": { "type": "string" },
        "target_audience": { "type": "string" },
        "timeliness": { "type": "string" }
      }
    },
    "concept_sparks": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["text", "sentence_index", "importance_score", "explanation_hint"],
        "properties": {
          "text": { "type": "string" },
          "sentence_index": { "type": "integer" },
          "importance_score": { "type": "integer", "minimum": 1, "maximum": 10 },
          "explanation_hint": { "type": "string" }
        }
      }
    },
    "argument_sparks": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["type", "text", "sentence_index", "role_description"],
        "properties": {
          "type": { "enum": ["claim", "evidence", "transition"] },
          "text": { "type": "string" },
          "sentence_index": { "type": "integer" },
          "role_description": { "type": "string" }
        }
      }
    },
    "knowledge_graph_nodes": {
      "type": "array",
      "items": { "type": "string" }
    },
    "summary": { "type": "string", "maxLength": 300 },
    "tags": {
      "type": "array",
      "items": { "type": "string" },
      "minItems": 3,
      "maxItems": 5
    }
  }
}
```

---

## 数据模型设计

### 数据库表结构

#### 1. analysis_reports 表

```sql
CREATE TABLE analysis_reports (
    id SERIAL PRIMARY KEY,
    article_id INTEGER NOT NULL UNIQUE REFERENCES articles(id) ON DELETE CASCADE,

    -- 分析状态
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    -- 状态: pending, processing, completed, failed

    -- 分析报告 (JSONB)
    report_data JSONB,

    -- 版本控制
    analysis_version VARCHAR(10) DEFAULT '1.0',

    -- LLM 元信息
    model_used VARCHAR(50),
    tokens_used INTEGER,
    processing_time_ms INTEGER,

    -- 错误信息
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,

    -- 时间戳
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,

    -- 索引
    INDEX idx_article_id (article_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);
```

#### 2. articles 表 (扩展)

```sql
ALTER TABLE articles ADD COLUMN analysis_status VARCHAR(20) DEFAULT 'pending';
ALTER TABLE articles ADD COLUMN has_sparks BOOLEAN DEFAULT FALSE;
```

#### 3. insight_sparks 表 (可选优化)

用于快速查询火花列表，避免解析 JSONB:

```sql
CREATE TABLE insight_sparks (
    id SERIAL PRIMARY KEY,
    article_id INTEGER NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    report_id INTEGER NOT NULL REFERENCES analysis_reports(id) ON DELETE CASCADE,

    -- 火花类型
    spark_type VARCHAR(20) NOT NULL,
    -- 类型: concept, argument, transition

    -- 火花内容
    text TEXT NOT NULL,
    sentence_index INTEGER NOT NULL,

    -- 额外数据 (JSONB)
    metadata JSONB,

    -- 位置信息 (用于渲染)
    dom_path TEXT,

    -- 索引
    INDEX idx_article_id (article_id),
    INDEX idx_spark_type (spark_type)
);
```

### JSONB 报告数据结构示例

```json
{
  "article_url": "https://example.com/article",
  "analysis_version": "1.0",
  "analyzed_at": "2025-10-20T10:30:00Z",

  "metadata": {
    "title": "理解元信息的重要性",
    "author": "张三",
    "publish_date": "2025-10-15",
    "word_count": 3200,
    "sentence_count": 85
  },

  "meta_info": {
    "author_stance": "批判性",
    "writing_intent": "教育",
    "emotional_tone": "冷静",
    "target_audience": "普通大众",
    "timeliness": "长期有效"
  },

  "concept_sparks": [
    {
      "text": "元信息",
      "sentence_index": 5,
      "importance_score": 9,
      "explanation_hint": "用一个日常生活中的例子解释'元信息'的概念。",
      "dom_path": "#sentence-5 > span:nth-child(2)"
    },
    {
      "text": "认知闭环",
      "sentence_index": 23,
      "importance_score": 8,
      "explanation_hint": "解释什么是认知闭环，以及如何打破它。",
      "dom_path": "#sentence-23 > span:nth-child(1)"
    }
  ],

  "argument_sparks": [
    {
      "type": "claim",
      "text": "元信息思维是高效学习的核心能力。",
      "sentence_index": 3,
      "role_description": "文章核心论点",
      "dom_path": "#sentence-3"
    },
    {
      "type": "evidence",
      "text": "研究表明，具备元信息意识的学生学习效率提升40%。",
      "sentence_index": 12,
      "role_description": "数据支撑",
      "dom_path": "#sentence-12"
    }
  ],

  "knowledge_graph_nodes": [
    "元信息",
    "批判性思维",
    "认知闭环",
    "学习方法论",
    "知识管理"
  ],

  "summary": "本文探讨了'元信息'思维在学习中的重要性。作者指出，元信息是关于信息的信息，包括信息的来源、可靠性、时效性等。通过培养元信息意识，读者可以建立更高效的学习体系，避免陷入认知闭环。",

  "tags": ["思维模型", "学习方法", "批判性思维", "认知科学"]
}
```

---

## 技术实现方案

### 后端技术栈

#### 1. 异步任务队列选型

**推荐: Celery**

理由:
- Python 生态成熟度高
- 支持任务优先级
- 完善的监控工具 (Flower)
- 失败重试机制

**配置示例**:

```python
# backend/app/celery_app.py
from celery import Celery

celery_app = Celery(
    'insightreader',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1'
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=90,  # 90秒超时
    task_soft_time_limit=60,
)
```

#### 2. SSE (Server-Sent Events) 实时通知

**推荐: FastAPI StreamingResponse**

```python
# backend/app/api/sse.py
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from asyncio import Queue
import asyncio
import json

router = APIRouter()

# 用户通知队列
user_queues: Dict[int, Queue] = {}

async def get_user_queue(user_id: int) -> Queue:
    """获取或创建用户的通知队列"""
    if user_id not in user_queues:
        user_queues[user_id] = Queue()
    return user_queues[user_id]

async def notify_analysis_complete(user_id: int, article_id: int):
    """通知用户分析完成"""
    queue = await get_user_queue(user_id)
    await queue.put({
        "event": "analysis_complete",
        "data": {
            "article_id": article_id
        }
    })

async def event_generator(user_id: int):
    """SSE 事件生成器"""
    queue = await get_user_queue(user_id)

    # 发送初始连接事件
    yield f"event: connected\ndata: {json.dumps({'user_id': user_id})}\n\n"

    while True:
        try:
            # 等待新事件（带超时，用于发送心跳）
            message = await asyncio.wait_for(queue.get(), timeout=30.0)

            # 发送事件
            event_type = message.get("event", "message")
            data = json.dumps(message.get("data", {}))
            yield f"event: {event_type}\ndata: {data}\n\n"

        except asyncio.TimeoutError:
            # 发送心跳保持连接
            yield f"event: heartbeat\ndata: {json.dumps({'timestamp': time.time()})}\n\n"

@router.get("/api/v1/sse/analysis-notifications")
async def sse_notifications(user_id: int):
    """SSE 端点"""
    return StreamingResponse(
        event_generator(user_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # 禁用 nginx 缓冲
        }
    )
```

#### 3. AI 分析服务

```python
# backend/app/services/unified_analysis_service.py
from openai import OpenAI
from app.config import settings
import json

class UnifiedAnalysisService:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url
        )

    async def analyze_article(self, article_content: str) -> dict:
        """
        执行统一深度分析
        """
        # 1. 预处理：分句
        sentences = self._split_sentences(article_content)

        # 2. 调用 LLM
        response = self.client.chat.completions.create(
            model=settings.default_model,
            messages=[
                {
                    "role": "system",
                    "content": self._build_system_prompt()
                },
                {
                    "role": "user",
                    "content": article_content
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
        )

        # 3. 解析并验证
        report = json.loads(response.choices[0].message.content)

        # 4. 后处理：添加 DOM 路径
        report = self._add_dom_paths(report, sentences)

        # 5. 验证
        self._validate_report(report)

        return {
            "report": report,
            "metadata": {
                "model": response.model,
                "tokens": response.usage.total_tokens,
                "processing_time_ms": response.response_ms
            }
        }

    def _split_sentences(self, text: str) -> List[str]:
        """
        智能分句
        """
        # 使用 nltk 或正则表达式
        import re
        sentences = re.split(r'[。！？\n]', text)
        return [s.strip() for s in sentences if s.strip()]

    def _add_dom_paths(self, report: dict, sentences: List[str]) -> dict:
        """
        为每个火花添加 DOM 路径
        """
        for spark in report.get('concept_sparks', []):
            idx = spark['sentence_index']
            spark['dom_path'] = f"#sentence-{idx}"

        for spark in report.get('argument_sparks', []):
            idx = spark['sentence_index']
            spark['dom_path'] = f"#sentence-{idx}"

        return report

    def _validate_report(self, report: dict):
        """
        验证报告结构
        """
        required_fields = ['meta_info', 'concept_sparks', 'summary', 'tags']
        for field in required_fields:
            if field not in report:
                raise ValueError(f"Missing required field: {field}")
```

### 前端技术实现

#### 1. 句子级 DOM 渲染

```typescript
// frontend/app/composables/useArticleRenderer.ts

export const useArticleRenderer = () => {
  /**
   * 将文章内容渲染为带句子 ID 的 HTML
   */
  const renderArticleWithSentenceIds = (content: string): string => {
    const sentences = splitIntoSentences(content)

    return sentences.map((sentence, index) => {
      return `<span id="sentence-${index}" data-sentence-index="${index}">${sentence}</span>`
    }).join('')
  }

  /**
   * 智能分句
   */
  const splitIntoSentences = (text: string): string[] => {
    // 使用正则表达式分句
    const sentences = text.split(/([。！？\n])/).reduce((acc, part, i, arr) => {
      if (i % 2 === 0 && part) {
        const punctuation = arr[i + 1] || ''
        acc.push(part + punctuation)
      }
      return acc
    }, [] as string[])

    return sentences.filter(s => s.trim())
  }

  return {
    renderArticleWithSentenceIds
  }
}
```

#### 2. SSE 监听

```typescript
// frontend/app/composables/useAnalysisNotifications.ts

export const useAnalysisNotifications = () => {
  const { user } = useAuth()
  const config = useRuntimeConfig()
  let eventSource: EventSource | null = null

  const connect = () => {
    if (!user.value) return

    const sseUrl = `${config.public.apiBase}/api/v1/sse/analysis-notifications?user_id=${user.value.id}`
    eventSource = new EventSource(sseUrl)

    // 监听连接事件
    eventSource.addEventListener('connected', (e) => {
      console.log('✅ SSE 已连接:', JSON.parse(e.data))
    })

    // 监听分析完成事件
    eventSource.addEventListener('analysis_complete', (e) => {
      const data = JSON.parse(e.data)
      handleAnalysisComplete(data.article_id)
    })

    // 监听心跳（保持连接）
    eventSource.addEventListener('heartbeat', (e) => {
      console.log('💓 SSE 心跳')
    })

    // 错误处理
    eventSource.onerror = (error) => {
      console.error('❌ SSE 连接错误:', error)
      // EventSource 会自动重连
    }
  }

  const handleAnalysisComplete = async (articleId: number) => {
    // 获取分析报告
    const report = await $fetch(`/api/v1/articles/${articleId}/analysis-report`)

    // 触发火花渲染
    const { renderSparks } = useSparkRenderer()
    renderSparks(report)

    // 显示完成通知
    showToast({
      message: `✨ 已为您发现 ${report.concept_sparks.length} 个高价值洞察点`,
      type: 'success'
    })
  }

  const disconnect = () => {
    if (eventSource) {
      eventSource.close()
      eventSource = null
    }
  }

  onMounted(() => {
    connect()
  })

  onUnmounted(() => {
    disconnect()
  })

  return {
    connect,
    disconnect
  }
}
```

#### 3. 火花渲染引擎

```typescript
// frontend/app/composables/useSparkRenderer.ts

export const useSparkRenderer = () => {
  /**
   * 渲染概念火花
   */
  const renderConceptSparks = (sparks: ConceptSpark[]) => {
    sparks.forEach((spark, index) => {
      const targetElement = document.querySelector(spark.dom_path)
      if (!targetElement) {
        console.warn(`无法找到元素: ${spark.dom_path}`)
        return
      }

      // 创建火花元素
      const sparkEl = createConceptSparkElement(spark)

      // 延迟渲染（瀑布流效果）
      setTimeout(() => {
        highlightTextInElement(targetElement, spark.text, sparkEl)
      }, index * 50)
    })
  }

  /**
   * 创建概念火花元素
   */
  const createConceptSparkElement = (spark: ConceptSpark): HTMLElement => {
    const span = document.createElement('span')
    span.className = 'concept-spark'
    span.dataset.sparkId = spark.id

    // 样式
    span.style.borderBottom = '2px dotted #10b981'
    span.style.cursor = 'pointer'
    span.style.position = 'relative'
    span.style.animation = 'fade-in-up 0.6s ease-out forwards'
    span.style.opacity = '0'

    // 点击事件
    span.addEventListener('click', async (e) => {
      e.stopPropagation()
      await showConceptExplanation(spark)
    })

    return span
  }

  /**
   * 高亮文本
   */
  const highlightTextInElement = (
    container: Element,
    text: string,
    highlightEl: HTMLElement
  ) => {
    const walker = document.createTreeWalker(
      container,
      NodeFilter.SHOW_TEXT
    )

    let node: Text | null
    while (node = walker.nextNode() as Text) {
      const index = node.textContent?.indexOf(text)
      if (index !== undefined && index >= 0) {
        const parent = node.parentNode
        if (!parent) continue

        const before = node.textContent!.substring(0, index)
        const after = node.textContent!.substring(index + text.length)

        highlightEl.textContent = text

        if (before) parent.insertBefore(document.createTextNode(before), node)
        parent.insertBefore(highlightEl, node)
        if (after) parent.insertBefore(document.createTextNode(after), node)
        parent.removeChild(node)

        break
      }
    }
  }

  /**
   * 显示概念解释卡片
   */
  const showConceptExplanation = async (spark: ConceptSpark) => {
    // 调用 AI 生成解释
    const explanation = await $fetch('/api/v1/sparks/explain', {
      method: 'POST',
      body: {
        hint: spark.explanation_hint,
        concept: spark.text
      }
    })

    // 显示卡片
    showSparkCard({
      title: spark.text,
      content: explanation,
      type: 'concept'
    })
  }

  return {
    renderConceptSparks,
    renderArgumentSparks,
    renderSparks
  }
}
```

---

## 实施路线图

### MVP (最小可行产品) - 4 周

**目标**: 验证核心价值，上线概念火花功能

#### Week 1: 后端基础设施

**任务**:
- [ ] 配置 Celery 异步任务队列
- [ ] 实现 `analysis_reports` 数据表
- [ ] 实现 SSE 通知服务
- [ ] 编写统一分析 Prompt V1

**验收标准**:
- 任务队列能正常运行
- SSE 能推送事件消息
- Prompt 能生成符合 Schema 的 JSON

#### Week 2: AI 分析服务

**任务**:
- [ ] 实现 `UnifiedAnalysisService`
- [ ] 实现文章预处理（分句、清洗）
- [ ] 实现 LLM 调用与报告生成
- [ ] 实现错误处理与重试机制

**验收标准**:
- 能成功分析一篇 3000 字文章
- 报告数据结构正确
- 错误能正确捕获并记录

#### Week 3: 前端渲染引擎

**任务**:
- [ ] 实现句子级 DOM 渲染
- [ ] 实现 SSE 事件监听
- [ ] 实现概念火花渲染
- [ ] 实现等待状态 UI

**验收标准**:
- 文章能正确渲染为带 ID 的 HTML
- 火花能准确高亮
- 动画流畅

#### Week 4: 集成与测试

**任务**:
- [ ] 端到端集成测试
- [ ] 性能优化（超过 5000 字的文章）
- [ ] 用户测试与反馈收集
- [ ] Bug 修复

**验收标准**:
- 完整流程无阻塞
- 用户反馈积极
- 性能达标（5000 字文章 < 30 秒）

---

### V2 功能扩展 - 2 周

**目标**: 丰富洞察维度

**任务**:
- [ ] 上线论证火花渲染
- [ ] 打通元视角功能（复用 meta_info）
- [ ] 优化 Prompt（提升准确率）

---

### V3 认知仪表盘 - 4 周

**目标**: 利用积累数据构建护城河

**任务**:
- [ ] 开发知识图谱可视化
- [ ] 开发好奇心指纹
- [ ] 开发阅读轨迹分析

---

## 风险评估与应对

### 风险 1: LLM 成本超预算

**风险等级**: 高

**应对策略**:
1. **成本监控**: 实时统计每日 API 调用成本
2. **用户限制**:
   - 免费用户: 每月 10 篇
   - 付费用户: 每月 100 篇
3. **模型降级**:
   - 短文（< 1000 字）使用 GPT-4o-mini
   - 长文使用 GPT-4o

### 风险 2: 分析质量不达标

**风险等级**: 高

**应对策略**:
1. **Prompt 迭代**: 收集真实文章测试，持续优化
2. **人工审核**: MVP 阶段每篇报告人工审核
3. **用户反馈**: 提供"火花不准确"反馈按钮

### 风险 3: 用户不接受延迟

**风险等级**: 中

**应对策略**:
1. **UX 设计**: 将延迟转化为期待（脉冲动画、进度提示）
2. **教育引导**: 首次使用时显示"高质量分析需要时间"的引导
3. **后台预加载**: 检测用户正在浏览的文章列表，提前分析

### 风险 4: SSE 连接不稳定

**风险等级**: 低

**应对策略**:
1. **自动重连**: EventSource 原生支持自动重连
2. **轮询降级**: SSE 失败时降级为轮询
3. **状态持久化**: 分析状态存储在数据库，刷新页面能恢复
4. **心跳机制**: 每30秒发送心跳保持连接

---

## 成功指标

### 技术指标

- **分析成功率**: > 95%
- **平均分析时间**: < 20 秒（3000 字文章）
- **火花准确率**: > 85%（用户反馈）
- **系统可用性**: > 99.5%

### 产品指标

- **火花点击率**: > 30%（用户点击过至少 1 个火花）
- **用户满意度**: > 4.0/5.0
- **留存率**: Week 1 > 40%

### 商业指标

- **单篇分析成本**: < $0.15
- **付费转化率**: > 5%

---

## 附录

### A. 示例文章分析报告

见 `/examples/sample-analysis-report.json`

### B. Prompt 优化历史

见 `/docs/prompt-evolution.md`

### C. 性能测试报告

见 `/docs/performance-benchmarks.md`

---

**文档状态**: ✅ 已完成
**下一步**: 开始后端实现
