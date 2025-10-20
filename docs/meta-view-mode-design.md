# 元视角模式 (Meta-View Mode) - 技术设计文档

## 📋 文档信息

| 项目 | 内容 |
|------|------|
| 功能名称 | 元视角模式 (Meta-View Mode) |
| 版本 | v1.0.0 |
| 文档状态 | 设计阶段 |
| 创建日期 | 2025-10-20 |
| 作者 | InsightReader Team |

---

## 🎯 一、项目概述

### 1.1 功能愿景

"元视角"旨在成为 InsightReader 的灵魂，将阅读从线性的、被动的信息接收行为，转变为**立体的、多维度的、主动的探索与审视过程**。我们的目标不是给用户提供答案，而是赋予他们提出更深刻问题的能力。

### 1.2 核心价值主张

#### 用户价值
- **提升批判性思维**: 识别论证结构、情感立场和潜在偏见
- **加速深度理解**: 解构文章元信息（意图、背景、时效）
- **赋能平行思维**: 多维度"思维透镜"，丰富阅读深度和广度

#### 产品价值
- 差异化竞争优势，建立技术壁垒
- 提升用户粘性和留存率
- 收集高质量的用户行为数据

### 1.3 设计哲学

**"按需赋能，优雅无扰" (On-demand Empowerment, Elegant & Unobtrusive)**

- **非侵入性**: 默认不干扰阅读流，需要时才激活
- **渐进式披露**: 信息分层展示，避免认知过载
- **即时反馈**: 所有交互提供清晰的视觉反馈
- **美学一致**: 延续深邃、冥想的设计风格

---

## 🏗️ 二、功能架构

### 2.1 系统架构图

```
┌─────────────────────────────────────────────────────────┐
│                     前端 (Frontend)                      │
├─────────────────────────────────────────────────────────┤
│  阅读页面                                                │
│  ├─ 👓 元视角触发器 (固定在右下角/右上角)                │
│  ├─ 📄 文章内容区 (可缩放宽度)                           │
│  └─ 📊 元信息面板 (滑出式侧边栏)                         │
│      ├─ 元信息卡片 (Meta-Info Cards)                     │
│      │   ├─ 作者意图分析                                 │
│      │   ├─ 时效性评估                                   │
│      │   ├─ 潜在偏见检测                                 │
│      │   └─ 知识缺口提示                                 │
│      └─ 思维透镜切换器 (Lens Switcher)                   │
│          ├─ 论证结构透镜                                 │
│          └─ 作者立场透镜                                 │
├─────────────────────────────────────────────────────────┤
│  状态管理 (Composables)                                  │
│  ├─ useMetaView.ts - 元视角核心逻辑                      │
│  └─ useThinkingLens.ts - 思维透镜管理                    │
└─────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────┐
│                     后端 (Backend)                       │
├─────────────────────────────────────────────────────────┤
│  API 路由                                                │
│  ├─ POST /api/v1/meta-analysis/analyze                  │
│  ├─ GET  /api/v1/meta-analysis/{article_id}             │
│  ├─ POST /api/v1/meta-analysis/feedback                 │
│  └─ POST /api/v1/thinking-lens/apply                    │
├─────────────────────────────────────────────────────────┤
│  服务层                                                  │
│  ├─ meta_analysis_service.py                            │
│  │   ├─ analyze_article_meta_info()                     │
│  │   ├─ detect_author_intent()                          │
│  │   ├─ evaluate_timeliness()                           │
│  │   ├─ detect_bias()                                   │
│  │   └─ identify_knowledge_gaps()                       │
│  └─ thinking_lens_service.py                            │
│      ├─ apply_argument_lens()                           │
│      └─ apply_stance_lens()                             │
├─────────────────────────────────────────────────────────┤
│  LLM 集成 (OpenAI API)                                   │
│  ├─ Prompt 工程 (多轮对话 + CoT)                         │
│  ├─ JSON 模式强制输出                                    │
│  └─ 错误处理和重试机制                                   │
├─────────────────────────────────────────────────────────┤
│  数据库 (Database)                                       │
│  ├─ meta_analyses - 元信息分析表                        │
│  ├─ thinking_lens_results - 透镜分析结果表              │
│  └─ meta_view_feedback - 用户反馈表                     │
└─────────────────────────────────────────────────────────┘
```

### 2.2 核心模块划分

#### 前端模块
1. **MetaViewTrigger** - 触发器组件
2. **MetaInfoPanel** - 元信息面板
3. **MetaInfoCard** - 元信息卡片（可复用）
4. **ThinkingLensSwitcher** - 透镜切换器
5. **ArticleHighlighter** - 文章高亮渲染器

#### 后端模块
1. **MetaAnalysisService** - 元信息分析服务
2. **ThinkingLensService** - 思维透镜服务
3. **LLMPromptEngine** - Prompt 工程引擎
4. **MetaViewFeedbackService** - 用户反馈服务

---

## 💾 三、数据库设计

### 3.1 ER 图

```
┌─────────────────┐
│     users       │
└────────┬────────┘
         │ 1
         │
         │ N
┌────────┴────────────────┐
│   articles              │
│  (现有表,新增字段)      │
│  + has_meta_analysis    │
└────────┬────────────────┘
         │ 1
         │
         │ 1
┌────────┴──────────────────────┐
│   meta_analyses               │
│  - id                         │
│  - article_id (FK)            │
│  - author_intent              │
│  - timeliness_score           │
│  - bias_analysis              │
│  - knowledge_gaps             │
│  - raw_llm_response           │
│  - created_at                 │
│  - updated_at                 │
└────────┬──────────────────────┘
         │ 1
         │
         │ N
┌────────┴──────────────────────┐
│  thinking_lens_results        │
│  - id                         │
│  - meta_analysis_id (FK)      │
│  - lens_type                  │
│  - highlights                 │
│  - annotations                │
│  - created_at                 │
└───────────────────────────────┘

         users
           │ 1
           │
           │ N
┌──────────┴────────────────────┐
│  meta_view_feedback           │
│  - id                         │
│  - user_id (FK)               │
│  - meta_analysis_id (FK)      │
│  - feedback_type              │
│  - rating (1-5)               │
│  - comment                    │
│  - created_at                 │
└───────────────────────────────┘
```

