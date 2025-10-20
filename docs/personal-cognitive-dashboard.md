# 个人认知仪表盘 - 技术设计文档

## 1. 项目概述

### 1.1 核心理念

**个人认知仪表盘**是 InsightReader 的核心功能升级，旨在将碎片化的阅读洞察转化为**可视化的个人知识资产**。

**核心价值主张**：
- 📊 **知识可视化**：将抽象的"我学到了什么"具象化为知识图谱
- 🔍 **自我认知**：通过数据发现自己的思维模式和知识盲区
- 🎯 **成长追踪**：量化阅读成长，提供持续的正向反馈

**设计哲学**：
> "洞察不应该是昙花一现的灵光乍现，而应该沉淀为可追溯、可复盘的知识资产。"

---

## 2. 功能架构设计

```
个人认知仪表盘
├── 🧠 知识图谱 (Knowledge Graph)
│   ├── 概念节点可视化
│   ├── 概念关系网络
│   ├── 交互式探索
│   └── 增长动画
│
├── 🎨 好奇心指纹 (Curiosity Fingerprint)
│   ├── 火花类型分布（雷达图）
│   ├── 阅读时序分析（折线图）
│   ├── 话题云图
│   └── 兴趣趋势预测
│
└── 🔦 思维盲区探测 (Blind Spot Detection - V2)
    ├── 未探索领域推荐
    ├── 知识孤岛识别
    └── 跨域阅读建议
```

---

## 3. 核心模块详细设计

### 3.1 知识图谱 (Knowledge Graph)

#### 3.1.1 数据模型

**节点类型**：
```typescript
interface KnowledgeNode {
  id: string                    // 唯一标识
  label: string                 // 显示文本（概念名称）
  type: 'concept' | 'entity'    // 节点类型
  size: number                  // 节点大小（基于关联洞察数量）
  color: string                 // 节点颜色（基于领域分类）
  metadata: {
    insightId: string           // 关联的洞察 ID
    createdAt: Date             // 创建时间
    reviewCount: number         // 被回顾次数
    domain: string              // 所属领域（AI、经济、哲学等）
  }
}
```

**边类型**：
```typescript
interface KnowledgeEdge {
  id: string
  source: string                // 源节点 ID
  target: string                // 目标节点 ID
  type: 'related' | 'contrast' | 'depends_on'  // 关系类型
  weight: number                // 关系强度（0-1）
  label?: string                // 关系描述（可选）
}
```

#### 3.1.2 图谱生成逻辑

**阶段 1：概念提取**
- 从历史洞察中提取所有高频概念
- 使用 TF-IDF 识别关键概念
- 过滤低质量概念（停用词、单字等）

**阶段 2：关系推断**
- **共现关系**：同一洞察中出现的概念建立连接
- **依赖关系**：使用 LLM 分析概念间的逻辑依赖
  ```python
  # 示例 Prompt
  """
  分析以下两个概念的关系：
  概念A: {concept_a}
  概念B: {concept_b}

  上下文：
  {insight_content}

  返回关系类型：
  - related: 相关
  - contrast: 对比
  - depends_on: A 依赖于 B
  - none: 无关系
  """
  ```

**阶段 3：图谱优化**
- 使用力导向布局算法（D3.js Force Simulation）
- 社区检测算法识别知识簇（Louvain Algorithm）
- 渐进式渲染（大图谱分批加载）

#### 3.1.3 可视化技术栈

**前端库选择**：
- **D3.js**：力导向布局 + 自定义交互
- 或 **Cytoscape.js**：开箱即用的图谱库（更易上手）

**交互设计**：
- 缩放/平移：探索大图谱
- 节点点击：查看关联洞察
- 拖拽节点：重新布局
- 悬停提示：显示节点元数据

**动画效果**：
```typescript
// 新节点出现动画
function addNodeWithAnimation(node: KnowledgeNode) {
  // 从中心放射出现
  node.x = centerX
  node.y = centerY
  node.scale = 0

  gsap.to(node, {
    scale: 1,
    duration: 0.6,
    ease: 'elastic.out(1, 0.5)'
  })
}
```

