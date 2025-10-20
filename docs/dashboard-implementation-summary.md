# 个人认知仪表盘 - 实现总结

## 📋 概述

本文档记录了 InsightReader 个人认知仪表盘功能的完整实现过程和技术细节。

**实施日期**: 2025年10月
**功能状态**: ✅ 已完成并集成

## 🎯 核心功能

### 1. 知识图谱可视化 (Knowledge Graph)
- **技术栈**: D3.js v7 力导向图 (Force-Directed Graph)
- **核心特性**:
  - 基于物理模拟的动态布局
  - 支持缩放 (Zoom) 和平移 (Pan)
  - 节点拖拽重排
  - 点击节点查看详情
  - 悬停动画效果
  - 模拟暂停/继续控制
  - 视图重置功能

- **力模拟参数**:
  ```javascript
  .force('link', d3.forceLink().distance(100).strength(0.5))
  .force('charge', d3.forceManyBody().strength(-300))
  .force('center', d3.forceCenter(width/2, height/2))
  .force('collision', d3.forceCollide().radius(d => d.size * 3 + 10))
  ```

- **节点生成逻辑**:
  - 从用户火花点击记录提取概念 (concept) 和实体 (entity)
  - 节点大小由点击次数决定 (`size = click_count`)
  - 自动识别知识领域 (domain) 并分配颜色

- **关系推断**:
  - 共现分析: 同一文章中出现的概念自动建立关联
  - 关系权重由共现频次决定
  - 支持多种关系类型: related, contrast, depends_on

### 2. 好奇心指纹分析 (Curiosity Fingerprint)
- **数据维度**:
  - 火花类型分布 (Spark Distribution): concept, argument, entity
  - 时间序列分析 (Time Series): 最近7天点击趋势
  - 话题云 (Topic Cloud): 高频词汇提取

- **计算逻辑**:
  ```python
  # 统计最近30天的火花点击
  clicks = db.query(SparkClick).filter(
      SparkClick.user_id == user_id,
      SparkClick.clicked_at >= datetime.utcnow() - timedelta(days=30)
  ).all()

  # 提取主导类型
  dominant_type = max(spark_distribution.items(), key=lambda x: x[1])[0]
  ```

- **缓存机制**:
  - 结果存储在 `curiosity_fingerprints` 表
  - 每次火花点击后自动更新
  - 避免重复计算，提升性能

### 3. 思维盲区探测 (Blind Spot Detection)
- **检测维度**:
  - **缺失领域** (Missing Domains): 用户未涉足的知识领域
  - **知识孤岛** (Knowledge Islands): 孤立的概念集合

- **孤岛检测算法**:
  ```python
  # 使用 DFS 查找连通分量
  def _find_connected_components(nodes, edges):
      adjacency = defaultdict(set)
      for edge in edges:
          adjacency[edge.source_id].add(edge.target_id)
          adjacency[edge.target_id].add(edge.source_id)

      visited = set()
      islands = []

      def dfs(node_id, component):
          visited.add(node_id)
          component.add(node_id)
          for neighbor in adjacency[node_id]:
              if neighbor not in visited:
                  dfs(neighbor, component)

      for node in nodes:
          if node.id not in visited:
              component = set()
              dfs(node.id, component)
              if len(component) >= 2:
                  islands.append(component)

      return islands
  ```

- **推荐生成**:
  - 为每个孤岛生成阅读建议
  - 提示用户建立概念之间的联系

## 🗄️ 数据库设计

### 新增表结构

#### 1. knowledge_nodes (知识节点表)
```sql
CREATE TABLE knowledge_nodes (
    id VARCHAR(36) PRIMARY KEY,
    user_id INTEGER NOT NULL,
    label VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,  -- 'concept' | 'entity'
    size INTEGER DEFAULT 1,
    color VARCHAR(7),
    domain VARCHAR(100),
    insight_id INTEGER,
    review_count INTEGER DEFAULT 0,
    created_at DATETIME,
    updated_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (insight_id) REFERENCES insight_cards(id),
    INDEX idx_user_id (user_id),
    INDEX idx_domain (domain)
);
```

#### 2. knowledge_edges (知识关系表)
```sql
CREATE TABLE knowledge_edges (
    id VARCHAR(36) PRIMARY KEY,
    source_id VARCHAR(36) NOT NULL,
    target_id VARCHAR(36) NOT NULL,
    type VARCHAR(50) DEFAULT 'related',  -- 'related' | 'contrast' | 'depends_on'
    weight FLOAT DEFAULT 0.5,
    created_at DATETIME,
    FOREIGN KEY (source_id) REFERENCES knowledge_nodes(id),
    FOREIGN KEY (target_id) REFERENCES knowledge_nodes(id),
    INDEX idx_source (source_id),
    INDEX idx_target (target_id)
);
```