### 3.2 表结构详细设计

#### 3.2.1 meta_analyses (元信息分析表)

```sql
CREATE TABLE meta_analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL UNIQUE,

    -- 作者意图分析
    author_intent JSON NOT NULL,
    -- 结构: {
    --   "primary": "inform|persuade|entertain|provoke",
    --   "confidence": 0.0-1.0,
    --   "description": "详细说明",
    --   "indicators": ["指标1", "指标2"]
    -- }

    -- 时效性评估
    timeliness_score FLOAT NOT NULL,
    -- 0.0-1.0, 1.0表示高度时效敏感
    timeliness_analysis JSON NOT NULL,
    -- 结构: {
    --   "category": "timeless|evergreen|time-sensitive|breaking",
    --   "decay_rate": "low|medium|high",
    --   "best_before": "ISO 8601日期或null",
    --   "context_dependencies": ["依赖1", "依赖2"]
    -- }

    -- 潜在偏见检测
    bias_analysis JSON NOT NULL,
    -- 结构: {
    --   "detected": true|false,
    --   "types": ["confirmation_bias", "political_bias", "cultural_bias"],
    --   "severity": "low|medium|high",
    --   "examples": [
    --     {"text": "原文片段", "type": "偏见类型", "explanation": "说明"}
    --   ],
    --   "overall_balance": "balanced|slightly_biased|heavily_biased"
    -- }

    -- 知识缺口提示
    knowledge_gaps JSON NOT NULL,
    -- 结构: {
    --   "prerequisites": ["前置知识1", "前置知识2"],
    --   "assumptions": ["假设1", "假设2"],
    --   "missing_context": ["缺失的背景1", "缺失的背景2"],
    --   "related_concepts": ["相关概念1", "相关概念2"]
    -- }

    -- 原始LLM响应 (用于调试和改进)
    raw_llm_response TEXT,

    -- 分析质量指标
    analysis_quality JSON,
    -- 结构: {
    --   "confidence_score": 0.0-1.0,
    --   "processing_time_ms": integer,
    --   "llm_model": "模型名称",
    --   "prompt_version": "v1.0"
    -- }

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
    INDEX idx_article_id (article_id)
);
```

#### 3.2.2 thinking_lens_results (思维透镜结果表)

```sql
CREATE TABLE thinking_lens_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    meta_analysis_id INTEGER NOT NULL,
    lens_type VARCHAR(50) NOT NULL,
    -- 'argument_structure' | 'author_stance'

    -- 高亮数据
    highlights JSON NOT NULL,
    -- 结构: [
    --   {
    --     "start": integer,  // 字符偏移量
    --     "end": integer,
    --     "text": "高亮文本",
    --     "category": "claim|evidence|subjective|objective|反讽",
    --     "color": "#hex颜色",
    --     "tooltip": "提示文本"
    --   }
    -- ]

    -- 注释和说明
    annotations JSON,
    -- 结构: {
    --   "summary": "透镜分析总结",
    --   "key_insights": ["洞察1", "洞察2"],
    --   "statistics": {
    --     "claim_count": integer,
    --     "evidence_count": integer,
    --     "claim_to_evidence_ratio": float
    --   }
    -- }

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (meta_analysis_id) REFERENCES meta_analyses(id) ON DELETE CASCADE,
    INDEX idx_meta_analysis (meta_analysis_id),
    INDEX idx_lens_type (lens_type),
    UNIQUE (meta_analysis_id, lens_type)
);
```

#### 3.2.3 meta_view_feedback (用户反馈表)

```sql
CREATE TABLE meta_view_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    meta_analysis_id INTEGER,
    lens_result_id INTEGER,

    feedback_type VARCHAR(50) NOT NULL,
    -- 'meta_info_card' | 'lens_highlight' | 'overall'

    rating INTEGER,
    -- 1-5, 可选

    comment TEXT,
    -- 用户文字反馈，可选

    feedback_data JSON,
    -- 结构化反馈数据，例如:
    -- {"helpful": true, "accurate": false, "specific_issue": "..."}

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (meta_analysis_id) REFERENCES meta_analyses(id) ON DELETE CASCADE,
    FOREIGN KEY (lens_result_id) REFERENCES thinking_lens_results(id) ON DELETE CASCADE,
    INDEX idx_user (user_id),
    INDEX idx_meta_analysis (meta_analysis_id),
    INDEX idx_created_at (created_at)
);
```

---

## 🔌 四、API 设计

### 4.1 元信息分析 API

#### 4.1.1 触发元信息分析

```http
POST /api/v1/meta-analysis/analyze
Content-Type: application/json
Authorization: Bearer {token}

{
  "article_id": 123,
  "full_text": "文章完整文本",
  "language": "zh",
  "force_reanalyze": false  // 是否强制重新分析
}
```

**响应**:
```json
{
  "status": "success|processing|cached",
  "message": "分析完成 | 正在后台分析 | 使用缓存结果",
  "meta_analysis": {
    "id": 456,
    "article_id": 123,
    "author_intent": {
      "primary": "inform",
      "confidence": 0.85,
      "description": "作者旨在客观介绍深度学习的基本原理",
      "indicators": ["使用中性语言", "提供大量技术细节", "避免价值判断"]
    },
    "timeliness_score": 0.4,
    "timeliness_analysis": {
      "category": "evergreen",
      "decay_rate": "low",
      "best_before": null,
      "context_dependencies": []
    },
    "bias_analysis": {
      "detected": false,
      "types": [],
      "severity": "low",
      "examples": [],
      "overall_balance": "balanced"
    },
    "knowledge_gaps": {
      "prerequisites": ["基础数学", "线性代数"],
      "assumptions": ["读者了解编程"],
      "missing_context": [],
      "related_concepts": ["神经网络", "反向传播"]
    },
    "analysis_quality": {
      "confidence_score": 0.88,
      "processing_time_ms": 3500,
      "llm_model": "gpt-4o",
      "prompt_version": "v1.0"
    }
  }
}
```