#### 3.1.4 后端 API 设计

```typescript
// GET /api/v1/dashboard/knowledge-graph
interface KnowledgeGraphResponse {
  nodes: KnowledgeNode[]
  edges: KnowledgeEdge[]
  stats: {
    totalNodes: number
    totalEdges: number
    domains: Record<string, number>
    latestUpdate: Date
  }
}

// POST /api/v1/dashboard/knowledge-graph/rebuild
// 异步任务：重新构建用户的知识图谱
interface RebuildRequest {
  userId: number
  useCache?: boolean
}
```

---

### 3.2 好奇心指纹 (Curiosity Fingerprint)

#### 3.2.1 核心指标

**1. 火花类型分布（雷达图）**
```typescript
interface SparkDistribution {
  concept: number      // 概念类火花点击次数
  argument: number     // 论证类火花点击次数
  entity: number       // 实体类火花点击次数（已移除，保留字段兼容性）
}
```

**2. 阅读时序分析（折线图）**
```typescript
interface ReadingTimeSeries {
  date: Date
  sparkCounts: {
    concept: number
    argument: number
  }
  insightCounts: number
}
```

**3. 话题云图**
```typescript
interface TopicCloud {
  topics: Array<{
    topic: string        // 话题名称（如"人工智能"）
    count: number        // 相关火花数量
    weight: number       // 归一化权重（0-1）
  }>
}
```

#### 3.2.2 可视化组件

**雷达图（Radar Chart）**
```vue
<template>
  <div class="curiosity-fingerprint">
    <h3>好奇心指纹</h3>
    <RadarChart :data="sparkDistribution" />

    <div class="insights">
      <p v-if="dominantType === 'concept'">
        💡 你是<strong>概念探索者</strong>：喜欢深挖专业术语和理论框架
      </p>
      <p v-else-if="dominantType === 'argument'">
        🔍 你是<strong>逻辑思考者</strong>：关注论证过程和数据证据
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
const { sparkDistribution } = useDashboard()

const dominantType = computed(() => {
  const { concept, argument } = sparkDistribution.value
  return concept > argument ? 'concept' : 'argument'
})
</script>
```

**时序图（Line Chart）**
- 使用 **Recharts** 或 **Chart.js**
- 显示最近 30 天的阅读活跃度
- 高亮最活跃的日期

**话题云（Tag Cloud）**
- 使用 **react-tagcloud** 或自定义 SVG
- 字体大小 ∝ 话题权重
- 颜色编码领域分类

#### 3.2.3 数据采集

**前端埋点**：
```typescript
// 在 useSparkAnalyzer.ts 中
const handleSparkClick = async (spark: Spark) => {
  // 记录火花点击
  await $fetch('/api/v1/analytics/spark-click', {
    method: 'POST',
    body: {
      userId: user.id,
      sparkType: spark.type,
      sparkText: spark.text,
      articleId: article.id,
      timestamp: new Date()
    }
  })
}
```

**后端聚合**：
```python
# app/services/analytics_service.py
class AnalyticsService:
    def get_curiosity_fingerprint(self, user_id: int) -> dict:
        # 查询最近 30 天的火花点击
        clicks = db.query(SparkClick).filter(
            SparkClick.user_id == user_id,
            SparkClick.created_at >= datetime.now() - timedelta(days=30)
        ).all()

        # 统计分布
        distribution = {
            'concept': sum(1 for c in clicks if c.spark_type == 'concept'),
            'argument': sum(1 for c in clicks if c.spark_type == 'argument'),
        }

        return distribution
```

---

### 3.3 思维盲区探测 (Blind Spot Detection - V2)

#### 3.3.1 盲区识别算法

