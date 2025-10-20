# 个人认知仪表盘 - API 快速参考

## 📡 Base URL

```
开发环境: http://localhost:8000
生产环境: https://your-domain.com
```

## 🔐 认证

所有 API 端点都需要用户身份验证。前端通过 `useAuth()` composable 管理认证状态，后端通过 `user_id` 参数识别用户。

## 📋 Dashboard API

### 1. 获取仪表盘总览

获取用户的完整仪表盘数据，包括知识图谱、好奇心指纹、思维盲区和统计信息。

**请求**
```http
GET /api/v1/dashboard/?user_id={user_id}
```

**参数**
| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| user_id | integer | 是 | 用户 ID |

**响应示例**
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
    "timeSeries": [
      {"date": "2025-10-14", "count": 5},
      {"date": "2025-10-15", "count": 8},
      {"date": "2025-10-16", "count": 3},
      {"date": "2025-10-17", "count": 12},
      {"date": "2025-10-18", "count": 7},
      {"date": "2025-10-19", "count": 9},
      {"date": "2025-10-20", "count": 11}
    ],
    "topicCloud": [
      {"text": "深度学习", "size": 16},
      {"text": "神经网络", "size": 12},
      {"text": "人工智能", "size": 10}
    ]
  },
  "blindSpots": {
    "missingDomains": ["生物学", "物理学", "历史"],
    "knowledgeIslands": [
      {
        "id": "island-1",
        "concepts": ["深度学习", "神经网络", "反向传播"],
        "recommendation": "建议阅读有关机器学习算法的内容，建立与其他AI概念的联系"
      }
    ]
  },
  "stats": {
    "totalSparkClicks": 100,
    "totalInsights": 15,
    "activeStreak": 7
  }
}
```

**状态码**
- `200 OK`: 成功
- `404 Not Found`: 用户不存在
- `500 Internal Server Error`: 服务器错误

---

### 2. 获取知识图谱详情

获取用户的知识图谱完整数据，包括所有节点和边的详细信息。

**请求**
```http
GET /api/v1/dashboard/knowledge-graph?user_id={user_id}
```

**参数**
| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| user_id | integer | 是 | 用户 ID |

**响应示例**
```json
{
  "nodes": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
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
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "label": "神经网络",
      "type": "concept",
      "size": 6,
      "color": "#10b981",
      "metadata": {
        "domain": "人工智能",
        "insightId": 124,
        "createdAt": "2025-10-16T14:20:00",
        "reviewCount": 2
      }
    }
  ],
  "edges": [
    {
      "id": "edge-uuid-1",
      "source": "550e8400-e29b-41d4-a716-446655440000",
      "target": "550e8400-e29b-41d4-a716-446655440001",
      "type": "related",
      "weight": 0.8
    }
  ],
  "stats": {
    "totalNodes": 25,
    "totalEdges": 18,
    "domains": {
      "人工智能": 8,
      "哲学": 6,
      "经济学": 11
    }
  }
}
```

**数据类型说明**

**KnowledgeNode**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 节点唯一标识 (UUID) |
| label | string | 节点显示标签 (概念名称) |
| type | string | 节点类型: "concept" (概念) 或 "entity" (实体) |
| size | integer | 节点大小 (基于点击次数) |
| color | string | 节点颜色 (十六进制, 基于领域) |
| metadata.domain | string | 知识领域 |
| metadata.insightId | integer | 关联的洞察卡片 ID |
| metadata.createdAt | string | 创建时间 (ISO 8601) |
| metadata.reviewCount | integer | 复习次数 |

**KnowledgeEdge**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 边唯一标识 (UUID) |
| source | string | 源节点 ID |
| target | string | 目标节点 ID |
| type | string | 关系类型: "related" / "contrast" / "depends_on" |
| weight | float | 关系权重 (0.0 - 1.0) |

**状态码**
- `200 OK`: 成功
- `404 Not Found`: 用户不存在或无数据
- `500 Internal Server Error`: 服务器错误

---

### 3. 获取好奇心指纹

获取用户的好奇心指纹分析数据，包括火花类型分布、时间序列和话题云。

**请求**
```http
GET /api/v1/dashboard/curiosity-fingerprint?user_id={user_id}
```

**参数**
| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| user_id | integer | 是 | 用户 ID |

**响应示例**
```json
{
  "dominantType": "concept",
  "sparkDistribution": {
    "concept": 45,
    "argument": 30,
    "entity": 25
  },
  "timeSeries": [
    {"date": "2025-10-14", "count": 5},
    {"date": "2025-10-15", "count": 8},
    {"date": "2025-10-16", "count": 3},
    {"date": "2025-10-17", "count": 12},
    {"date": "2025-10-18", "count": 7},
    {"date": "2025-10-19", "count": 9},
    {"date": "2025-10-20", "count": 11}
  ],
  "topicCloud": [
    {"text": "深度学习", "size": 16},
    {"text": "神经网络", "size": 12},
    {"text": "人工智能", "size": 10},
    {"text": "反向传播", "size": 8},
    {"text": "卷积网络", "size": 6}
  ]
}
```

**数据说明**
| 字段 | 类型 | 说明 |
|------|------|------|
| dominantType | string | 主导火花类型: "concept" / "argument" / "entity" |
| sparkDistribution | object | 火花类型分布 (数量统计) |
| timeSeries | array | 最近7天点击时间序列 |
| timeSeries[].date | string | 日期 (YYYY-MM-DD) |
| timeSeries[].count | integer | 当天点击数 |
| topicCloud | array | 高频话题词 (前20个) |
| topicCloud[].text | string | 话题词 |
| topicCloud[].size | integer | 词频 (用于可视化大小) |

**状态码**
- `200 OK`: 成功
- `404 Not Found`: 用户不存在或无数据
- `500 Internal Server Error`: 服务器错误

---

### 4. 获取思维盲区

获取用户的思维盲区分析，包括未探索的知识领域和知识孤岛。

**请求**
```http
GET /api/v1/dashboard/blind-spots?user_id={user_id}
```

**参数**
| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| user_id | integer | 是 | 用户 ID |

**响应示例**
```json
{
  "missingDomains": ["生物学", "物理学", "历史"],
  "knowledgeIslands": [
    {
      "id": "island-1",
      "concepts": ["深度学习", "神经网络", "反向传播"],
      "recommendation": "建议阅读有关机器学习算法的内容，建立与其他AI概念的联系"
    },
    {
      "id": "island-2",
      "concepts": ["市场经济", "供需关系"],
      "recommendation": "建议学习宏观经济学，将微观概念与宏观视角连接"
    }
  ]
}
```

**数据说明**
| 字段 | 类型 | 说明 |
|------|------|------|
| missingDomains | array | 用户未涉足的知识领域列表 |
| knowledgeIslands | array | 知识孤岛列表 (孤立的概念集合) |
| knowledgeIslands[].id | string | 孤岛唯一标识 |
| knowledgeIslands[].concepts | array | 孤岛中的概念列表 |
| knowledgeIslands[].recommendation | string | 建立联系的建议 |

**盲区检测逻辑**
- **缺失领域**: 预定义领域集合 - 用户已涉足领域
- **知识孤岛**: 使用 DFS 算法查找图中的连通分量，孤立的分量即为孤岛

**状态码**
- `200 OK`: 成功
- `404 Not Found`: 用户不存在
- `500 Internal Server Error`: 服务器错误

---

### 5. 重建知识图谱

强制重建用户的知识图谱，重新分析所有火花点击记录。

**请求**
```http
POST /api/v1/dashboard/rebuild
Content-Type: application/json
```

**请求体**
```json
{
  "user_id": 1
}
```

**参数**
| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| user_id | integer | 是 | 用户 ID |

**响应示例**
```json
{
  "message": "知识图谱重建成功",
  "stats": {
    "nodesCreated": 25,
    "edgesCreated": 18,
    "processingTimeMs": 1234
  }
}
```

**数据说明**
| 字段 | 类型 | 说明 |
|------|------|------|
| message | string | 操作结果消息 |
| stats.nodesCreated | integer | 创建的节点数 |
| stats.edgesCreated | integer | 创建的边数 |
| stats.processingTimeMs | integer | 处理耗时 (毫秒) |

**重建过程**
1. 删除用户的所有旧节点和边
2. 从火花点击记录重新提取概念和实体
3. 基于共现分析重新构建关系
4. 识别领域并分配颜色

**使用场景**
- 数据损坏或不一致时
- 算法升级后重新分析
- 用户手动触发 (前端"重建图谱"按钮)

**状态码**
- `200 OK`: 重建成功
- `400 Bad Request`: 请求参数错误
- `404 Not Found`: 用户不存在
- `500 Internal Server Error`: 重建失败

---

## 📊 Analytics API

### 记录火花点击

记录用户点击火花的行为，自动更新好奇心指纹和知识图谱。

**请求**
```http
POST /api/v1/analytics/spark-click
Content-Type: application/json
```

**请求体**
```json
{
  "user_id": 1,
  "spark_type": "concept",
  "spark_text": "深度学习"
}
```

**参数**
| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| user_id | integer | 是 | 用户 ID |
| spark_type | string | 是 | 火花类型: "concept" / "argument" / "entity" |
| spark_text | string | 是 | 火花文本内容 |

**响应示例**
```json
{
  "message": "火花点击已记录",
  "clickId": 12345
}
```

**数据说明**
| 字段 | 类型 | 说明 |
|------|------|------|
| message | string | 操作结果消息 |
| clickId | integer | 点击记录 ID |

**触发流程**
1. 创建 `SparkClick` 记录
2. 更新 `CuriosityFingerprint` 缓存
3. 增量更新知识图谱 (如需要)

**调用时机**
- 用户在阅读文章时点击火花
- 前端 `useSparkAnalyzer.ts` 中的 `handleSparkClick()` 自动调用

**状态码**
- `200 OK`: 记录成功
- `400 Bad Request`: 请求参数错误
- `401 Unauthorized`: 用户未登录
- `500 Internal Server Error`: 记录失败

---

## 🔧 前端使用示例

### 使用 useDashboard Composable

```typescript
<script setup lang="ts">
import { useDashboard } from '~/composables/useDashboard'
import { useAuth } from '~/composables/useAuth'