#### 4.1.2 获取元信息分析结果

```http
GET /api/v1/meta-analysis/{article_id}
Authorization: Bearer {token}
```

**响应**:
```json
{
  "exists": true,
  "meta_analysis": { /* 同上 */ }
}
```

### 4.2 思维透镜 API

#### 4.2.1 应用思维透镜

```http
POST /api/v1/thinking-lens/apply
Content-Type: application/json
Authorization: Bearer {token}

{
  "article_id": 123,
  "lens_type": "argument_structure",  // 'argument_structure' | 'author_stance'
  "full_text": "文章完整文本"
}
```

**响应**:
```json
{
  "status": "success",
  "lens_result": {
    "id": 789,
    "lens_type": "argument_structure",
    "highlights": [
      {
        "start": 50,
        "end": 120,
        "text": "深度学习是机器学习的一个分支",
        "category": "claim",
        "color": "#dbeafe",
        "tooltip": "核心观点：定义深度学习"
      },
      {
        "start": 150,
        "end": 250,
        "text": "研究表明，深度神经网络在图像识别任务上达到了超越人类的准确率",
        "category": "evidence",
        "color": "#d1fae5",
        "tooltip": "证据：引用研究结果"
      }
    ],
    "annotations": {
      "summary": "文章采用\"主张-证据\"结构，逻辑清晰",
      "key_insights": [
        "共识别3个核心主张",
        "每个主张都有相应证据支撑",
        "主张-证据比例: 1:1.5"
      ],
      "statistics": {
        "claim_count": 3,
        "evidence_count": 5,
        "claim_to_evidence_ratio": 1.67
      }
    }
  }
}
```

### 4.3 用户反馈 API

#### 4.3.1 提交反馈

```http
POST /api/v1/meta-analysis/feedback
Content-Type: application/json
Authorization: Bearer {token}

{
  "meta_analysis_id": 456,
  "lens_result_id": 789,  // 可选
  "feedback_type": "lens_highlight",
  "rating": 4,
  "comment": "高亮很准确，但有一处误判",
  "feedback_data": {
    "helpful": true,
    "accurate": true,
    "specific_issue": "第3个高亮应该是evidence而非claim"
  }
}
```

**响应**:
```json
{
  "status": "success",
  "message": "感谢您的反馈！"
}
```

---

## 🎨 五、UI/UX 详细设计

### 5.1 触发器 (Trigger)

#### 视觉设计
```
默认状态:
┌────┐
│ 👓 │  <- 半透明，opacity: 0.4
└────┘

悬停状态:
┌──────────────┐
│ 👓 开启元视角 │  <- 实体，opacity: 1.0，显示文字
└──────────────┘

加载状态:
┌────┐
│ ⟳  │  <- 旋转动画，提示分析中
└────┘

激活状态:
┌────┐
│ ✕  │  <- 变为关闭按钮
└────┘
```

#### 定位和样式
```vue
<template>
  <button
    @click="toggleMetaView"
    :class="[
      'fixed z-50 w-12 h-12 rounded-full shadow-lg transition-all duration-300',
      'bg-gradient-to-br from-violet-500/80 to-purple-600/80 backdrop-blur-md',
      'hover:from-violet-600 hover:to-purple-700 hover:shadow-xl hover:scale-110',
      'bottom-24 right-8',  // 右下角，避开火花分析按钮
      isActive ? 'opacity-100' : 'opacity-40 hover:opacity-100'
    ]"
  >
    <svg v-if="!isLoading && !isActive" class="w-6 h-6 text-white mx-auto">
      <!-- 眼镜图标 -->
    </svg>
    <svg v-else-if="isLoading" class="w-6 h-6 text-white animate-spin mx-auto">
      <!-- 加载图标 -->
    </svg>
    <svg v-else class="w-6 h-6 text-white mx-auto">
      <!-- 关闭图标 -->
    </svg>
  </button>

  <!-- 悬停提示 -->
  <Transition name="fade">
    <div
      v-if="showTooltip"
      class="fixed bottom-24 right-24 px-3 py-1.5 bg-gray-900 text-white text-xs rounded-lg"
    >
      {{ isActive ? '关闭元视角' : '开启元视角' }}
    </div>
  </Transition>
</template>
```

### 5.2 元信息面板 (Meta-Info Panel)

#### 布局结构
```
桌面端:
┌──────────────────────────────────┬──────────────────────┐
│                                  │  元信息面板 (400px)  │
│         文章阅读区               │                      │
│       (宽度动态收缩)             │  ┌────────────────┐  │
│                                  │  │ 元信息卡片 1   │  │
│                                  │  │ (作者意图)     │  │
│                                  │  └────────────────┘  │
│                                  │                      │
│                                  │  ┌────────────────┐  │
│                                  │  │ 元信息卡片 2   │  │
│                                  │  │ (时效性)       │  │
│                                  │  └────────────────┘  │
│                                  │                      │
│                                  │  ┌────────────────┐  │
│                                  │  │ 思维透镜切换   │  │
│                                  │  └────────────────┘  │
└──────────────────────────────────┴──────────────────────┘

移动端:
┌──────────────────────────────────┐
│         文章阅读区               │
│                                  │
│                                  │
│                                  │
└──────────────────────────────────┘
┌──────────────────────────────────┐
│       元信息面板 (底部滑出)      │
│  ┌────────────────────────────┐  │
│  │ 元信息卡片 (可滑动)        │  │
│  └────────────────────────────┘  │
└──────────────────────────────────┘
```

#### 滑出动画
```vue
<Transition
  enter-active-class="transition-all duration-300 ease-out"
  enter-from-class="translate-x-full"
  enter-to-class="translate-x-0"
  leave-active-class="transition-all duration-300 ease-in"
  leave-from-class="translate-x-0"
  leave-to-class="translate-x-full"
>
  <aside
    v-if="isMetaViewActive"
    class="fixed top-0 right-0 h-full w-[400px] bg-white/70 backdrop-blur-xl border-l border-gray-200/50 shadow-2xl overflow-y-auto z-40"
  >
    <!-- 面板内容 -->
  </aside>
</Transition>
```