**算法 1：领域缺失检测**
```python
def detect_domain_gaps(user_id: int) -> List[str]:
    """
    检测用户未涉足的知识领域

    逻辑：
    1. 获取用户已阅读的所有领域
    2. 对比预定义的知识领域列表
    3. 返回缺失的领域
    """
    all_domains = ['人工智能', '经济学', '哲学', '历史', '生物学', ...]
    user_domains = db.query(Insight.domain).filter(
        Insight.user_id == user_id
    ).distinct().all()

    missing = set(all_domains) - set(user_domains)
    return list(missing)
```

**算法 2：知识孤岛识别**
```python
def detect_knowledge_islands(graph: nx.Graph) -> List[List[str]]:
    """
    使用图算法识别孤立的概念簇

    逻辑：
    1. 使用 NetworkX 的连通分量算法
    2. 识别规模 < 5 的孤立子图
    3. 推荐相关概念建立连接
    """
    components = nx.connected_components(graph)
    islands = [
        list(comp) for comp in components
        if len(comp) < 5 and len(comp) > 1
    ]
    return islands
```

**算法 3：跨域阅读建议**
```python
def suggest_cross_domain_reading(user_id: int) -> List[str]:
    """
    基于协同过滤推荐跨领域内容

    逻辑：
    1. 找到阅读偏好相似的其他用户
    2. 找到他们阅读但当前用户未接触的领域
    3. 返回推荐列表
    """
    similar_users = find_similar_users(user_id, top_k=10)
    their_domains = get_domains_of_users(similar_users)
    my_domains = get_domains_of_user(user_id)

    recommended = set(their_domains) - set(my_domains)
    return list(recommended)
```

#### 3.3.2 UI 设计

**盲区卡片**：
```vue
<template>
  <div class="blind-spot-card">
    <div class="icon">🔦</div>
    <h4>思维盲区探测</h4>

    <div class="gap-list">
      <div v-for="domain in missingDomains" :key="domain" class="gap-item">
        <span class="domain-name">{{ domain }}</span>
        <button @click="exploreDomain(domain)">
          去探索
        </button>
      </div>
    </div>

    <div class="islands" v-if="knowledgeIslands.length > 0">
      <h5>知识孤岛</h5>
      <p class="hint">
        这些概念彼此孤立，建议阅读相关内容建立联系：
      </p>
      <div v-for="island in knowledgeIslands" :key="island.id" class="island">
        {{ island.concepts.join(' · ') }}
      </div>
    </div>
  </div>
</template>
```

---

## 4. 数据库设计

### 4.1 新增表结构

**知识节点表**：
```sql
CREATE TABLE knowledge_nodes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    label VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL CHECK (type IN ('concept', 'entity')),
    size INTEGER DEFAULT 1,
    color VARCHAR(7),
    domain VARCHAR(100),
    insight_id UUID REFERENCES insights(id),
    review_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_knowledge_nodes_user_id ON knowledge_nodes(user_id);
CREATE INDEX idx_knowledge_nodes_domain ON knowledge_nodes(domain);
```

**知识关系表**：
```sql
CREATE TABLE knowledge_edges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    source_id UUID NOT NULL REFERENCES knowledge_nodes(id) ON DELETE CASCADE,
    target_id UUID NOT NULL REFERENCES knowledge_nodes(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL CHECK (type IN ('related', 'contrast', 'depends_on')),
    weight FLOAT DEFAULT 0.5 CHECK (weight BETWEEN 0 AND 1),
    label VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_knowledge_edges_user_id ON knowledge_edges(user_id);
CREATE INDEX idx_knowledge_edges_source ON knowledge_edges(source_id);
CREATE INDEX idx_knowledge_edges_target ON knowledge_edges(target_id);
```

**火花点击日志表**：
```sql
CREATE TABLE spark_clicks (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    spark_type VARCHAR(50) NOT NULL,
    spark_text TEXT NOT NULL,
    article_id INTEGER REFERENCES articles(id) ON DELETE SET NULL,
    clicked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_spark_clicks_user_id ON spark_clicks(user_id);
CREATE INDEX idx_spark_clicks_clicked_at ON spark_clicks(clicked_at);
```

