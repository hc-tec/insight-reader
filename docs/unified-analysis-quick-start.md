# 统一深度分析引擎 - 快速启动指南

## 环境准备

### 安装 Python 依赖

```bash
cd backend
pip install celery
```

**注意**: 本项目使用 SQLite 数据库作为 Celery 的消息队列，无需安装 Redis。详见 `celery-setup-without-redis.md`。

---

## 启动服务

### 方案 A: 全功能启动（推荐）

需要 **3 个终端窗口**：

#### 终端 1: 启动 FastAPI

```bash
cd D:\AIProject\InsightReader\backend
python -m uvicorn app.main:app --reload --port 8000
```

#### 终端 2: 启动 Celery Worker

```bash
cd D:\AIProject\InsightReader\backend
celery -A app.celery_app worker --loglevel=info --pool=solo
```

> **注意**: Windows 下需要使用 `--pool=solo` 参数

#### 终端 3: 启动前端

```bash
cd D:\AIProject\InsightReader\frontend
npm run dev
```

### 方案 B: 简化启动（仅测试 API）

如果只想测试 API，不需要异步分析：

```bash
# 只启动 FastAPI
cd D:\AIProject\InsightReader\backend
python -m uvicorn app.main:app --reload
```

---

## 测试流程

### 1. 保存文章并触发分析

**API 调用**:

```bash
curl -X POST "http://localhost:8000/api/v1/articles/save-with-analysis" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "测试文章",
    "content": "元信息是一个重要的概念。它指的是关于信息的信息。批判性思维帮助我们理解元信息。元信息思维是高效学习的核心能力。研究表明，具备元信息意识的学生学习效率提升40%。",
    "user_id": 1
  }'
```

**响应示例**:

```json
{
  "article": {
    "id": 123,
    "is_new": true
  },
  "analysis": {
    "status": "pending",
    "task_id": "abc-123-def"
  }
}
```

### 2. 连接 SSE 接收通知

**浏览器**:

```
http://localhost:8000/api/v1/sse/analysis-notifications?user_id=1
```

你会看到：

```
event: connected
data: {"user_id": 1, "timestamp": 1698765432.123}

event: heartbeat
data: {"timestamp": 1698765462.456}

event: analysis_complete
data: {"article_id": 123, "timestamp": 1698765475.789}
```

### 3. 查询分析状态

```bash
curl "http://localhost:8000/api/v1/articles/123/analysis-status"
```

**响应**:

```json
{
  "status": "completed",  // pending, processing, completed, failed
  "progress": 100,
  "error_message": null
}
```

### 4. 获取分析报告

```bash
curl "http://localhost:8000/api/v1/articles/123/analysis-report"
```

**响应**:

```json
{
  "report_data": {
    "meta_info": { ... },
    "concept_sparks": [
      {
        "text": "元信息",
        "sentence_index": 0,
        "importance_score": 9,
        "explanation_hint": "用一个日常生活中的例子解释'元信息'的概念。",
        "dom_path": "#sentence-0"
      }
    ],
    "summary": "...",
    "tags": ["概念", "学习"]
  },
  "metadata": {
    "model_used": "gpt-4o",
    "tokens_used": 1250,
    "processing_time_ms": 15000,
    "completed_at": "2025-10-20T10:30:00Z"
  }
}
```

---

## 前端集成示例

### 在页面中使用

```vue
<template>
  <div>
    <!-- 文章容器（必须有 ID） -->
    <div id="article-content-container" v-html="renderedContent"></div>

    <!-- 分析状态指示器 -->
    <div v-if="isAnalyzing" class="fixed top-4 right-4">
      <div class="animate-pulse">
        🧠 正在深度分析文章...
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const { renderArticleWithSentenceIds } = useArticleRenderer()
const { connect } = useAnalysisNotifications()
const config = useRuntimeConfig()

// 文章内容
const articleContent = ref('')
const renderedContent = ref('')
const isAnalyzing = ref(false)

// 提交文章
const handleSubmitArticle = async (content: string) => {
  // 1. 渲染带句子 ID 的 HTML
  renderedContent.value = renderArticleWithSentenceIds(content)

  // 2. 保存文章并触发分析
  isAnalyzing.value = true

  const response = await $fetch(`${config.public.apiBase}/api/v1/articles/save-with-analysis`, {
    method: 'POST',
    body: {
      title: '我的文章',
      content: content,
      user_id: 1
    }
  })

  console.log('文章已保存，ID:', response.article.id)

  // 3. SSE 会自动通知分析完成，自动渲染火花
}

// 建立 SSE 连接
onMounted(() => {
  connect()
})
</script>
```

---

## 故障排查

### 问题 1: Celery Worker 无法启动

**错误**: `KeyError: 'allow_pickle'` 或 `ImportError: cannot import name 'soft_unicode'`

**解决**:

```bash
pip install --upgrade celery
```

### 问题 2: Celery 数据库连接失败

**错误**: `OperationalError: unable to open database file`

**解决**:

```bash
# 检查数据库文件路径是否正确
# 确保 backend/insightreader_v2.db 存在
# 如果不存在，运行数据库迁移脚本
```

### 问题 3: SSE 连接断开

**错误**: 浏览器控制台显示 `EventSource failed`

**解决**:

1. 检查用户 ID 是否正确
2. 检查 FastAPI 服务是否运行
3. 查看浏览器 Network 面板的错误详情

### 问题 4: 火花不显示

**可能原因**:

1. ✅ 检查文章容器是否有 `id="article-content-container"`
2. ✅ 检查 `renderArticleWithSentenceIds()` 是否被调用
3. ✅ 检查浏览器控制台是否有错误
4. ✅ 检查分析报告中的 `dom_path` 是否正确

### 问题 5: OpenAI API 调用失败

**错误**: `openai.APIConnectionError`

**解决**:

1. 检查 `backend/app/config.py` 中的 API Key
2. 检查 `openai_base_url` 配置
3. 检查网络连接

---

## 性能优化建议

### 1. Celery Worker 数量

根据服务器性能调整：

```bash
# 单 Worker
celery -A app.celery_app worker --loglevel=info

# 多 Worker（4个并发）
celery -A app.celery_app worker --loglevel=info --concurrency=4
```

### 2. 切换到 Redis（可选）

如需更高性能，可切换到 Redis。详见 `celery-setup-without-redis.md`。

### 3. Nginx 反向代理

SSE 需要禁用缓冲：

```nginx
location /api/v1/sse/ {
    proxy_pass http://localhost:8000;
    proxy_buffering off;
    proxy_cache off;
    proxy_read_timeout 86400;
}
```

---

## 监控与日志

### Celery 任务监控

使用 Flower（Celery 监控工具）：

```bash
pip install flower
celery -A app.celery_app flower
```

访问: `http://localhost:5555`

### 日志查看

**FastAPI 日志**:
```bash
tail -f logs/api.log
```

**Celery 日志**:
```bash
# 在 Celery 启动时会显示在终端
```

---

## 下一步

1. ✅ 测试完整流程
2. ✅ 优化 UI（等待动画、火花卡片）
3. ✅ 添加错误边界
4. ✅ 性能测试
5. ✅ 部署到生产环境

祝您使用愉快！🎉