### 5.3 元信息卡片 (Meta-Info Cards)

#### 卡片组件模板
```vue
<template>
  <div class="mb-4 bg-white/80 backdrop-blur-md border border-gray-200/50 rounded-2xl p-5 shadow-sm hover:shadow-md transition-all">
    <!-- 卡片头部 -->
    <div class="flex items-center justify-between mb-3">
      <div class="flex items-center gap-2">
        <div :class="['w-8 h-8 rounded-lg flex items-center justify-center', iconBgClass]">
          <component :is="icon" class="w-5 h-5 text-white" />
        </div>
        <h4 class="text-sm font-semibold text-gray-800">{{ title }}</h4>
      </div>

      <!-- 置信度指示器 -->
      <div v-if="confidence" class="flex items-center gap-1">
        <div class="w-16 h-1.5 bg-gray-200 rounded-full overflow-hidden">
          <div
            :class="['h-full rounded-full transition-all', confidenceColorClass]"
            :style="{ width: `${confidence * 100}%` }"
          ></div>
        </div>
        <span class="text-xs text-gray-500">{{ Math.round(confidence * 100) }}%</span>
      </div>
    </div>

    <!-- 卡片内容 -->
    <div class="space-y-2">
      <slot />
    </div>

    <!-- 反馈按钮 -->
    <div class="mt-3 flex items-center justify-end gap-2">
      <button
        @click="$emit('feedback', 'helpful')"
        class="p-1.5 rounded-lg hover:bg-gray-100 transition-colors"
        title="有帮助"
      >
        <ThumbsUpIcon class="w-4 h-4 text-gray-400 hover:text-emerald-600" />
      </button>
      <button
        @click="$emit('feedback', 'not-helpful')"
        class="p-1.5 rounded-lg hover:bg-gray-100 transition-colors"
        title="不准确"
      >
        <ThumbsDownIcon class="w-4 h-4 text-gray-400 hover:text-red-600" />
      </button>
    </div>
  </div>
</template>
```

#### 具体卡片示例

**作者意图卡片**:
```vue
<MetaInfoCard
  title="作者意图"
  icon="TargetIcon"
  :confidence="authorIntent.confidence"
  icon-bg-class="bg-gradient-to-br from-violet-500 to-purple-600"
>
  <div class="flex items-center gap-2 mb-2">
    <span class="px-3 py-1 bg-violet-100 text-violet-700 text-xs font-medium rounded-full">
      {{ intentLabel }}
    </span>
  </div>
  <p class="text-sm text-gray-700 leading-relaxed">
    {{ authorIntent.description }}
  </p>
  <div v-if="authorIntent.indicators.length > 0" class="mt-2">
    <p class="text-xs text-gray-500 mb-1">识别依据:</p>
    <ul class="space-y-1">
      <li
        v-for="(indicator, index) in authorIntent.indicators"
        :key="index"
        class="text-xs text-gray-600 flex items-start gap-1"
      >
        <span class="text-violet-500 mt-0.5">•</span>
        <span>{{ indicator }}</span>
      </li>
    </ul>
  </div>
</MetaInfoCard>
```

**时效性评估卡片**:
```vue
<MetaInfoCard
  title="时效性评估"
  icon="ClockIcon"
  :confidence="timelinessScore"
  icon-bg-class="bg-gradient-to-br from-amber-500 to-orange-600"
>
  <div class="flex items-center gap-2 mb-2">
    <span :class="[
      'px-3 py-1 text-xs font-medium rounded-full',
      categoryColorClass
    ]">
      {{ categoryLabel }}
    </span>
  </div>

  <!-- 时效性条形图 -->
  <div class="relative h-2 bg-gray-200 rounded-full overflow-hidden mb-3">
    <div
      :class="['h-full rounded-full transition-all', scoreColorClass]"
      :style="{ width: `${timelinessScore * 100}%` }"
    ></div>
  </div>

  <div class="space-y-2 text-sm">
    <div class="flex items-center justify-between">
      <span class="text-gray-600">衰减速度:</span>
      <span class="font-medium text-gray-800">{{ decayRateLabel }}</span>
    </div>
    <div v-if="bestBefore" class="flex items-center justify-between">
      <span class="text-gray-600">有效期至:</span>
      <span class="font-medium text-gray-800">{{ formatDate(bestBefore) }}</span>
    </div>
  </div>

  <div v-if="contextDependencies.length > 0" class="mt-3 p-3 bg-amber-50/50 rounded-lg">
    <p class="text-xs text-amber-800 font-medium mb-1">时效性依赖:</p>
    <ul class="space-y-1">
      <li
        v-for="dep in contextDependencies"
        :key="dep"
        class="text-xs text-amber-700"
      >
        • {{ dep }}
      </li>
    </ul>
  </div>
</MetaInfoCard>
```

### 5.4 思维透镜切换器 (Thinking Lens Switcher)