#### 3. spark_clicks (火花点击日志表)
```sql
CREATE TABLE spark_clicks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    spark_type VARCHAR(50) NOT NULL,
    spark_text TEXT NOT NULL,
    clicked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user_id (user_id),
    INDEX idx_clicked_at (clicked_at)
);
```

#### 4. curiosity_fingerprints (好奇心指纹缓存表)
```sql
CREATE TABLE curiosity_fingerprints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    spark_distribution JSON,
    time_series JSON,
    topic_cloud JSON,
    updated_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

## 🔌 API 端点

### Dashboard API (`/api/v1/dashboard/`)

#### 1. 获取仪表盘总览
```http
GET /api/v1/dashboard/?user_id={user_id}
```

**响应示例**:
```json
{
  "knowledgeGraph": {
    "totalNodes": 25,
    "totalEdges": 18,
    "domains": {
      "人工智能": 8,
      "哲学": 6,
      "经济学": 11
    }
  },
  "curiosityFingerprint": {
    "dominantType": "concept",
    "sparkDistribution": {
      "concept": 45,
      "argument": 30,
      "entity": 25
    },
    "timeSeries": [...],
    "topicCloud": [...]
  },
  "blindSpots": {
    "missingDomains": ["生物学", "物理学"],
    "knowledgeIslands": [...]
  },
  "stats": {
    "totalSparkClicks": 100,
    "totalInsights": 15,
    "activeStreak": 7
  }
}
```

#### 2. 获取知识图谱详情
```http
GET /api/v1/dashboard/knowledge-graph?user_id={user_id}
```

**响应示例**:
```json
{
  "nodes": [
    {
      "id": "node-uuid-1",
      "label": "深度学习",
      "type": "concept",
      "size": 8,
      "color": "#10b981",
      "metadata": {
        "domain": "人工智能",
        "insightId": 123,
        "createdAt": "2025-10-15T10:30:00",
        "reviewCount": 3
      }
    }
  ],
  "edges": [
    {
      "id": "edge-uuid-1",
      "source": "node-uuid-1",
      "target": "node-uuid-2",
      "type": "related",
      "weight": 0.8
    }
  ],
  "stats": {
    "totalNodes": 25,
    "totalEdges": 18,
    "domains": {...}
  }
}
```

#### 3. 获取好奇心指纹
```http
GET /api/v1/dashboard/curiosity-fingerprint?user_id={user_id}
```

#### 4. 获取思维盲区
```http
GET /api/v1/dashboard/blind-spots?user_id={user_id}
```

#### 5. 重建知识图谱
```http
POST /api/v1/dashboard/rebuild
Content-Type: application/json

{
  "user_id": 1
}
```

### Analytics API (`/api/v1/analytics/`)

#### 记录火花点击
```http
POST /api/v1/analytics/spark-click
Content-Type: application/json

{
  "user_id": 1,
  "spark_type": "concept",
  "spark_text": "深度学习"
}
```

## 🎨 前端实现

### 组件架构

```
dashboard.vue (页面)
├── AppHeader (导航栏)
├── KnowledgeGraph.vue (知识图谱)
├── CuriosityFingerprint.vue (好奇心指纹)
└── BlindSpotDetector.vue (思维盲区)
```

### 状态管理

使用 Nuxt 3 的 `useState` API 实现全局状态:

```typescript
// composables/useDashboard.ts
const overview = useState<DashboardOverview | null>('dashboard-overview', () => null)
const knowledgeGraph = useState<KnowledgeGraphData | null>('knowledge-graph', () => null)
const curiosityFingerprint = useState<CuriosityFingerprintData | null>('curiosity-fingerprint', () => null)
const blindSpots = useState<BlindSpotsData | null>('blind-spots', () => null)
```

### 设计系统

**一致性原则**: 所有组件与现有前端保持一致的"深邃、冥想"美学风格

**核心样式模式**:
```css
/* 卡片容器 */
.card {
  @apply bg-white/70 backdrop-blur-xl border border-gray-200/50 rounded-2xl shadow-sm;
}

/* 渐变背景 */
.background {
  @apply bg-gradient-to-br from-slate-50 via-white to-zinc-50;
}

/* 图标容器 */
.icon-container {
  @apply w-10 h-10 bg-gradient-to-br from-emerald-500 to-teal-600
         rounded-xl flex items-center justify-center shadow-md;
}