const { user } = useAuth()
const {
  overview,
  knowledgeGraph,
  curiosityFingerprint,
  blindSpots,
  isLoading,
  fetchOverview,
  fetchKnowledgeGraph,
  rebuildKnowledgeGraph,
  recordSparkClick
} = useDashboard()

// 加载总览
onMounted(async () => {
  if (user.value?.id) {
    await fetchOverview(user.value.id)
  }
})

// 加载知识图谱
const loadGraph = async () => {
  if (user.value?.id) {
    await fetchKnowledgeGraph(user.value.id)
  }
}

// 重建图谱
const rebuild = async () => {
  if (user.value?.id) {
    await rebuildKnowledgeGraph(user.value.id)
  }
}

// 记录火花点击
const handleSparkClick = async (type: string, text: string) => {
  if (user.value?.id) {
    await recordSparkClick(user.value.id, type, text)
  }
}
</script>

<template>
  <div>
    <div v-if="isLoading">加载中...</div>
    <div v-else-if="overview">
      <p>总节点数: {{ overview.knowledgeGraph.totalNodes }}</p>
      <p>总关系数: {{ overview.knowledgeGraph.totalEdges }}</p>
      <p>主导类型: {{ overview.curiosityFingerprint.dominantType }}</p>
    </div>
  </div>