```vue
<template>
  <div class="mt-6 bg-gradient-to-br from-slate-50/50 to-zinc-50/50 border border-gray-200/50 rounded-2xl p-5">
    <h4 class="text-sm font-semibold text-gray-800 mb-4 flex items-center gap-2">
      <EyeIcon class="w-5 h-5 text-violet-600" />
      思维透镜
    </h4>

    <div class="space-y-2">
      <!-- 论证结构透镜 -->
      <button
        @click="toggleLens('argument_structure')"
        :class="[
          'w-full p-3 rounded-xl border-2 transition-all text-left',
          activeLens === 'argument_structure'
            ? 'border-blue-500 bg-blue-50/50 shadow-sm'
            : 'border-gray-200 hover:border-blue-300 hover:bg-blue-50/30'
        ]"
      >
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm font-medium text-gray-800">论证结构</span>
          <div v-if="activeLens === 'argument_structure'" class="flex items-center gap-1 text-xs text-blue-600">
            <CheckCircleIcon class="w-4 h-4" />
            <span>已激活</span>
          </div>
        </div>
        <p class="text-xs text-gray-600 mb-2">
          识别文章的核心主张与支撑证据
        </p>

        <!-- 图例 -->
        <div v-if="activeLens === 'argument_structure'" class="flex items-center gap-3 text-xs">
          <div class="flex items-center gap-1">
            <div class="w-3 h-3 rounded bg-blue-200"></div>
            <span class="text-gray-600">主张</span>
          </div>
          <div class="flex items-center gap-1">
            <div class="w-3 h-3 rounded bg-green-200"></div>
            <span class="text-gray-600">证据</span>
          </div>
        </div>
      </button>

      <!-- 作者立场透镜 -->
      <button
        @click="toggleLens('author_stance')"
        :class="[
          'w-full p-3 rounded-xl border-2 transition-all text-left',
          activeLens === 'author_stance'
            ? 'border-yellow-500 bg-yellow-50/50 shadow-sm'
            : 'border-gray-200 hover:border-yellow-300 hover:bg-yellow-50/30'
        ]"
      >
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm font-medium text-gray-800">作者立场</span>
          <div v-if="activeLens === 'author_stance'" class="flex items-center gap-1 text-xs text-yellow-600">
            <CheckCircleIcon class="w-4 h-4" />
            <span>已激活</span>
          </div>
        </div>
        <p class="text-xs text-gray-600 mb-2">
          区分事实陈述与主观观点
        </p>

        <!-- 图例 -->
        <div v-if="activeLens === 'author_stance'" class="flex items-center gap-3 text-xs">
          <div class="flex items-center gap-1">
            <div class="w-3 h-3 rounded bg-yellow-200"></div>
            <span class="text-gray-600">主观</span>
          </div>
          <div class="flex items-center gap-1">
            <div class="w-3 h-3 rounded bg-gray-200"></div>
            <span class="text-gray-600">客观</span>
          </div>
        </div>
      </button>
    </div>

    <!-- 统计信息 -->
    <div v-if="activeLens && lensStats" class="mt-4 p-3 bg-white/60 rounded-lg border border-gray-200/50">
      <p class="text-xs text-gray-600 mb-2">统计信息:</p>
      <div class="grid grid-cols-2 gap-2 text-xs">
        <div v-for="(value, key) in lensStats" :key="key">
          <span class="text-gray-500">{{ key }}:</span>
          <span class="ml-1 font-medium text-gray-800">{{ value }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
```

### 5.5 文章高亮渲染

#### 高亮颜色系统
```typescript
const HIGHLIGHT_COLORS = {
  // 论证结构透镜
  argument_structure: {
    claim: {
      bg: 'rgba(191, 219, 254, 0.4)',      // 淡蓝色 (blue-200/40)
      border: 'rgba(59, 130, 246, 0.3)',   // 蓝色边框
      tooltip: '核心主张'
    },
    evidence: {
      bg: 'rgba(209, 250, 229, 0.4)',      // 淡绿色 (green-200/40)
      border: 'rgba(34, 197, 94, 0.3)',    // 绿色边框
      tooltip: '支撑证据'
    }
  },

  // 作者立场透镜
  author_stance: {
    subjective: {
      bg: 'rgba(254, 240, 138, 0.4)',      // 淡黄色 (yellow-200/40)
      border: 'rgba(234, 179, 8, 0.3)',    // 黄色边框
      tooltip: '主观表达'
    },
    objective: {
      bg: 'rgba(226, 232, 240, 0.4)',      // 淡灰色 (slate-200/40)
      border: 'rgba(100, 116, 139, 0.3)',  // 灰色边框
      tooltip: '客观陈述'
    },
    irony: {
      bg: 'rgba(253, 224, 71, 0.4)',       // 淡黄色 (yellow-300/40)
      border: 'rgba(234, 179, 8, 0.4)',    // 黄色边框
      tooltip: '反讽/讽刺'
    }
  }
}
```

#### 高亮实现逻辑
```typescript
// composables/useThinkingLens.ts
export const useThinkingLens = () => {
  const applyHighlights = (containerEl: HTMLElement, highlights: Highlight[]) => {
    // 清除旧高亮
    removeOldHighlights(containerEl)

    // 按位置从后往前排序（避免位置偏移）
    const sortedHighlights = [...highlights].sort((a, b) => b.start - a.start)

    // 收集文本节点
    const textNodes = collectTextNodes(containerEl)

    // 应用高亮
    for (const highlight of sortedHighlights) {
      const targetNode = findNodeByOffset(textNodes, highlight.start)
      if (!targetNode) continue

      // 创建高亮元素
      const highlightEl = createHighlightElement(highlight)

      // 插入DOM
      insertHighlight(targetNode, highlight, highlightEl)
    }
  }

  const createHighlightElement = (highlight: Highlight): HTMLElement => {
    const span = document.createElement('span')
    span.className = 'meta-view-highlight'
    span.dataset.category = highlight.category
    span.dataset.lensType = highlight.lensType

    const colorScheme = HIGHLIGHT_COLORS[highlight.lensType][highlight.category]
    span.style.backgroundColor = colorScheme.bg
    span.style.borderBottom = `2px solid ${colorScheme.border}`
    span.style.cursor = 'pointer'
    span.textContent = highlight.text

    // 添加 tooltip
    span.title = highlight.tooltip || colorScheme.tooltip

    // 悬停效果
    span.addEventListener('mouseenter', () => {
      span.style.backgroundColor = colorScheme.bg.replace('0.4', '0.6')
    })
    span.addEventListener('mouseleave', () => {
      span.style.backgroundColor = colorScheme.bg
    })

    return span
  }

  return {
    applyHighlights,
    removeHighlights: () => removeOldHighlights(containerEl)
  }
}
```

---

## 🤖 六、LLM Prompt 工程

### 6.1 Prompt 设计原则

1. **结构化输出强制**: 使用 OpenAI 的 JSON mode 或 Function Calling
2. **思维链引导**: 先分析，再归纳，最后输出
3. **Few-shot 示例**: 提供2-3个高质量示例
4. **明确约束**: 清晰定义每个字段的取值范围和格式
5. **防御性设计**: 处理边缘情况和模糊文本

### 6.2 元信息分析 Prompt