/* 渐变文字 */
.gradient-text {
  @apply bg-gradient-to-r from-slate-800 to-zinc-700
         bg-clip-text text-transparent font-bold;
}

/* 模糊光球装饰 */
<div class="fixed inset-0 overflow-hidden pointer-events-none">
  <div class="absolute -top-40 -right-40 w-96 h-96 bg-emerald-400/10 rounded-full blur-3xl"></div>
  <div class="absolute top-1/3 -left-40 w-80 h-80 bg-teal-400/10 rounded-full blur-3xl"></div>
</div>
```

**颜色主题**:
- 主色: Emerald (#10b981) → Teal (#14b8a6) 渐变
- 辅助色: Slate (#64748b) → Zinc (#71717a) 渐变
- 强调色: Amber (#f59e0b) → Orange (#f97316) 渐变

### D3.js 集成

**安装依赖**:
```json
{
  "dependencies": {
    "d3": "^7.9.0"
  }
}
```

**导入和类型**:
```typescript
import * as d3 from 'd3'
import type { KnowledgeGraphData, KnowledgeNode, KnowledgeEdge } from '~/composables/useDashboard'
```

**关键实现**:
- SVG 画布: 响应式宽度，固定高度 500px
- 缩放范围: 0.1x - 4x
- 拖拽固定: 拖拽时固定节点位置 (fx, fy)
- 拖拽结束: 释放节点，恢复物理模拟
- Tick 更新: 每帧更新节点和边的位置

### 用户认证集成

**认证流程**:
```typescript
// pages/dashboard.vue
const { isAuthenticated, user } = useAuth()
const userId = computed(() => user.value?.id || null)

onMounted(async () => {
  // 检查登录状态
  if (!isAuthenticated.value) {
    router.push('/login')
    return
  }

  // 加载仪表盘数据
  if (userId.value) {
    await fetchOverview(userId.value)
  }
})

// 监听用户变化
watch(userId, async (newUserId) => {
  if (newUserId) {
    await fetchOverview(newUserId)
  }
})
```

**火花点击埋点**:
```typescript
// composables/useSparkAnalyzer.ts
const handleSparkClick = async (event: Event) => {
  // ... 火花交互逻辑 ...

  // 记录点击（仅登录用户）
  const { recordSparkClick } = useDashboard()
  const { user } = useAuth()

  if (user.value?.id) {
    await recordSparkClick(user.value.id, sparkType, sparkText)
  }
}
```

## 🔧 后端服务

### 服务层架构

```
services/
├── analytics_service.py      # 火花点击追踪、好奇心指纹计算
└── knowledge_graph_service.py # 知识图谱构建、盲区检测
```

### 核心算法

#### 1. 领域识别
```python
def _identify_domain(self, concept: str) -> str:
    """基于关键词匹配识别概念所属领域"""
    domain_keywords = {
        "人工智能": ["深度学习", "神经网络", "机器学习", "AI", "算法"],
        "哲学": ["存在", "本质", "意识", "认识论", "伦理"],
        "经济学": ["市场", "供需", "通货膨胀", "资本", "贸易"],
        # ... 更多领域
    }

    for domain, keywords in domain_keywords.items():
        for keyword in keywords:
            if keyword in concept:
                return domain

    return "未分类"
```

#### 2. 颜色分配
```python
def _assign_color_by_domain(self, domain: str) -> str:
    """根据领域分配颜色"""
    color_map = {
        "人工智能": "#10b981",  # emerald-500
        "哲学": "#8b5cf6",       # violet-500
        "经济学": "#f59e0b",     # amber-500
        "未分类": "#64748b",     # slate-500
        # ... 更多映射
    }
    return color_map.get(domain, "#64748b")
```

#### 3. 话题提取
```python
def _extract_topic_cloud(self, clicks: List[SparkClick]) -> List[Dict]:
    """提取高频话题词"""
    from collections import Counter

    all_texts = ' '.join([click.spark_text for click in clicks])

    # 简单分词（生产环境应使用 jieba 等专业分词库）
    words = all_texts.split()
    word_counts = Counter(words)

    # 取前20个高频词
    top_words = word_counts.most_common(20)

    return [
        {"text": word, "size": count * 2}
        for word, count in top_words
    ]