**好奇心指纹缓存表**：
```sql
CREATE TABLE curiosity_fingerprints (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    spark_distribution JSONB NOT NULL,
    time_series JSONB NOT NULL,
    topic_cloud JSONB NOT NULL,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_curiosity_fingerprints_user_id ON curiosity_fingerprints(user_id);
```

---

## 5. API 设计

### 5.1 仪表盘总览

```http
GET /api/v1/dashboard
Authorization: Bearer <token>
```

**响应**：
```json
{
  "knowledgeGraph": {
    "totalNodes": 156,
    "totalEdges": 342,
    "domains": {
      "人工智能": 45,
      "经济学": 32,
      "哲学": 28
    }
  },
  "curiosityFingerprint": {
    "sparkDistribution": {
      "concept": 120,
      "argument": 85
    },
    "dominantType": "concept"
  },
  "blindSpots": {
    "missingDomains": ["历史", "生物学"],
    "knowledgeIslands": 3
  }
}
```

### 5.2 知识图谱数据

```http
GET /api/v1/dashboard/knowledge-graph
Authorization: Bearer <token>
```

**响应**：
```json
{
  "nodes": [
    {
      "id": "node_1",
      "label": "深度学习",
      "type": "concept",
      "size": 12,
      "color": "#10b981",
      "metadata": {
        "domain": "人工智能",
        "insightId": "insight_123",
        "createdAt": "2025-01-15T10:30:00Z",
        "reviewCount": 3
      }
    }
  ],
  "edges": [
    {
      "id": "edge_1",
      "source": "node_1",
      "target": "node_2",
      "type": "related",
      "weight": 0.8
    }
  ]
}
```

### 5.3 好奇心指纹

```http
GET /api/v1/dashboard/curiosity-fingerprint
Authorization: Bearer <token>
```

**响应**：
```json
{
  "sparkDistribution": {
    "concept": 120,
    "argument": 85
  },
  "timeSeries": [
    {
      "date": "2025-01-01",
      "sparkCounts": {
        "concept": 5,
        "argument": 3
      },
      "insightCounts": 8
    }
  ],
  "topicCloud": [
    {
      "topic": "人工智能",
      "count": 45,
      "weight": 1.0
    },
    {
      "topic": "量子计算",
      "count": 12,
      "weight": 0.27
    }
  ]
}
```

### 5.4 盲区探测

```http
GET /api/v1/dashboard/blind-spots
Authorization: Bearer <token>
```

**响应**：
```json
{
  "missingDomains": ["历史", "生物学", "心理学"],
  "knowledgeIslands": [
    {
      "id": "island_1",
      "concepts": ["量子纠缠", "薛定谔方程"],
      "recommendation": "建议阅读量子力学基础知识"
    }
  ],
  "crossDomainSuggestions": [
    {
      "domain": "神经科学",
      "reason": "与你的人工智能兴趣相关"
    }
  ]
}
```

---

## 6. 前端组件设计

### 6.1 页面结构

```vue
<template>
  <div class="dashboard-page">
    <!-- 顶部导航 -->
    <DashboardHeader />

    <!-- 主内容区 -->
    <div class="dashboard-grid">
      <!-- 左侧：知识图谱 -->
      <div class="graph-section">
        <KnowledgeGraph :data="graphData" />
      </div>

      <!-- 右侧：指标面板 -->
      <div class="metrics-section">
        <!-- 好奇心指纹 -->
        <CuriosityFingerprint :data="fingerprintData" />

        <!-- 思维盲区 -->
        <BlindSpotDetector :data="blindSpotData" />

        <!-- 统计卡片 -->
        <StatsCards :stats="dashboardStats" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const {
  graphData,
  fingerprintData,
  blindSpotData,
  dashboardStats
} = useDashboard()
</script>
```

### 6.2 核心组件