```python
META_ANALYSIS_SYSTEM_PROMPT = """
你是一位专业的文本分析专家，擅长识别文章的元信息（作者意图、时效性、潜在偏见等）。

你的任务是深入分析用户提供的文章，并以JSON格式输出结构化的元信息分析结果。

# 分析维度

1. **作者意图 (Author Intent)**
   - 主要意图类型：inform (告知), persuade (说服), entertain (娱乐), provoke (激发思考)
   - 置信度：0.0-1.0
   - 详细说明：100字以内
   - 识别依据：列出3-5个关键指标

2. **时效性 (Timeliness)**
   - 时效性分数：0.0-1.0 (0表示永恒内容，1表示高度时效敏感)
   - 类别：timeless (永恒), evergreen (常青), time-sensitive (时效敏感), breaking (突发新闻)
   - 衰减速度：low (慢), medium (中等), high (快)
   - 有效期：ISO 8601日期或null
   - 时效依赖：列出影响时效性的关键因素

3. **潜在偏见 (Bias)**
   - 是否检测到偏见：true/false
   - 偏见类型：confirmation_bias, political_bias, cultural_bias, selection_bias等
   - 严重程度：low, medium, high
   - 具体案例：每个案例包含原文片段、偏见类型和说明
   - 整体平衡性：balanced, slightly_biased, heavily_biased

4. **知识缺口 (Knowledge Gaps)**
   - 前置知识：列出阅读本文需要的背景知识
   - 隐含假设：列出作者未明说的假设
   - 缺失背景：指出文中未提及但重要的上下文
   - 相关概念：列出可扩展阅读的相关主题

# 输出格式

必须严格按照以下JSON schema输出：

{
  "author_intent": {
    "primary": "inform|persuade|entertain|provoke",
    "confidence": 0.0-1.0,
    "description": "string",
    "indicators": ["string"]
  },
  "timeliness": {
    "score": 0.0-1.0,
    "category": "timeless|evergreen|time-sensitive|breaking",
    "decay_rate": "low|medium|high",
    "best_before": "ISO 8601 date or null",
    "context_dependencies": ["string"]
  },
  "bias": {
    "detected": true|false,
    "types": ["string"],
    "severity": "low|medium|high",
    "examples": [
      {
        "text": "string",
        "type": "string",
        "explanation": "string"
      }
    ],
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

- 分析要客观、中立，避免主观判断
- 对于不确定的分析，降低置信度
- 偏见检测要谨慎，避免误报
- 所有列表字段至少包含1个元素，最多5个
"""

META_ANALYSIS_USER_PROMPT_TEMPLATE = """
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
```

### 6.3 论证结构透镜 Prompt

```python
ARGUMENT_LENS_SYSTEM_PROMPT = """
你是一位逻辑分析专家，擅长识别文本中的论证结构。

你的任务是分析文章，标注出：
1. **核心主张 (Claims)**: 作者想要证明或传达的核心观点
2. **支撑证据 (Evidence)**: 用于支持主张的数据、事实、例子、引用等

# 标注规则

- 每个标注必须包含：起始位置、结束位置、文本片段、类别、提示信息
- 位置是字符级偏移量（从0开始）
- 主张和证据要形成逻辑对应关系
- 避免标注过短（<10字符）或过长（>200字符）的片段

# 输出格式

{
  "highlights": [
    {
      "start": integer,
      "end": integer,
      "text": "string",
      "category": "claim|evidence",
      "tooltip": "string"
    }
  ],
  "annotations": {
    "summary": "string",
    "key_insights": ["string"],
    "statistics": {
      "claim_count": integer,
      "evidence_count": integer,
      "claim_to_evidence_ratio": float
    }
  }
}
"""

ARGUMENT_LENS_USER_PROMPT_TEMPLATE = """
请分析以下文章的论证结构，标注出核心主张和支撑证据：

{content}

请输出JSON格式的分析结果。
"""
```

### 6.4 作者立场透镜 Prompt

```python
STANCE_LENS_SYSTEM_PROMPT = """
你是一位语言学专家，擅长区分文本中的主观表达和客观陈述。

你的任务是分析文章，标注出：
1. **主观表达 (Subjective)**: 包含个人观点、价值判断、情感色彩的句子
2. **客观陈述 (Objective)**: 中性描述事实的句子
3. **反讽/讽刺 (Irony)**: 表面意思与实际意图相反的表达

# 标注规则

- 主观表达的标志：情感词汇、价值判断、模糊限定词（"我认为"、"可能"、"应该"）
- 客观陈述的标志：具体数据、明确事实、中性动词
- 反讽较难识别，需结合语境，不确定时不标注
- 每个句子只标注一次，选择最主要的类别

# 输出格式

{
  "highlights": [
    {
      "start": integer,
      "end": integer,
      "text": "string",
      "category": "subjective|objective|irony",
      "tooltip": "string"
    }
  ],
  "annotations": {
    "summary": "string",
    "key_insights": ["string"],
    "statistics": {
      "subjective_count": integer,
      "objective_count": integer,
      "subjectivity_ratio": float
    }
  }
}
"""
```

### 6.5 Prompt 调用流程