```

## 📊 性能优化

### 1. 数据库索引
```python
# 关键字段索引
Index('idx_user_id', KnowledgeNode.user_id)
Index('idx_domain', KnowledgeNode.domain)
Index('idx_clicked_at', SparkClick.clicked_at)
```

### 2. 缓存策略
- 好奇心指纹计算结果缓存
- 仅在火花点击后更新，避免重复计算
- 使用 JSON 字段存储复杂数据结构

### 3. 前端优化
- 使用 `readonly()` 防止意外修改状态
- 组件懒加载 (`v-if` 条件渲染)
- D3.js 模拟可暂停，减少不必要计算
- 节流防抖 (未来可添加)

## 🧪 测试建议

### 单元测试
```python
# tests/test_analytics_service.py
def test_record_spark_click():
    service = AnalyticsService(db)
    service.record_spark_click(user_id=1, spark_type="concept", spark_text="测试概念")

    clicks = db.query(SparkClick).filter(SparkClick.user_id == 1).all()
    assert len(clicks) > 0

def test_compute_curiosity_fingerprint():
    service = AnalyticsService(db)
    # 插入测试数据...
    fingerprint = service._compute_curiosity_fingerprint(user_id=1)

    assert "spark_distribution" in fingerprint
    assert "dominant_type" in fingerprint
```

### 集成测试
```python
# tests/test_dashboard_api.py
def test_get_dashboard_overview(client):
    response = client.get("/api/v1/dashboard/?user_id=1")
    assert response.status_code == 200

    data = response.json()
    assert "knowledgeGraph" in data
    assert "curiosityFingerprint" in data
    assert "blindSpots" in data
```

### 前端测试
```typescript
// tests/composables/useDashboard.spec.ts
import { describe, it, expect } from 'vitest'
import { useDashboard } from '~/composables/useDashboard'

describe('useDashboard', () => {
  it('should fetch knowledge graph', async () => {
    const { fetchKnowledgeGraph, knowledgeGraph } = useDashboard()
    await fetchKnowledgeGraph(1)

    expect(knowledgeGraph.value).toBeDefined()
    expect(knowledgeGraph.value?.nodes).toBeInstanceOf(Array)
  })
})
```

## 🚀 部署注意事项

### 数据库迁移
```bash
# 使用 Alembic 或手动执行
alembic revision --autogenerate -m "Add dashboard tables"
alembic upgrade head
```

### 环境变量
```env
# .env
DATABASE_URL=sqlite:///./insightreader.db
SECRET_KEY=your-secret-key
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

### 依赖安装
```bash
# 后端
cd backend
pip install -r requirements.txt

# 前端
cd frontend
npm install
```

### 启动服务
```bash
# 后端 (开发环境)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 前端 (开发环境)
npm run dev

# 生产环境构建
npm run build
npm run preview
```

## 🔮 未来增强方向

### 1. LLM 增强的关系推断
```python
# 使用 AI 识别概念之间的深层关系
def _infer_relationships_with_llm(self, concepts: List[str]) -> List[Dict]:
    prompt = f"""
    分析以下概念之间的关系：
    {', '.join(concepts)}

    返回格式：
    - 概念A -> 概念B: 关系类型 (related/contrast/depends_on)
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    # 解析响应，构建关系...
```

### 2. Celery 异步任务队列
```python
# tasks/knowledge_graph.py
from celery import Celery

celery = Celery('tasks', broker='redis://localhost:6379/0')

@celery.task
def rebuild_knowledge_graph_async(user_id: int):
    """异步重建知识图谱"""
    service = KnowledgeGraphService(db)
    service.rebuild_knowledge_graph(user_id)
    return {"status": "completed", "user_id": user_id}
```

### 3. 图谱高级交互
- 节点聚类视图 (按领域分组)
- 关系类型筛选
- 时间轴回放 (查看知识增长过程)
- 导出为 PNG/SVG
- 全屏沉浸模式

### 4. 社交功能
- 知识图谱分享
- 好奇心指纹对比
- 推荐相似用户

### 5. 高级分析
- 知识深度评分
- 学习路径推荐
- 认知盲区预警

## 📝 变更日志

### v1.0.0 - 2025-10-20
- ✅ 完成数据库表设计
- ✅ 实现后端 API (dashboard, analytics)
- ✅ 实现前端页面和组件
- ✅ D3.js 知识图谱可视化
- ✅ 用户认证集成
- ✅ 设计系统一致性
- ✅ 火花点击埋点

## 🙏 致谢

感谢以下开源项目:
- **D3.js**: 强大的数据可视化库
- **FastAPI**: 现代化的 Python Web 框架
- **Nuxt 3**: Vue.js 全栈框架
- **Tailwind CSS**: 实用优先的 CSS 框架
- **SQLAlchemy**: Python SQL 工具包

---

**文档维护者**: InsightReader Team
**最后更新**: 2025-10-20
**版本**: 1.0.0
