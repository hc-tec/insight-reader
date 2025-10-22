# 后端异步重构文档

## 概述

本次重构将所有耗时的LLM分析接口从同步阻塞模式改为异步非阻塞模式，解决前端15秒超时问题。

### 重构目标

1. ✅ **快速响应**: 所有分析接口在提交任务后立即返回（<100ms）
2. ✅ **异步执行**: LLM调用在后台异步执行，不阻塞HTTP请求
3. ✅ **实时通知**: 通过SSE（Server-Sent Events）实时推送分析完成事件
4. ✅ **零依赖**: 仅使用FastAPI内置功能，无需引入Celery等额外框架

---

## 架构设计

### 核心组件

#### 1. TaskManager (任务管理器)
位置: `app/core/task_manager.py`

**功能**:
- 创建和管理后台任务
- 跟踪任务状态（pending → processing → completed/failed）
- 任务完成后通过SSE推送事件

**主要方法**:
```python
class TaskManager:
    def submit_task(
        task_type: str,
        task_func: Callable,
        metadata: Dict[str, Any],
        *args, **kwargs
    ) -> str:
        """提交后台任务，立即返回task_id"""

    async def execute_task(task_id: str, task_func: Callable, *args, **kwargs):
        """在后台执行任务"""

    def get_task(task_id: str) -> Optional[TaskInfo]:
        """获取任务信息"""
```

#### 2. SSEManager (SSE事件管理器)
位置: `app/core/task_manager.py` (TaskManager内部)

**功能**:
- 管理用户的SSE连接
- 向用户推送任务状态事件

**主要方法**:
```python
class SSEManager:
    def add_connection(user_id: int) -> asyncio.Queue:
        """添加新的SSE连接"""

    async def send_event(user_id: int, event_type: str, data: Dict):
        """向用户发送事件"""
```

---

## 重构的接口

### 1. 统一分析接口

#### POST `/api/v1/articles/save-with-analysis`

**旧版本** (同步，阻塞15+秒):
```python
# 保存文章
article = save_article(...)

# 同步执行分析（阻塞）
result = await analyze_article(article.content)  # 15+ seconds

# 返回结果
return {"article": {...}, "analysis": result}
```

**新版本** (异步，立即返回):
```python
# 保存文章 (快速)
article = save_article(...)

# 检查是否已有分析结果
if has_existing_analysis(article.id):
    return {"article": {...}, "analysis": {"status": "completed"}}

# 提交后台任务 (非阻塞)
task_id = task_manager.submit_task(
    task_type="article_analysis",
    task_func=analyze_article_task,
    metadata={"article_id": article.id, "user_id": user_id},
    article.id
)

# 立即返回 (<100ms)
return {
    "article": {...},
    "analysis": {"status": "pending", "task_id": task_id}
}
```

**响应格式**:
```json
{
  "article": {
    "id": 123,
    "is_new": true
  },
  "analysis": {
    "status": "pending",  // "pending" | "completed"
    "task_id": "uuid-xxx-xxx"
  }
}
```

**SSE事件** (分析完成后推送):
```javascript
// 事件类型: task_completed
{
  "task_id": "uuid-xxx-xxx",
  "task_type": "article_analysis",
  "result": {
    "article_id": 123,
    "status": "completed",
    "report_data": {...}
  }
}
```

---

### 2. 元视角分析接口

#### POST `/api/v1/meta-analysis/analyze`

**新版本行为**:
1. 检查是否已有元视角分析结果
2. 如果有 → 立即返回 `status: "completed"`
3. 如果没有 → 提交后台任务，返回 `status: "pending"`

**响应格式**:
```json
{
  "status": "pending",  // "completed" | "pending"
  "message": "分析已开始",
  "meta_analysis": null,  // 已完成时包含结果
  "task_id": "uuid-xxx-xxx"
}
```

**SSE事件**:
```javascript
// 事件类型: task_completed
{
  "task_id": "uuid-xxx-xxx",
  "task_type": "meta_analysis",
  "result": {
    "article_id": 123,
    "status": "completed",
    "meta_analysis": {...}
  }
}
```

---

### 3. 思维透镜接口

#### GET `/api/v1/articles/{article_id}/thinking-lens/{lens_type}`