```python
# services/meta_analysis_service.py

from openai import OpenAI
import json

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
        language: str = "zh"
    ) -> dict:
        """元信息分析"""

        # 构建用户提示
        user_prompt = META_ANALYSIS_USER_PROMPT_TEMPLATE.format(
            title=title,
            author=author,
            publish_date=publish_date,
            language=language,
            content=content[:5000]  # 限制长度，避免超出token限制
        )

        try:
            # 调用 OpenAI API (使用 JSON mode)
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": META_ANALYSIS_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},  # 强制JSON输出
                temperature=0.3,  # 降低随机性，提高稳定性
                max_tokens=2000
            )

            # 解析响应
            result = json.loads(response.choices[0].message.content)

            # 验证结构
            self._validate_meta_analysis_result(result)

            # 保存到数据库
            meta_analysis = MetaAnalysis(
                article_id=article_id,
                author_intent=result['author_intent'],
                timeliness_score=result['timeliness']['score'],
                timeliness_analysis=result['timeliness'],
                bias_analysis=result['bias'],
                knowledge_gaps=result['knowledge_gaps'],
                raw_llm_response=response.choices[0].message.content,
                analysis_quality={
                    "confidence_score": result['author_intent']['confidence'],
                    "processing_time_ms": int(response.usage.total_tokens * 10),  # 估算
                    "llm_model": "gpt-4o",
                    "prompt_version": "v1.0"
                }
            )

            self.db.add(meta_analysis)
            self.db.commit()
            self.db.refresh(meta_analysis)

            return self._format_meta_analysis_response(meta_analysis)

        except Exception as e:
            logger.error(f"元信息分析失败: {str(e)}")
            raise HTTPException(status_code=500, detail="元信息分析失败")

    def _validate_meta_analysis_result(self, result: dict):
        """验证LLM输出结构"""
        required_keys = ['author_intent', 'timeliness', 'bias', 'knowledge_gaps']
        for key in required_keys:
            if key not in result:
                raise ValueError(f"缺少必需字段: {key}")

        # 验证作者意图
        if result['author_intent']['primary'] not in ['inform', 'persuade', 'entertain', 'provoke']:
            raise ValueError("无效的作者意图类型")

        # 验证置信度范围
        if not 0 <= result['author_intent']['confidence'] <= 1:
            raise ValueError("置信度必须在0-1之间")

        # ... 更多验证 ...
```

---

## 🚀 七、实施路线图

### 7.1 阶段划分

#### **Phase 1: MVP (最小可行产品) - 2周**

**目标**: 验证核心功能和用户价值

**范围**:
- ✅ 元视角触发器
- ✅ 元信息面板滑出动画
- ✅ 2个元信息卡片（作者意图 + 时效性）
- ✅ 1个思维透镜（论证结构）
- ✅ 基础高亮渲染
- ✅ 元信息分析API
- ✅ 数据库基础表结构

**不包含**:
- ❌ 潜在偏见检测
- ❌ 知识缺口提示
- ❌ 作者立场透镜
- ❌ 用户反馈机制
- ❌ 性能优化

**交付物**:
- 可工作的原型
- 技术设计文档
- API 文档
- 初步测试数据

---

#### **Phase 2: 功能完善 - 2周**

**目标**: 补全所有设计功能

**范围**:
- ✅ 潜在偏见检测卡片
- ✅ 知识缺口提示卡片
- ✅ 作者立场透镜
- ✅ 用户反馈按钮和API
- ✅ 透镜切换动画优化
- ✅ 移动端适配

**交付物**:
- 功能完整的产品
- 用户使用指南
- 完整的测试用例

---

#### **Phase 3: 优化与迭代 - 1周**

**目标**: 提升性能、稳定性和用户体验

**范围**:
- ✅ Prompt 调优（基于真实数据）
- ✅ 性能优化（缓存、异步处理）
- ✅ 错误处理完善
- ✅ A/B 测试准备
- ✅ 数据分析埋点

**交付物**:
- 生产就绪的代码
- 性能测试报告
- 运营数据看板

---

### 7.2 技术风险与应对

| 风险 | 影响 | 概率 | 应对策略 |
|------|------|------|---------|
| LLM 输出不稳定 | 高 | 中 | 1. 使用 JSON mode 强制结构化输出<br>2. 多轮验证和重试机制<br>3. 降级策略：部分功能失败不影响整体 |
| 分析耗时长 | 中 | 高 | 1. 异步处理，前端显示加载状态<br>2. 结果缓存，避免重复分析<br>3. 分段分析（先快速分析，再深度分析） |
| 成本过高 | 中 | 中 | 1. 只对保存/收藏的文章进行分析<br>2. 限制分析频次（每用户每天上限）<br>3. 使用更便宜的模型（gpt-3.5-turbo）降级 |
| 高亮位置偏移 | 低 | 低 | 1. 使用健壮的文本节点遍历算法<br>2. 充分测试各种HTML结构<br>3. 边界情况处理（跨标签高亮） |
| 用户体验复杂 | 中 | 中 | 1. 渐进式披露，避免信息过载<br>2. 清晰的视觉层次<br>3. 用户引导和教程 |

---

## 📊 八、数据分析与指标

### 8.1 核心指标 (KPIs)

**使用率指标**:
- 元视角激活率: 阅读文章的用户中，点击👓图标的比例
- 透镜使用率: 激活元视角后，切换透镜的比例
- 平均使用时长: 元视角面板打开的平均时长

**价值指标**:
- 用户反馈评分: 👍/👎 比例
- 功能留存率: 首次使用后，7天内再次使用的比例
- 深度阅读转化: 使用元视角后，进行火花点击/收藏的比例提升

**性能指标**:
- 分析平均耗时: P50, P95, P99
- API 成功率: 分析请求的成功率
- 高亮渲染性能: 大文章（>5000字）的渲染帧率

### 8.2 埋点方案

```typescript
// 元视角激活
trackEvent('meta_view_activated', {
  article_id: number,
  trigger_source: 'button' | 'keyboard_shortcut',
  user_id: number,
  timestamp: Date
})

// 透镜切换
trackEvent('thinking_lens_toggled', {
  article_id: number,
  lens_type: 'argument_structure' | 'author_stance',
  action: 'enabled' | 'disabled',
  user_id: number,
  timestamp: Date
})

// 用户反馈
trackEvent('meta_view_feedback_submitted', {
  article_id: number,
  feedback_type: 'meta_info_card' | 'lens_highlight',
  component: 'author_intent' | 'timeliness' | '...',
  rating: 1-5 | null,
  helpful: boolean,
  user_id: number,
  timestamp: Date
})

// 分析性能
trackEvent('meta_analysis_completed', {
  article_id: number,
  processing_time_ms: number,
  llm_model: string,
  success: boolean,
  error_type: string | null,
  timestamp: Date
})
```

---

## 🎓 九、最佳实践与规范

### 9.1 前端开发规范

**组件拆分原则**:
- 单一职责：每个组件只负责一个功能模块
- 可复用：MetaInfoCard 设计为通用卡片组件
- 状态隔离：使用 composables 管理复杂状态