**KnowledgeGraph.vue**：
```vue
<template>
  <div ref="graphContainer" class="knowledge-graph">
    <svg ref="svgRef"></svg>

    <!-- 控制面板 -->
    <div class="controls">
      <button @click="zoomIn">放大</button>
      <button @click="zoomOut">缩小</button>
      <button @click="resetView">重置</button>

      <select v-model="filterDomain">
        <option value="all">全部领域</option>
        <option v-for="domain in domains" :key="domain">
          {{ domain }}
        </option>
      </select>
    </div>
  </div>
</template>

<script setup lang="ts">
import * as d3 from 'd3'

const props = defineProps<{
  data: { nodes: KnowledgeNode[], edges: KnowledgeEdge[] }
}>()

const svgRef = ref<SVGSVGElement | null>(null)

onMounted(() => {
  initGraph()
})

function initGraph() {
  const svg = d3.select(svgRef.value)
  const width = 800
  const height = 600

  // 力导向模拟
  const simulation = d3.forceSimulation(props.data.nodes)
    .force('link', d3.forceLink(props.data.edges).id(d => d.id))
    .force('charge', d3.forceManyBody().strength(-200))
    .force('center', d3.forceCenter(width / 2, height / 2))

  // 绘制边
  const links = svg.append('g')
    .selectAll('line')
    .data(props.data.edges)
    .enter().append('line')
    .attr('stroke', '#999')
    .attr('stroke-width', d => d.weight * 3)

  // 绘制节点
  const nodes = svg.append('g')
    .selectAll('circle')
    .data(props.data.nodes)
    .enter().append('circle')
    .attr('r', d => d.size * 5)
    .attr('fill', d => d.color)
    .call(drag(simulation))

  // 更新位置
  simulation.on('tick', () => {
    links
      .attr('x1', d => d.source.x)
      .attr('y1', d => d.source.y)
      .attr('x2', d => d.target.x)
      .attr('y2', d => d.target.y)

    nodes
      .attr('cx', d => d.x)
      .attr('cy', d => d.y)
  })
}

function drag(simulation) {
  function dragstarted(event, d) {
    if (!event.active) simulation.alphaTarget(0.3).restart()
    d.fx = d.x
    d.fy = d.y
  }

  function dragged(event, d) {
    d.fx = event.x
    d.fy = event.y
  }

  function dragended(event, d) {
    if (!event.active) simulation.alphaTarget(0)
    d.fx = null
    d.fy = null
  }

  return d3.drag()
    .on('start', dragstarted)
    .on('drag', dragged)
    .on('end', dragended)
}
</script>
```

**CuriosityFingerprint.vue**：
```vue
<template>
  <div class="curiosity-fingerprint">
    <h3>好奇心指纹</h3>

    <!-- 雷达图 -->
    <RadarChart :data="radarData" />

    <!-- 洞察文本 -->
    <div class="insight-text">
      <p class="dominant-type">
        {{ insightText }}
      </p>
    </div>

    <!-- 时序图 -->
    <h4>阅读活跃度（最近 30 天）</h4>
    <LineChart :data="timeSeriesData" />

    <!-- 话题云 -->
    <h4>热门话题</h4>
    <TagCloud :topics="topicCloudData" />
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  data: {
    sparkDistribution: Record<string, number>
    timeSeries: any[]
    topicCloud: any[]
  }
}>()

const insightText = computed(() => {
  const { concept, argument } = props.data.sparkDistribution

  if (concept > argument * 1.5) {
    return '💡 你是概念探索者：喜欢深挖专业术语和理论框架'
  } else if (argument > concept * 1.5) {
    return '🔍 你是逻辑思考者：关注论证过程和数据证据'
  } else {
    return '⚖️ 你是均衡学习者：概念和论证并重'
  }
})

const radarData = computed(() => {
  return Object.entries(props.data.sparkDistribution).map(([key, value]) => ({
    axis: key,
    value: value
  }))
})
</script>
```

---

## 7. 实施路线图

### Phase 1: MVP（4 周）

**Week 1-2: 后端基础**
- ✅ 数据库表设计和迁移
- ✅ API 端点实现（知识图谱、好奇心指纹）
- ✅ 火花点击埋点集成