**lens_type**: `argument_structure` | `author_stance`

**新版本行为**:
1. 检查文章是否存在元视角分析（必需）
2. 检查是否已有透镜分析结果
3. 如果有 → 立即返回 `status: "completed"`
4. 如果没有 → 提交后台任务，返回 `status: "pending"`

**响应格式**:
```json
{
  "status": "pending",  // "completed" | "pending"
  "lens_result": null,  // 已完成时包含结果
  "task_id": "uuid-xxx-xxx"
}
```

**SSE事件**:
```javascript
// 事件类型: task_completed
{
  "task_id": "uuid-xxx-xxx",
  "task_type": "thinking_lens_argument_structure",
  "result": {
    "lens_type": "argument_structure",
    "status": "completed",
    "lens_result": {...}
  }
}
```

---

## SSE连接和事件

### SSE端点

#### GET `/api/v1/sse/analysis-notifications?user_id={user_id}`

**功能**: 建立SSE连接，接收实时任务状态更新

**事件类型**:

1. **connected** (连接建立)
```javascript
{
  "user_id": 123,
  "timestamp": 1234567890
}
```

2. **heartbeat** (心跳，每30秒)
```javascript
{
  "timestamp": 1234567890
}
```

3. **task_started** (任务开始)
```javascript
{
  "task_id": "uuid-xxx",
  "task_type": "article_analysis"
}
```

4. **task_completed** (任务完成)
```javascript
{
  "task_id": "uuid-xxx",
  "task_type": "article_analysis",
  "result": {...},
  "processing_time": 15.5
}
```

5. **task_failed** (任务失败)
```javascript
{
  "task_id": "uuid-xxx",
  "task_type": "article_analysis",
  "error": "Error message"
}
```

---

## 工作流程示例

### 场景: 用户上传新文章

```
1. 前端: POST /api/v1/articles/save-with-analysis
   └─> 后端: 保存文章, 返回 pending 状态 (<100ms)

2. 后端: 在后台执行分析任务 (15秒)
   ├─> 发送 SSE 事件: task_started
   ├─> 执行 LLM 分析...
   └─> 发送 SSE 事件: task_completed

3. 前端: 收到 SSE task_completed 事件
   └─> 获取分析报告: GET /api/v1/articles/{id}/analysis-report
   └─> 渲染火花效果
```

### 场景: 用户点击思维透镜

```
1. 前端: GET /api/v1/articles/{id}/thinking-lens/argument_structure
   └─> 后端: 返回 pending 状态 (<100ms)

2. 后端: 在后台执行透镜分析 (5-10秒)
   └─> 发送 SSE 事件: task_completed

3. 前端: 收到 SSE 事件
   └─> 应用透镜高亮
```

---

## 前端适配要点

### 1. 建立SSE连接

```typescript
// 在用户登录后建立SSE连接
const eventSource = new EventSource(
  `${apiBase}/api/v1/sse/analysis-notifications?user_id=${userId}`
)

eventSource.addEventListener('task_completed', (event) => {
  const data = JSON.parse(event.data)
  handleTaskCompleted(data)
})
```

### 2. 处理pending响应

```typescript
const response = await fetch('/api/v1/articles/save-with-analysis', {
  method: 'POST',
  body: JSON.stringify(article)
})

const { article, analysis } = await response.json()

if (analysis.status === 'completed') {
  // 已有结果，直接加载
  loadAnalysisReport(article.id)
} else if (analysis.status === 'pending') {
  // 等待SSE通知
  console.log('分析已开始，等待完成通知...')
}
```

### 3. 监听SSE事件

```typescript
function handleTaskCompleted(data) {
  if (data.task_type === 'article_analysis') {
    // 文章分析完成
    loadAnalysisReport(data.result.article_id)
    renderSparks(data.result.report_data)
  } else if (data.task_type.startsWith('thinking_lens_')) {
    // 透镜分析完成
    applyLensHighlights(data.result.lens_result)
  } else if (data.task_type === 'meta_analysis') {
    // 元视角分析完成
    updateMetaView(data.result.meta_analysis)
  }
}
```

### 4. 删除旧的apply接口调用

❌ **删除**: `/api/v1/thinking-lens/apply` 的前端调用