**性能优化**:
```typescript
// 使用 computed 缓存计算结果
const intentLabel = computed(() => {
  const labels = {
    inform: '告知',
    persuade: '说服',
    entertain: '娱乐',
    provoke: '激发思考'
  }
  return labels[authorIntent.value.primary]
})

// 使用 debounce 避免频繁API调用
const debouncedAnalyze = debounce(async () => {
  await analyzeArticle(articleId.value)
}, 500)

// 虚拟滚动（如果元信息卡片很多）
import { useVirtualList } from '@vueuse/core'
const { list, containerProps, wrapperProps } = useVirtualList(metaCards, {
  itemHeight: 200
})
```

**错误处理**:
```typescript
try {
  await analyzeArticle(articleId.value)
} catch (error) {
  if (error.response?.status === 429) {
    // 限流错误
    showNotification('分析请求过于频繁，请稍后再试', 'warning')
  } else if (error.response?.status === 500) {
    // 服务器错误
    showNotification('分析失败，请稍后重试', 'error')
  } else {
    // 其他错误
    showNotification('未知错误', 'error')
  }

  // 记录错误日志
  logError('meta_view_error', {
    article_id: articleId.value,
    error: error.message,
    stack: error.stack
  })
}
```

### 9.2 后端开发规范

**Prompt 版本管理**:
```python
# 使用版本号管理 Prompt
PROMPT_VERSIONS = {
    "v1.0": {
        "meta_analysis": META_ANALYSIS_SYSTEM_PROMPT_V1,
        "argument_lens": ARGUMENT_LENS_SYSTEM_PROMPT_V1
    },
    "v1.1": {
        "meta_analysis": META_ANALYSIS_SYSTEM_PROMPT_V1_1,
        "argument_lens": ARGUMENT_LENS_SYSTEM_PROMPT_V1_1
    }
}

def get_prompt(prompt_type: str, version: str = "latest"):
    if version == "latest":
        version = max(PROMPT_VERSIONS.keys())
    return PROMPT_VERSIONS[version][prompt_type]
```

**重试机制**:
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
async def call_openai_api(messages: list) -> dict:
    response = await self.client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        response_format={"type": "json_object"},
        temperature=0.3
    )
    return json.loads(response.choices[0].message.content)
```

**成本控制**:
```python
# 限流装饰器
from functools import wraps
from datetime import datetime, timedelta

def rate_limit(max_calls: int, period: timedelta):
    """限制API调用频率"""
    def decorator(func):
        calls = {}

        @wraps(func)
        async def wrapper(user_id: int, *args, **kwargs):
            now = datetime.utcnow()

            # 清理过期记录
            calls[user_id] = [
                call_time for call_time in calls.get(user_id, [])
                if now - call_time < period
            ]

            # 检查是否超限
            if len(calls.get(user_id, [])) >= max_calls:
                raise HTTPException(
                    status_code=429,
                    detail=f"每{period.total_seconds()}秒最多调用{max_calls}次"
                )

            # 记录本次调用
            calls.setdefault(user_id, []).append(now)

            return await func(user_id, *args, **kwargs)

        return wrapper
    return decorator

@rate_limit(max_calls=10, period=timedelta(hours=1))
async def analyze_article(user_id: int, article_id: int):
    # ... 分析逻辑 ...
```

---

## 📝 十、文档与培训

### 10.1 需要产出的文档

1. **技术设计文档** (本文档)
2. **API 参考文档**
3. **前端组件使用指南**
4. **Prompt 工程手册**
5. **用户使用指南**
6. **运维手册**

### 10.2 团队培训计划

**开发团队**:
- Prompt 工程培训（2小时）
- LLM API 最佳实践（1小时）
- 前端复杂状态管理（1.5小时）

**产品/设计团队**:
- 元视角功能演示（30分钟）
- 用户价值讲解（30分钟）
- 数据指标解读（30分钟）

---

## ✅ 十一、验收标准

### 11.1 功能验收

- [ ] 用户可以点击👓图标激活元视角
- [ ] 元信息面板平滑滑出，文章区域宽度相应缩小
- [ ] 显示作者意图、时效性、潜在偏见、知识缺口四张卡片
- [ ] 用户可以切换论证结构和作者立场两个透镜
- [ ] 激活透镜后，文章中相应内容被正确高亮
- [ ] 高亮颜色符合设计规范，悬停有视觉反馈
- [ ] 用户可以提交反馈（👍/👎）
- [ ] 移动端和桌面端均正常显示

### 11.2 性能验收

- [ ] 元信息分析平均耗时 < 5秒（P95）
- [ ] 高亮渲染不卡顿（>30 FPS）
- [ ] API 成功率 > 95%
- [ ] 前端bundle大小增加 < 50KB

### 11.3 质量验收

- [ ] 单元测试覆盖率 > 70%
- [ ] 集成测试通过
- [ ] 无严重bug（P0/P1）
- [ ] 代码review通过
- [ ] 文档完整

---

## 📊 附录

### 附录A: 技术栈清单

**前端**:
- Vue 3 + Composition API
- TypeScript
- Nuxt 3
- Tailwind CSS
- @vueuse/core (工具库)
- lucide-vue-next (图标)

**后端**:
- Python 3.12+
- FastAPI
- SQLAlchemy
- OpenAI Python SDK
- Pydantic (数据验证)
- Tenacity (重试机制)

**数据库**:
- SQLite (开发环境)
- PostgreSQL (生产环境推荐)

**基础设施**:
- Docker (容器化)
- Redis (缓存 - 可选)
- Sentry (错误监控 - 可选)

### 附录B: 参考资料

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)
- [Vue 3 Composition API](https://vuejs.org/guide/extras/composition-api-faq.html)
- [Tailwind CSS](https://tailwindcss.com/docs)

---

**文档版本**: 1.0.0
**最后更新**: 2025-10-20
**维护者**: InsightReader Team
**审核状态**: ✅ 已审核

---

## 变更日志

### v1.0.0 - 2025-10-20
- 初始版本
- 完成完整的技术设计
- 包含数据库设计、API设计、UI/UX设计
- 包含LLM Prompt工程方案
- 包含实施路线图和风险评估