</template>
```

### 直接调用 API (fetch)

```typescript
// 获取仪表盘总览
const response = await $fetch('/api/v1/dashboard/', {
  method: 'GET',
  params: { user_id: 1 }
})

// 重建知识图谱
const response = await $fetch('/api/v1/dashboard/rebuild', {
  method: 'POST',
  body: { user_id: 1 }
})

// 记录火花点击
const response = await $fetch('/api/v1/analytics/spark-click', {
  method: 'POST',
  body: {
    user_id: 1,
    spark_type: 'concept',
    spark_text: '深度学习'
  }
})
```

---

## 🐛 错误响应

所有 API 端点在发生错误时返回统一格式:

```json
{
  "detail": "错误描述信息"
}
```

**常见错误码**
- `400 Bad Request`: 请求参数错误或缺失
- `401 Unauthorized`: 用户未认证
- `404 Not Found`: 资源不存在
- `500 Internal Server Error`: 服务器内部错误

---

## 📈 性能建议

1. **缓存**: 好奇心指纹数据已缓存，避免重复计算
2. **分页**: 大量节点时考虑分页加载 (未实现)
3. **节流**: 前端可对重建操作进行节流，避免频繁调用
4. **索引**: 数据库关键字段已添加索引，提升查询性能

---

## 🔄 数据更新时机

| 操作 | 触发更新 |
|------|---------|
| 点击火花 | ✅ 立即更新 SparkClick + CuriosityFingerprint |
| 重建图谱 | ✅ 完全重建 KnowledgeNode + KnowledgeEdge |
| 加载仪表盘 | ❌ 仅读取，不触发更新 |
| 删除用户 | ⚠️ 需手动清理关联数据 (级联删除) |

---

**文档版本**: 1.0.0
**最后更新**: 2025-10-20
**维护者**: InsightReader Team
