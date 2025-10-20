# InsightReader "洞察火花" (Insight Spark) 功能设计文档

## 文档信息
- **版本**: v1.0
- **创建日期**: 2025-10-20
- **负责人**: Claude
- **状态**: 设计阶段
- **核心理念**: "邀请，而非打扰"

---

## 目录
1. [核心愿景与价值主张](#核心愿景与价值主张)
2. [功能定义与用户场景](#功能定义与用户场景)
3. [设计原则](#设计原则)
4. [视觉设计规范](#视觉设计规范)
5. [技术架构](#技术架构)
6. [两阶段分析引擎](#两阶段分析引擎)
7. [前端实现方案](#前端实现方案)
8. [后端实现方案](#后端实现方案)
9. [性能优化策略](#性能优化策略)
10. [数据流与API设计](#数据流与api设计)
11. [用户体验细节](#用户体验细节)
12. [开发路线图](#开发路线图)

---

## 核心愿景与价值主张

### 功能愿景

"洞察火花"旨在将静态的文本页面，转变为一个**充满"隐藏宝藏"的互动式探索地图**。它不是一个功能，而是一种阅读体验的升华，其核心是**催化用户的好奇心**，并对其进行即时、精准的回报。

**关键理念**：让每一次阅读都可能成为一次发现之旅。

### 核心用户价值

#### 1. 无扰的好奇心催化剂 (Unobtrusive Curiosity Catalyst)
通过极其微妙的视觉提示，激发用户探索的欲望，而完全不打断其核心的阅读心流。

**设计哲学**：
- 视觉提示如同"呼吸"般自然
- 永不遮挡文本主体
- 遵循"渐进式显示"原则

#### 2. 按需的即时深度 (On-demand Instant Depth)
将昂贵且强大的 AI 分析能力，精确地应用在用户真正感兴趣的"点"上，避免资源浪费，同时提供最大价值。

**价值公式**：
```
用户价值 = AI 能力 × 用户意图的精准度
```

#### 3. 主动的探索引导 (Proactive Exploration Guidance)
不是等待用户提问，而是通过智能标记，**主动但温和地**建议用户"这里可能值得深入"。

---

## 功能定义与用户场景

### 什么是"洞察火花"？

"洞察火花"是一种**智能文本增强系统**，它能够：
1. **自动识别**文章中值得深入探索的关键点（概念、论证、实体）
2. **非侵入式标记**这些关键点（微妙的视觉提示）
3. **按需生成**深度洞察（只在用户点击时调用 AI）

### 典型用户场景

#### 场景 1：阅读技术文章
```
用户：正在阅读一篇关于"分布式系统"的文章

文本："在CAP定理中，一致性(Consistency)和可用性(Availability)..."
      ~~~~~~~~~~~~~~~~                     ~~~~~~~~~~~~~~

视觉：用户看到"CAP定理"下方有微妙的emerald色虚线

交互：
1. 鼠标悬停 → 虚线变实，出现 🔍 图标和提示文字"解释这个概念"
2. 点击 → 火花闪烁动画 → 右侧弹出 AI 洞察卡片
3. AI 生成："CAP定理是分布式系统设计的基础理论，它指出..."

价值：用户无需离开当前阅读，即时获得深度解释
```

#### 场景 2：阅读新闻报道
```
用户：阅读一篇商业新闻

文本："埃隆·马斯克(Elon Musk)表示，根据最新数据显示，特斯拉Q3营收增长42%..."
      ~~~~~~~~~~~~~~                                                ~~~

视觉：
- "埃隆·马斯克"旁边有半透明 👤 图标
- "42%"下方有半透明虚线，末尾有 💡 图标

交互：
1. 点击 👤 → AI 提供人物背景、最新动态
2. 点击 💡 → AI 分析"42%增长"的含义、行业对比、可能影响

价值：深度理解新闻背后的上下文和数据含义
```

#### 场景 3：学习学术论文
```
用户：阅读机器学习论文

文本："我们使用Transformer架构，结合自注意力机制(self-attention)..."
              ~~~~~~~                ~~~~~~~~~~~~~~~~

视觉：两处都有概念火花标记

交互：
1. 点击"Transformer" → AI 解释架构原理、应用场景
2. 点击"自注意力机制" → AI 提供数学原理、图解说明
3. 两个洞察可以互相关联，形成知识网络

价值：将艰深的学术概念拆解为易懂的解释
```

---

## 设计原则

### 1. 邀请，而非打扰 (Invite, Don't Interrupt)

**具体实践**：
- ❌ 不使用：弹窗、模态框、高饱和度颜色
- ✅ 使用：渐变透明度、微妙虚线、柔和动画

**代码示例**：
```css
/* 错误示范 */
.spark-wrong {
  background: yellow;
  font-weight: bold;
  animation: blink 0.5s infinite;
}

/* 正确示范 */
.spark-correct {
  border-bottom: 1px dashed rgba(16, 185, 129, 0.3);
  transition: all 0.2s ease;
}

.spark-correct:hover {
  border-bottom-color: rgba(16, 185, 129, 0.8);
  border-bottom-width: 2px;
}
```

### 2. 宁缺毋滥 (Quality Over Quantity)

**识别准确性要求**：
- 精确度 > 70%（被标记的内容确实值得探索）
- 召回率可以低（漏掉一些不要紧，标错了才是灾难）

**评估指标**：
```
火花价值得分 = 点击率 × 用户停留时间 × 未关闭率
```

### 3. 渐进式披露 (Progressive Disclosure)

**视觉层级**：
```
默认状态 (opacity: 0.3)
    ↓ 鼠标进入附近区域
半激活 (opacity: 0.6)
    ↓ 鼠标悬停在火花上
完全激活 (opacity: 1.0 + 图标 + 提示文字)
    ↓ 点击
AI 洞察生成
```

### 4. 性能优先 (Performance First)

**黄金规则**：
- 页面加载时间增加 < 100ms
- 火花渲染不引起可见的重排 (reflow)
- 轻量级 NLP 处理时间 < 500ms
- AI 调用仅在用户点击时发生

---

## 视觉设计规范

### 火花类型与样式

#### 1. 概念火花 (Concept Spark)

**适用场景**：专业术语、技术概念、行业黑话

**视觉规范**：
```css
.concept-spark {
  /* 基础样式 */
  border-bottom: 1px dashed rgba(16, 185, 129, 0.3);
  cursor: help;
  position: relative;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 悬停状态 */
.concept-spark:hover {
  border-bottom: 2px solid rgba(16, 185, 129, 0.8);
  border-bottom-style: solid;
}

/* 图标 */
.concept-spark::after {
  content: '🔍';
  position: absolute;
  right: -20px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 14px;
  opacity: 0;
  transition: opacity 0.2s;
}

.concept-spark:hover::after {
  opacity: 1;
}
```

**提示文字**：
- 简短："解释这个概念"
- 中等："了解 [概念名] 的含义"
- 详细："深入理解 [概念名] 及其应用"

#### 2. 论证火花 (Argument Spark)

**适用场景**：包含数据、逻辑推理、因果关系的句子

**视觉规范**：
```css
.argument-spark {
  position: relative;
  padding-right: 24px;
}

/* 图标放在句子末尾 */
.argument-spark::after {
  content: '💡';
  position: absolute;
  right: 0;
  top: 0;
  font-size: 16px;
  opacity: 0.5;
  transition: all 0.2s;
}

.argument-spark:hover::after {
  opacity: 1;
  transform: scale(1.1);
}
```

**提示文字**：
- 数据类："查看数据分析"
- 逻辑类："拆解推理逻辑"
- 因果类："理解因果关系"

#### 3. 实体火花 (Entity Spark)

**适用场景**：人名、地名、组织名、产品名

**视觉规范**：
```css
.entity-spark {
  position: relative;
  padding-right: 20px;
  display: inline-flex;
  align-items: center;
}

.entity-spark::after {
  content: '👤'; /* 或 🏢、🌍 根据实体类型 */
  margin-left: 4px;
  font-size: 12px;
  opacity: 0.5;
  transition: all 0.2s;
}

.entity-spark:hover::after {
  opacity: 1;
}
```

**图标映射**：
- 人名：👤
- 组织/公司：🏢
- 地点：🌍
- 产品/品牌：📦

**提示文字**：
- "了解 [人名] 的背景"
- "关于 [公司名] 的更多信息"
- "探索 [地名] 的相关内容"

### 颜色系统

**主题色：Emerald（翡翠绿）**
```css
:root {
  /* 火花专用颜色 */
  --spark-emerald-50: rgba(16, 185, 129, 0.05);
  --spark-emerald-100: rgba(16, 185, 129, 0.1);
  --spark-emerald-300: rgba(16, 185, 129, 0.3);
  --spark-emerald-500: rgba(16, 185, 129, 0.5);
  --spark-emerald-700: rgba(16, 185, 129, 0.7);
  --spark-emerald-900: rgba(16, 185, 129, 0.9);

  /* 黄金比例透明度 */
  --spark-opacity-rest: 0.3;      /* 静止状态 */
  --spark-opacity-hover: 0.618;   /* 悬停状态（黄金比例）*/
  --spark-opacity-active: 1.0;    /* 激活状态 */
}
```

### 动画规范

#### 火花出现动画
```css
@keyframes spark-appear {
  from {
    opacity: 0;
    transform: translateY(2px);
  }
  to {
    opacity: var(--spark-opacity-rest);
    transform: translateY(0);
  }
}

.spark {
  animation: spark-appear 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
```

#### 点击时的"闪烁"动画
```css
@keyframes spark-flash {
  0% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.3;
    transform: scale(1.05);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

.spark-clicked {
  animation: spark-flash 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}
```

---

## 技术架构

### 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        用户界面层                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  ArticlePane (文章展示)                               │   │
│  │  ├─ SparkRenderer (火花渲染器)                        │   │
│  │  ├─ SparkTooltip (火花提示)                          │   │
│  │  └─ SparkHighlight (火花高亮)                        │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  InsightPane (洞察面板)                               │   │
│  │  └─ SparkInsightCard (火花洞察卡片)                   │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      前端业务逻辑层                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  useSparkAnalyzer (火花分析 Composable)               │   │
│  │  ├─ analyzeText() - 调用后端分析                      │   │
│  │  ├─ renderSparks() - 渲染火花到 DOM                   │   │
│  │  └─ trackSparkInteraction() - 跟踪用户交互            │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  useSparkInsight (火花洞察 Composable)                │   │
│  │  ├─ generateInsight() - 生成火花洞察                  │   │
│  │  └─ cacheInsight() - 缓存已生成的洞察                 │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      后端服务层                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  SparkAnalysisService (火花分析服务)                  │   │
│  │  ├─ Stage 1: 轻量级 NLP 扫描                          │   │
│  │  │   ├─ NER (命名实体识别)                            │   │
│  │  │   ├─ 关键词提取 (TF-IDF/TextRank)                  │   │
│  │  │   └─ 句法分析 (依存关系)                           │   │
│  │  ├─ Stage 2: AI 洞察生成 (按需)                       │   │
│  │  │   └─ LLM API 调用 (GPT-4o)                        │   │
│  │  └─ 缓存层 (Redis)                                    │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 数据流

```
用户粘贴文章
    ↓
前端发送文本到后端
    ↓
[Stage 1] 轻量级 NLP 扫描 (< 500ms)
    ├─ spaCy 提取实体 (人名、地名、组织)
    ├─ TextRank 提取关键概念
    └─ 句法分析识别论证句
    ↓
返回火花位置数据 [{type, start, end, text}]
    ↓
前端渲染火花 (DOM 注入 <span> 标签)
    ↓
用户看到文章 + 微妙的火花标记
    ↓
用户点击某个火花
    ↓
[Stage 2] AI 洞察生成 (SSE 流式)
    ├─ 根据火花类型选择 prompt
    ├─ 调用 GPT-4o API
    └─ 流式返回洞察内容
    ↓
右侧面板显示洞察卡片
```

---

## 两阶段分析引擎

### Stage 1: 轻量级 NLP 扫描

**目标**：快速、廉价地识别所有潜在的"火花"位置

**技术栈**：
- **Python**: spaCy (中文: `zh_core_web_sm`, 英文: `en_core_web_sm`)
- **关键词提取**: jieba + TextRank (中文), RAKE (英文)
- **正则表达式**: 识别特定模式（数字、百分比、比较词）

#### 实现方案

**1. 实体识别 (Entity Recognition)**

```python
import spacy

# 加载模型
nlp_zh = spacy.load("zh_core_web_sm")
nlp_en = spacy.load("en_core_web_sm")

def extract_entities(text: str, lang: str = "zh") -> List[Dict]:
    """提取命名实体"""
    nlp = nlp_zh if lang == "zh" else nlp_en
    doc = nlp(text)

    entities = []
    for ent in doc.ents:
        if ent.label_ in ["PERSON", "ORG", "GPE", "PRODUCT"]:
            entities.append({
                "type": "entity",
                "subtype": map_entity_type(ent.label_),
                "text": ent.text,
                "start": ent.start_char,
                "end": ent.end_char,
                "icon": get_entity_icon(ent.label_)
            })

    return entities

def map_entity_type(spacy_label: str) -> str:
    """映射 spaCy 实体类型到我们的分类"""
    mapping = {
        "PERSON": "person",
        "ORG": "organization",
        "GPE": "location",
        "PRODUCT": "product"
    }
    return mapping.get(spacy_label, "entity")

def get_entity_icon(label: str) -> str:
    """获取实体图标"""
    icons = {
        "PERSON": "👤",
        "ORG": "🏢",
        "GPE": "🌍",
        "PRODUCT": "📦"
    }
    return icons.get(label, "🔖")
```

**2. 概念提取 (Concept Extraction)**

```python
from textrank4zh import TextRank4Keyword
import jieba.analyse

def extract_concepts(text: str, lang: str = "zh") -> List[Dict]:
    """提取关键概念"""
    concepts = []

    if lang == "zh":
        # 使用 TextRank 提取关键词
        tr4kw = TextRank4Keyword()
        tr4kw.analyze(text, window=5, lower=True)

        keywords = tr4kw.get_keywords(num=20, word_min_len=2)

        for kw in keywords:
            # 在原文中查找关键词位置
            start = text.find(kw.word)
            if start != -1:
                concepts.append({
                    "type": "concept",
                    "text": kw.word,
                    "start": start,
                    "end": start + len(kw.word),
                    "weight": kw.weight,
                    "icon": "🔍"
                })
    else:
        # 英文使用 RAKE 算法
        from rake_nltk import Rake
        rake = Rake()
        rake.extract_keywords_from_text(text)
        phrases = rake.get_ranked_phrases()[:20]

        for phrase in phrases:
            start = text.find(phrase)
            if start != -1:
                concepts.append({
                    "type": "concept",
                    "text": phrase,
                    "start": start,
                    "end": start + len(phrase),
                    "icon": "🔍"
                })

    return concepts
```

**3. 论证识别 (Argument Detection)**

```python
import re

def extract_arguments(text: str, lang: str = "zh") -> List[Dict]:
    """识别包含论证的句子"""
    arguments = []

    # 分句
    sentences = split_sentences(text)

    for sent in sentences:
        score = 0
        triggers = []

        # 检测因果关系词
        causal_patterns = {
            "zh": ["因为", "由于", "因此", "所以", "导致", "造成"],
            "en": ["because", "therefore", "thus", "hence", "consequently"]
        }
        for word in causal_patterns.get(lang, []):
            if word in sent:
                score += 2
                triggers.append("causal")

        # 检测数据/百分比
        if re.search(r'\d+%|\d+\.\d+%|\d+倍', sent):
            score += 3
            triggers.append("data")

        # 检测比较级
        comparison_patterns = {
            "zh": ["更", "最", "相比", "对比", "优于", "劣于"],
            "en": ["more", "most", "better", "worse", "compared to"]
        }
        for word in comparison_patterns.get(lang, []):
            if word in sent:
                score += 1
                triggers.append("comparison")

        # 如果得分 >= 3，标记为论证句
        if score >= 3:
            start = text.find(sent)
            if start != -1:
                arguments.append({
                    "type": "argument",
                    "text": sent,
                    "start": start,
                    "end": start + len(sent),
                    "score": score,
                    "triggers": triggers,
                    "icon": "💡"
                })

    return arguments

def split_sentences(text: str) -> List[str]:
    """分句"""
    import re
    # 简化版分句，实际应使用更复杂的算法
    sentences = re.split(r'[。！？.!?]', text)
    return [s.strip() for s in sentences if len(s.strip()) > 10]
```

**4. 整合与过滤**

```python
def analyze_sparks(text: str, lang: str = "zh") -> Dict:
    """整合所有火花分析"""
    # 提取所有类型的火花
    entities = extract_entities(text, lang)
    concepts = extract_concepts(text, lang)
    arguments = extract_arguments(text, lang)

    # 合并
    all_sparks = entities + concepts + arguments

    # 去重（同一位置可能被多次标记）
    all_sparks = deduplicate_sparks(all_sparks)

    # 过滤低质量火花
    all_sparks = filter_sparks(all_sparks)

    # 限制数量（避免过度标记）
    all_sparks = all_sparks[:50]

    # 按位置排序
    all_sparks.sort(key=lambda x: x['start'])

    return {
        "sparks": all_sparks,
        "total_count": len(all_sparks),
        "stats": {
            "entities": len([s for s in all_sparks if s['type'] == 'entity']),
            "concepts": len([s for s in all_sparks if s['type'] == 'concept']),
            "arguments": len([s for s in all_sparks if s['type'] == 'argument'])
        }
    }

def deduplicate_sparks(sparks: List[Dict]) -> List[Dict]:
    """去除重叠的火花"""
    # 按权重排序，保留高权重的
    sparks.sort(key=lambda x: x.get('weight', 0), reverse=True)

    result = []
    occupied_ranges = []

    for spark in sparks:
        start, end = spark['start'], spark['end']
        # 检查是否与已有火花重叠
        overlap = False
        for occ_start, occ_end in occupied_ranges:
            if not (end <= occ_start or start >= occ_end):
                overlap = True
                break

        if not overlap:
            result.append(spark)
            occupied_ranges.append((start, end))

    return result

def filter_sparks(sparks: List[Dict]) -> List[Dict]:
    """过滤低质量火花"""
    filtered = []

    for spark in sparks:
        # 过滤太短的概念（< 2字符）
        if spark['type'] == 'concept' and len(spark['text']) < 2:
            continue

        # 过滤常见词（的、了、是等）
        if spark['text'] in ['的', '了', '是', '在', 'the', 'is', 'a', 'an']:
            continue

        # 过滤权重太低的概念
        if spark['type'] == 'concept' and spark.get('weight', 0) < 0.1:
            continue

        filtered.append(spark)

    return filtered
```

### Stage 2: AI 洞察生成

**目标**：根据火花类型，生成精准、有价值的洞察

**技术栈**：
- OpenAI GPT-4o API
- 专门设计的 Prompt 模板
- SSE 流式响应

#### Prompt 设计

**1. 概念火花 Prompt**

```python
CONCEPT_SPARK_PROMPT = """你是一个专业的知识解释助手。用户正在阅读文章时，对某个概念感兴趣。

**上下文**：
{context}

**用户关注的概念**：
"{concept}"

**任务**：
请用简洁、清晰的语言解释这个概念。要求：
1. 首先用一句话（不超过30字）给出核心定义
2. 然后用2-3句话展开说明（包括应用场景、重要性）
3. 如果可能，举一个简单的例子
4. 总字数控制在150字以内

**注意**：
- 语言要通俗易懂，避免过度专业化
- 直接解释，不要有"这个概念是指..."这样的开场白
- 如果是缩写，先给出全称

请开始你的解释：
"""

def generate_concept_insight_prompt(concept: str, context: str) -> str:
    """生成概念火花的 prompt"""
    return CONCEPT_SPARK_PROMPT.format(
        concept=concept,
        context=context
    )
```

**2. 论证火花 Prompt**

```python
ARGUMENT_SPARK_PROMPT = """你是一个专业的逻辑分析助手。用户正在阅读文章时，对某个论证或数据感兴趣。

**上下文**：
{context}

**用户关注的内容**：
"{argument}"

**检测到的特征**：
{triggers}

**任务**：
根据检测到的特征，提供相应的分析：
- 如果包含数据/百分比：解读数据的含义，提供行业对比或历史趋势
- 如果包含因果关系：拆解推理逻辑，指出前提和结论
- 如果包含比较：分析比较的维度和公平性

要求：
1. 直接进入分析，不要重复原文
2. 提供额外的视角或信息
3. 总字数控制在200字以内

请开始你的分析：
"""

def generate_argument_insight_prompt(
    argument: str,
    context: str,
    triggers: List[str]
) -> str:
    """生成论证火花的 prompt"""
    trigger_desc = "、".join(triggers)
    return ARGUMENT_SPARK_PROMPT.format(
        argument=argument,
        context=context,
        triggers=trigger_desc
    )
```

**3. 实体火花 Prompt**

```python
ENTITY_SPARK_PROMPT = """你是一个专业的背景信息提供助手。用户正在阅读文章时，对某个{entity_type}感兴趣。

**上下文**：
{context}

**用户关注的{entity_type}**：
"{entity}"

**任务**：
提供这个{entity_type}的关键背景信息。要求：
1. 简要介绍（身份、地位、领域）
2. 最相关的近期动态或历史背景（1-2点）
3. 与文章内容的关联性
4. 总字数控制在150字以内

请提供背景信息：
"""

ENTITY_TYPE_NAMES = {
    "person": "人物",
    "organization": "组织",
    "location": "地点",
    "product": "产品"
}

def generate_entity_insight_prompt(
    entity: str,
    entity_type: str,
    context: str
) -> str:
    """生成实体火花的 prompt"""
    type_name = ENTITY_TYPE_NAMES.get(entity_type, "实体")
    return ENTITY_SPARK_PROMPT.format(
        entity_type=type_name,
        entity=entity,
        context=context
    )
```

---

## 前端实现方案

### 组件结构

```
components/
├── spark/
│   ├── SparkRenderer.vue        # 火花渲染器（核心）
│   ├── SparkTooltip.vue         # 火花提示框
│   ├── SparkInsightCard.vue     # 火花洞察卡片
│   └── SparkSettings.vue        # 火花设置面板
```

### 核心 Composable: useSparkAnalyzer

```typescript
// frontend/app/composables/useSparkAnalyzer.ts

import type { Spark, SparkAnalysisResult } from '~/types/spark'

export const useSparkAnalyzer = () => {
  const config = useRuntimeConfig()
  const { content: articleContent } = useArticle()

  // 状态
  const sparks = useState<Spark[]>('sparks', () => [])
  const isAnalyzing = useState<boolean>('spark-analyzing', () => false)
  const analysisError = useState<string | null>('spark-error', () => null)

  // 分析文章，获取火花位置
  const analyzeArticle = async (text: string) => {
    isAnalyzing.value = true
    analysisError.value = null

    try {
      const response = await $fetch<SparkAnalysisResult>(
        `${config.public.apiBase}/api/v1/sparks/analyze`,
        {
          method: 'POST',
          body: { text, lang: detectLanguage(text) }
        }
      )

      sparks.value = response.sparks
      console.log('✨ 火花分析完成:', response.total_count, '个火花')

      return response
    } catch (error) {
      console.error('火花分析失败:', error)
      analysisError.value = error instanceof Error ? error.message : '分析失败'
      return null
    } finally {
      isAnalyzing.value = false
    }
  }

  // 检测语言
  const detectLanguage = (text: string): 'zh' | 'en' => {
    // 简单的语言检测：检查中文字符比例
    const chineseChars = text.match(/[\u4e00-\u9fa5]/g) || []
    const ratio = chineseChars.length / text.length
    return ratio > 0.3 ? 'zh' : 'en'
  }

  // 渲染火花到 DOM
  const renderSparks = (containerEl: HTMLElement) => {
    if (!containerEl || sparks.value.length === 0) return

    const originalHtml = containerEl.innerHTML
    const textContent = containerEl.textContent || ''

    // 按位置从后往前替换（避免位置偏移）
    const sortedSparks = [...sparks.value].sort((a, b) => b.start - a.start)

    let modifiedHtml = originalHtml

    sortedSparks.forEach(spark => {
      const sparkHtml = createSparkHtml(spark)
      // 替换文本为带火花标记的 HTML
      modifiedHtml = insertSparkAtPosition(
        modifiedHtml,
        spark.start,
        spark.end,
        sparkHtml
      )
    })

    containerEl.innerHTML = modifiedHtml

    // 绑定事件监听器
    attachSparkListeners(containerEl)
  }

  // 创建火花 HTML
  const createSparkHtml = (spark: Spark): string => {
    const sparkClass = `spark spark-${spark.type}`
    const icon = spark.icon || ''

    return `<span
      class="${sparkClass}"
      data-spark-id="${spark.id || generateId()}"
      data-spark-type="${spark.type}"
      data-spark-text="${escapeHtml(spark.text)}"
    >${spark.text}<span class="spark-icon">${icon}</span></span>`
  }

  // 在指定位置插入火花
  const insertSparkAtPosition = (
    html: string,
    start: number,
    end: number,
    sparkHtml: string
  ): string => {
    // 这里需要处理 HTML 标签的影响
    // 简化版实现：假设没有嵌套标签
    const before = html.substring(0, start)
    const after = html.substring(end)
    return before + sparkHtml + after
  }

  // 绑定火花点击事件
  const attachSparkListeners = (containerEl: HTMLElement) => {
    const sparkElements = containerEl.querySelectorAll('.spark')

    sparkElements.forEach(el => {
      // 悬停效果
      el.addEventListener('mouseenter', handleSparkHover)
      el.addEventListener('mouseleave', handleSparkUnhover)

      // 点击效果
      el.addEventListener('click', handleSparkClick)
    })
  }

  // 处理火花悬停
  const handleSparkHover = (event: Event) => {
    const target = event.currentTarget as HTMLElement
    target.classList.add('spark-hover')

    // 显示提示框
    showSparkTooltip(target)
  }

  const handleSparkUnhover = (event: Event) => {
    const target = event.currentTarget as HTMLElement
    target.classList.remove('spark-hover')

    // 隐藏提示框
    hideSparkTooltip()
  }

  // 处理火花点击
  const handleSparkClick = async (event: Event) => {
    const target = event.currentTarget as HTMLElement
    const sparkId = target.dataset.sparkId
    const sparkType = target.dataset.sparkType
    const sparkText = target.dataset.sparkText

    // 添加点击动画
    target.classList.add('spark-clicked')
    setTimeout(() => target.classList.remove('spark-clicked'), 400)

    // 触发洞察生成
    await generateSparkInsight(sparkId!, sparkType!, sparkText!)
  }

  // 清空火花
  const clearSparks = () => {
    sparks.value = []
  }

  return {
    sparks: readonly(sparks),
    isAnalyzing: readonly(isAnalyzing),
    analysisError: readonly(analysisError),
    analyzeArticle,
    renderSparks,
    clearSparks
  }
}
```

### 核心 Composable: useSparkInsight

```typescript
// frontend/app/composables/useSparkInsight.ts

import type { SparkInsight } from '~/types/spark'

export const useSparkInsight = () => {
  const config = useRuntimeConfig()
  const { content: articleContent } = useArticle()

  // 状态
  const currentSparkInsight = useState<string>('spark-insight', () => '')
  const currentSparkReasoning = useState<string>('spark-reasoning', () => '')
  const isGenerating = useState<boolean>('spark-generating', () => false)
  const sparkInsightCache = useState<Map<string, string>>('spark-cache', () => new Map())

  // 生成火花洞察
  const generateSparkInsight = async (
    sparkId: string,
    sparkType: string,
    sparkText: string
  ) => {
    // 检查缓存
    const cacheKey = `${sparkType}:${sparkText}`
    if (sparkInsightCache.value.has(cacheKey)) {
      currentSparkInsight.value = sparkInsightCache.value.get(cacheKey)!
      console.log('🎯 使用缓存的洞察')
      return
    }

    isGenerating.value = true
    currentSparkInsight.value = ''
    currentSparkReasoning.value = ''

    try {
      const { connect } = useSSE()

      const request = {
        spark_type: sparkType,
        spark_text: sparkText,
        context: getContextAroundSpark(sparkText),
        use_reasoning: false // 火花洞察通常不需要推理模式
      }

      await connect('/api/v1/sparks/generate-insight', request, {
        onStart: () => {
          console.log('✨ 开始生成火花洞察')
        },
        onDelta: (content: string) => {
          currentSparkInsight.value += content
        },
        onComplete: (metadata) => {
          // 缓存结果
          sparkInsightCache.value.set(cacheKey, currentSparkInsight.value)
          isGenerating.value = false
          console.log('✅ 火花洞察生成完成')
        },
        onError: (err) => {
          console.error('❌ 火花洞察生成失败:', err)
          isGenerating.value = false
        }
      })
    } catch (error) {
      console.error('火花洞察生成错误:', error)
      isGenerating.value = false
    }
  }

  // 获取火花周围的上下文
  const getContextAroundSpark = (sparkText: string, contextLength: number = 200): string => {
    const fullText = articleContent.value
    const index = fullText.indexOf(sparkText)

    if (index === -1) return sparkText

    const start = Math.max(0, index - contextLength)
    const end = Math.min(fullText.length, index + sparkText.length + contextLength)

    return fullText.substring(start, end)
  }

  return {
    currentSparkInsight: readonly(currentSparkInsight),
    isGenerating: readonly(isGenerating),
    generateSparkInsight
  }
}
```

---

## 后端实现方案

### API 端点设计

#### 1. 分析火花

**Endpoint**: `POST /api/v1/sparks/analyze`

**请求体**:
```json
{
  "text": "完整的文章文本...",
  "lang": "zh"
}
```

**响应**:
```json
{
  "sparks": [
    {
      "id": "spark_1",
      "type": "concept",
      "text": "CAP定理",
      "start": 125,
      "end": 130,
      "icon": "🔍",
      "weight": 0.85
    },
    {
      "id": "spark_2",
      "type": "entity",
      "subtype": "person",
      "text": "埃隆·马斯克",
      "start": 245,
      "end": 251,
      "icon": "👤"
    }
  ],
  "total_count": 15,
  "stats": {
    "entities": 5,
    "concepts": 8,
    "arguments": 2
  },
  "processing_time_ms": 350
}
```

#### 2. 生成火花洞察

**Endpoint**: `POST /api/v1/sparks/generate-insight`

**请求体**:
```json
{
  "spark_type": "concept",
  "spark_text": "CAP定理",
  "context": "...在分布式系统中，CAP定理指出...",
  "use_reasoning": false
}
```

**响应** (SSE 流式):
```
data: {"type": "start"}
data: {"type": "delta", "content": "CAP"}
data: {"type": "delta", "content": "定理"}
...
data: {"type": "complete", "metadata": {...}}
```

---

## 性能优化策略

### 1. 缓存策略

**多层缓存**:
```
L1: 前端内存缓存 (sparkInsightCache)
    ↓ miss
L2: 浏览器 localStorage
    ↓ miss
L3: 后端 Redis 缓存
    ↓ miss
L4: 调用 AI API
```

**缓存键设计**:
```python
cache_key = f"spark:{spark_type}:{hash(spark_text)}:{hash(context[:100])}"
```

**缓存过期时间**:
- 概念火花：7 天（概念解释相对稳定）
- 实体火花：1 天（人物/公司动态变化快）
- 论证火花：3 天

### 2. 批处理优化

**问题**：用户可能快速点击多个火花

**解决**：
```typescript
// 使用防抖，避免过度请求
const debouncedGenerate = useDebounceFn(generateSparkInsight, 300)
```

### 3. DOM 渲染优化

**问题**：大量火花标记可能导致 DOM 过大

**解决**：
- 虚拟滚动（仅渲染可见区域的火花）
- 懒加载（用户滚动到附近才渲染）
- 使用 `requestIdleCallback` 在浏览器空闲时渲染

```typescript
const renderSparksLazily = () => {
  const sparksToRender = sparks.value.slice(0, 30) // 首次只渲染前30个

  requestIdleCallback(() => {
    renderSparks(containerEl, sparksToRender)
  })
}
```

---

## 用户体验细节

### 1. 渐进式启用

**首次使用**:
```
用户粘贴文章
    ↓
显示引导提示："✨ 发现 15 个洞察火花，点击高亮文字探索更多"
    ↓
用户点击第一个火花
    ↓
显示祝贺："🎉 太棒了！你发现了第一个火花"
```

### 2. 设置面板

**用户可以自定义**:
- [ ] 启用/禁用火花功能
- [ ] 选择火花类型（概念/论证/实体）
- [ ] 调整火花灵敏度（少/中/多）
- [ ] 选择视觉样式（虚线/实线/高亮）

### 3. 键盘快捷键

- `Shift + 鼠标悬停` → 直接生成洞察（跳过点击）
- `Esc` → 关闭当前洞察卡片
- `N` → 跳转到下一个火花
- `P` → 跳转到上一个火花

---

## 开发路线图

### MVP 阶段（2周）

**Week 1: 后端基础**
- [ ] 搭建 NLP 分析管道（spaCy + jieba）
- [ ] 实现概念提取（TextRank）
- [ ] 实现实体识别（NER）
- [ ] 创建火花分析 API 端点
- [ ] 集成 Redis 缓存

**Week 2: 前端基础**
- [ ] 创建 `useSparkAnalyzer` composable
- [ ] 实现火花渲染到 DOM
- [ ] 实现火花点击交互
- [ ] 创建火花洞察卡片组件
- [ ] 集成到现有 ArticlePane

### 完善阶段（2周）

**Week 3: 优化与扩展**
- [ ] 添加论证火花识别
- [ ] 优化火花去重算法
- [ ] 实现洞察缓存（三层）
- [ ] 添加火花设置面板
- [ ] A/B 测试不同视觉样式

**Week 4: 用户体验**
- [ ] 添加引导教程
- [ ] 实现键盘快捷键
- [ ] 性能优化（虚拟滚动）
- [ ] 添加用户反馈机制
- [ ] 数据埋点与分析

---

## 成功指标

### 核心指标

1. **火花点击率 (Spark Click Rate)**
   - 目标：> 30%（30% 的火花被点击）
   - 计算：点击的火花数 / 总火花数

2. **火花价值得分 (Spark Value Score)**
   - 目标：> 60
   - 计算：点击率 × 平均停留时间(秒) × (1 - 关闭率)

3. **用户留存影响**
   - 启用火花的用户 vs 未启用用户的留存率对比
   - 目标：+15% 留存率提升

4. **AI 成本控制**
   - 每篇文章的平均 AI 调用次数
   - 目标：< 5 次（大多数用户只探索少数火花）

### 质量指标

1. **火花准确性**
   - 通过用户反馈（👍/👎）评估
   - 目标：> 75% 的火花被认为"有价值"

2. **性能指标**
   - 火花分析时间：< 500ms
   - 页面加载延迟：< 100ms
   - 火花渲染延迟：< 200ms

---

## 风险与缓解

### 风险 1：过度标记导致视觉混乱

**缓解策略**:
- 严格限制火花数量（每篇文章 < 50 个）
- 实现"宁缺毋滥"的过滤逻辑
- 提供火花密度调节选项

### 风险 2：NLP 识别不准确

**缓解策略**:
- 使用用户反馈数据持续优化
- 建立领域专用词典
- 实现人工审核机制（对高频标记）

### 风险 3：AI 成本失控

**缓解策略**:
- 三层缓存机制
- 限制每用户每日洞察生成次数
- 优先使用 gpt-4o-mini

---

## 总结

"洞察火花"功能的核心价值在于：

1. **化被动为主动**：从"用户提问"变成"系统引导"
2. **降低探索成本**：一键获取深度洞察，无需离开阅读流
3. **提升学习效率**：将隐性知识显性化

通过"两阶段分析"架构，我们在**性能**和**价值**之间找到了完美平衡。第一阶段的轻量级扫描保证了速度，第二阶段的按需 AI 生成保证了质量。

这份设计方案不仅是技术实现，更是对"优雅交互"的追求。每一个视觉细节、每一个动画时长、每一个 prompt 模板，都服务于一个目标：**让用户在不知不觉中，爱上深度阅读。**

---

> 🌟 "The best interface is no interface. The second best is one you don't notice."
>
> — 设计哲学