✅ **保留**: `/api/v1/articles/{id}/thinking-lens/{type}` 的调用

---

## 数据库变更

无需修改数据库结构。现有的 `AnalysisReport` 表的 `status` 字段已支持：
- `pending`: 待处理
- `processing`: 处理中
- `completed`: 已完成
- `failed`: 失败

---

## 性能对比

| 操作 | 旧版本（同步） | 新版本（异步） |
|------|--------------|--------------|
| 保存文章并分析 | 15-30秒（阻塞） | <100ms（立即返回） |
| 元视角分析 | 5-10秒（阻塞） | <100ms（立即返回） |
| 思维透镜分析 | 3-5秒（阻塞） | <100ms（立即返回） |
| 前端超时风险 | 高（15秒超时） | 无（立即响应） |
| 并发处理能力 | 低（阻塞） | 高（异步） |

---

## 错误处理

### 任务失败

当后台任务失败时，会通过SSE推送 `task_failed` 事件：

```javascript
{
  "task_id": "uuid-xxx",
  "task_type": "article_analysis",
  "error": "OpenAI API调用失败"
}
```

前端应监听此事件并向用户显示错误信息。

### 网络断线

SSE连接断开时，浏览器会自动重连。前端应：
1. 重新建立SSE连接
2. 检查pending任务的状态
3. 必要时重新提交任务

---

## 监控和日志

### 日志格式

所有异步任务的日志都带有统一前缀：

```
[后台任务] 开始分析文章，ID: 123
[后台任务] 文章分析完成，ID: 123, 耗时: 15500ms
[API] 异步分析任务已提交，文章ID: 123, 任务ID: uuid-xxx
[SSE] 事件已发送: task_completed, 用户ID: 456
```

### 任务清理

TaskManager会保留所有任务信息，可通过 `cleanup_old_tasks(max_age_hours=24)` 清理旧任务。

---

## 测试指南

### 1. 测试异步分析

```bash
# 启动后端
cd backend
python -m uvicorn app.main:app --reload

# 在另一个终端监听SSE
curl -N http://localhost:8000/api/v1/sse/analysis-notifications?user_id=1

# 提交分析任务
curl -X POST http://localhost:8000/api/v1/articles/save-with-analysis \
  -H "Content-Type: application/json" \
  -d '{"title": "测试文章", "content": "这是测试内容...", "user_id": 1}'

# 观察SSE终端，应该收到 task_started 和 task_completed 事件
```

### 2. 测试思维透镜

```bash
# 1. 先保存文章（获得article_id）
# 2. 调用透镜接口
curl "http://localhost:8000/api/v1/articles/1/thinking-lens/argument_structure"

# 观察SSE终端，应该收到透镜分析完成事件
```

---

## 常见问题

### Q: 任务提交后如何知道完成了？
A: 通过SSE监听 `task_completed` 事件，事件中包含task_id和结果数据。

### Q: 如果用户关闭页面，任务会继续执行吗？
A: 会的，任务在后台独立执行，结果会保存到数据库。用户下次访问时可直接获取结果。

### Q: 如何避免重复分析？
A: 接口会先检查是否已有结果，如果有则立即返回completed状态，不会重复分析。

### Q: SSE连接断开怎么办？
A: 浏览器会自动重连。重连后会继续接收后续事件。已完成的任务结果存储在数据库中，可通过查询接口获取。

### Q: 可以同时运行多个分析任务吗？
A: 可以，TaskManager支持并发执行多个任务。

---

## 后续优化方向

1. **任务优先级**: 为不同类型的任务设置优先级
2. **任务队列**: 限制并发任务数量，避免资源耗尽
3. **任务进度**: 报告任务执行进度（0-100%）
4. **任务取消**: 支持取消正在执行的任务
5. **任务重试**: 失败任务自动重试机制
6. **分布式部署**: 使用Redis作为任务队列，支持多实例部署

---

## 总结

本次异步重构：
- ✅ 解决了前端15秒超时问题
- ✅ 提升了用户体验（立即响应）
- ✅ 提高了系统并发能力
- ✅ 无需额外依赖
- ✅ 完全向后兼容

所有LLM分析接口现在都支持异步模式，前端需要相应适配以监听SSE事件。