**Week 3: 知识图谱构建**
- ✅ 概念提取算法
- ✅ 关系推断逻辑（基于共现）
- ✅ 图谱数据生成服务

**Week 4: 前端可视化**
- ✅ 知识图谱组件（D3.js）
- ✅ 好奇心指纹组件（Recharts）
- ✅ 仪表盘页面集成

### Phase 2: 优化（2 周）

**Week 5: 性能优化**
- 大图谱渐进式加载
- 异步任务队列（Celery）
- 缓存层优化

**Week 6: 盲区探测**
- 领域缺失检测
- 知识孤岛识别
- 推荐算法实现

### Phase 3: 增强（持续迭代）

- 🔮 LLM 增强的关系推断
- 🎯 个性化阅读推荐
- 📊 更丰富的可视化样式
- 🤝 社交功能（知识图谱分享）

---

## 8. 技术栈总结

### 前端
- **图谱可视化**: D3.js / Cytoscape.js
- **图表**: Recharts / Chart.js
- **动画**: GSAP
- **状态管理**: Nuxt 3 Composables

### 后端
- **框架**: FastAPI
- **任务队列**: Celery + Redis
- **NLP**: Stanza（已集成）
- **图算法**: NetworkX
- **LLM**: OpenAI API / Claude API

### 数据库
- **主库**: PostgreSQL
- **缓存**: Redis
- **向量存储**: pgvector（可选，用于概念相似度）

---

## 9. 风险评估与应对

### 风险 1: 图谱构建性能问题
**风险**: 用户洞察数量过多（1000+ 条）导致图谱生成缓慢

**应对**:
- 使用异步任务（Celery）后台构建
- 增量更新策略（只处理新增洞察）
- 图谱缓存（存入数据库）

### 风险 2: LLM API 成本
**风险**: 关系推断大量调用 LLM 导致成本高

**应对**:
- 优先使用共现算法（免费）
- LLM 仅用于关键关系验证
- 实现本地 embedding 模型（Sentence-BERT）

### 风险 3: 用户隐私
**风险**: 知识图谱泄露个人阅读偏好

**应对**:
- 所有数据用户隔离（user_id 分区）
- 图谱不可公开访问（除非用户主动分享）
- 敏感数据加密存储

---

## 10. 成功指标（KPIs）

### 用户参与度
- **仪表盘访问率**: 目标 >40% DAU 访问
- **图谱交互率**: 目标 >60% 用户点击节点
- **平均停留时长**: 目标 >2 分钟

### 功能有效性
- **知识图谱节点数**: 平均 >50 个/用户（30 天）
- **盲区探索转化率**: >15% 用户点击盲区推荐
- **火花点击增长**: 相比无仪表盘提升 >20%

### 技术性能
- **图谱加载时间**: <2 秒（100 节点）
- **API 响应时间**: P95 <500ms
- **缓存命中率**: >80%

---

## 11. 未来展望

### 个性化阅读推荐引擎
基于知识图谱的协同过滤：
- "喜欢深度学习的人也在读《复杂》"
- "你的知识图谱缺少经济学节点，推荐..."

### 知识图谱社交
- 分享你的知识图谱
- 对比好友的好奇心指纹
- 组队阅读挑战

### AI 教练
- "你最近对量子计算很感兴趣，建议阅读《量子之谜》"
- "检测到知识孤岛，为你生成连接路径"

---

## 结语

**个人认知仪表盘**不仅是一个功能，更是 InsightReader 哲学的升华：

> "阅读的意义不在于消费信息，而在于构建自己的知识体系。"

通过可视化、数据化、游戏化的设计，我们让用户：
1. **看见成长**：知识图谱的每一个新节点都是成就
2. **认识自己**：好奇心指纹揭示思维模式
3. **持续进步**：盲区探测推动跨界学习

这是一个将"深度阅读"转化为"深度学习"的工具。

---

**文档版本**: v1.0
**最后更新**: 2025-01-20
**负责人**: InsightReader Team
