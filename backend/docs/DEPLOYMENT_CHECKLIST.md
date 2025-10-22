# 异步系统部署检查清单

## 📋 部署前准备

### 1. 数据库迁移

#### 检查当前数据库状态
```bash
cd backend
python -c "from app.db.database import engine; from sqlalchemy import inspect; inspector = inspect(engine); print('Tables:', inspector.get_table_names())"
```

#### 运行迁移脚本（添加新字段）
```bash
python -m app.db.migrate_add_async_fields
```

**预期输出**:
```
============================================================
数据库迁移 - 添加异步重构字段
============================================================

当前数据库: sqlite:///./insightreader_v3.db

[1/2] 添加 analysis_reports.analysis_metadata 字段...
  ✓ analysis_reports.analysis_metadata 添加成功

[2/2] 添加 meta_analyses.generated_title 字段...
  ✓ meta_analyses.generated_title 添加成功

============================================================
[SUCCESS] 数据库迁移完成！
============================================================
```

### 2. 依赖检查

确保已安装所有依赖：
```bash
pip install -r requirements.txt
```

**关键依赖**:
- `sse-starlette==2.0.0` - SSE 支持
- `asyncio` - Python 标准库（无需安装）

### 3. 环境变量配置

检查 `.env` 文件包含：
```bash
# 数据库
STORAGE2_DATABASE_URL=postgresql://...  # 或留空使用 SQLite

# OpenAI API
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1

# JWT
SECRET_KEY=your-secret-key

# CORS（开发环境）
CORS_ORIGINS=["http://localhost:3000"]

# Frontend URL（OAuth 重定向）
FRONTEND_URL=http://localhost:3000  # 或留空（同域部署）
```

---

## 🚀 启动应用

### 开发环境

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**预期输出**:
```
INFO:     Will watch for changes in these directories: ['/path/to/backend']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 生产环境

```bash
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 300 \
  --graceful-timeout 30 \
  --access-logfile - \
  --error-logfile -
```

---

## ✅ 功能测试

### 1. 健康检查

```bash
curl http://localhost:8000/health
```

**预期响应**:
```json
{
  "status": "ok",
  "version": "2.0.0"
}
```

### 2. API 文档

访问: http://localhost:8000/docs

**检查新增的 API 端点**:
- ✅ `/api/v1/tasks/{task_id}/events` (SSE)
- ✅ `/api/v1/tasks/{task_id}/status`
- ✅ `/api/v1/tasks/{task_id}/cancel`
- ✅ `/api/v1/articles/save-with-analysis` (异步)
- ✅ `/api/v1/meta-analysis/analyze` (异步)
- ✅ `/api/v1/thinking-lens/apply` (异步)

### 3. 异步分析测试

#### 提交统一分析任务

```bash
curl -X POST http://localhost:8000/api/v1/articles/save-with-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "title": "测试文章",
    "content": "这是一篇测试文章的内容...",
    "user_id": 1
  }'
```

**预期响应**:
```json
{
  "article": {
    "id": 1,
    "is_new": true
  },
  "analysis": {
    "status": "pending",
    "task_id": "unified_analysis_1"
  }
}
```

#### 订阅 SSE 事件（浏览器测试）

打开浏览器控制台，执行：

```javascript
const taskId = 'unified_analysis_1';
const eventSource = new EventSource(`http://localhost:8000/api/v1/tasks/${taskId}/events`);

eventSource.addEventListener('task_created', (e) => {
  console.log('任务创建:', JSON.parse(e.data));
});

eventSource.addEventListener('task_started', (e) => {
  console.log('任务开始:', JSON.parse(e.data));
});

eventSource.addEventListener('task_completed', (e) => {
  console.log('任务完成:', JSON.parse(e.data));
  eventSource.close();
});

eventSource.addEventListener('task_failed', (e) => {
  console.error('任务失败:', JSON.parse(e.data));
  eventSource.close();
});

eventSource.onerror = (error) => {
  console.error('SSE 错误:', error);
};
```

#### 查询任务状态

```bash
curl http://localhost:8000/api/v1/tasks/unified_analysis_1/status
```

**预期响应**:
```json
{
  "task_id": "unified_analysis_1",
  "status": "processing",
  "progress": 50,
  "message": "正在分析...",
  "result": null,
  "error": null,
  "created_at": "2025-10-21T14:00:00",
  "started_at": "2025-10-21T14:00:01",
  "completed_at": null
}
```

### 4. OAuth 重定向测试

#### Google OAuth
1. 访问: http://localhost:8000/api/v1/auth/google/login
2. 登录后应重定向到: `http://localhost:3000/#/auth/callback?token=...`

#### GitHub OAuth
1. 访问: http://localhost:8000/api/v1/auth/github/login
2. 登录后应重定向到: `http://localhost:3000/#/auth/callback?token=...`

**检查点**:
- ✅ URL 包含 `/#/` (Hash 路由)
- ✅ Token 存在且有效
- ✅ 错误重定向到 `/#/login?error=...`

---

## 🐛 故障排查

### 1. SSE 连接失败

**症状**: EventSource 报错 "Failed to connect"

**检查**:
```bash
# 1. 检查 CORS 配置
curl -I -X OPTIONS http://localhost:8000/api/v1/tasks/test/events \
  -H "Origin: http://localhost:3000"

# 应包含:
# Access-Control-Allow-Origin: http://localhost:3000
# Access-Control-Allow-Credentials: true
```

**解决方案**:
```python
# app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. 任务一直 pending

**症状**: 任务状态不更新

**检查日志**:
```bash
# 查看后端日志
tail -f logs/app.log | grep "TaskManager"

# 或直接查看控制台输出
```

**可能原因**:
1. 后台任务执行失败但未捕获异常
2. 数据库连接问题
3. LLM API 调用失败

**调试**:
```python
# 临时添加更多日志
logger.info(f"[DEBUG] Task {task_id} starting...")
logger.info(f"[DEBUG] Calling LLM API...")
logger.info(f"[DEBUG] LLM response: {response}")
```

### 3. 数据库迁移失败

**症状**: "column already exists" 或 "permission denied"

**解决方案**:

```bash
# 方案 1: 检查字段是否已存在
python -c "
from app.db.database import engine
from sqlalchemy import inspect
inspector = inspect(engine)
cols = inspector.get_columns('analysis_reports')
print([c['name'] for c in cols])
"

# 方案 2: 手动添加字段（PostgreSQL）
psql -U user -d dbname -c "
ALTER TABLE analysis_reports ADD COLUMN IF NOT EXISTS analysis_metadata JSONB;
ALTER TABLE meta_analyses ADD COLUMN IF NOT EXISTS generated_title VARCHAR(500);
"

# 方案 3: 手动添加字段（SQLite）
sqlite3 insightreader_v3.db "
ALTER TABLE analysis_reports ADD COLUMN analysis_metadata TEXT;
ALTER TABLE meta_analyses ADD COLUMN generated_title TEXT;
"
```

### 4. OAuth 重定向到错误路径

**症状**: 重定向到 `/auth/callback` 而不是 `/#/auth/callback`

**检查**:
```python
# app/api/auth.py
# 确保包含此代码:
base_url = settings.frontend_url if settings.frontend_url else ""
redirect_url = f"{base_url}/#/auth/callback?token={access_token}"
```

**测试**:
```bash
# 检查重定向 URL
curl -I http://localhost:8000/api/v1/auth/google/login
# 应重定向到 Google OAuth
```

---

## 📊 性能监控

### 1. 任务队列大小

```python
# 添加监控端点
@app.get("/api/v1/admin/tasks/stats")
async def get_task_stats():
    return {
        "total_tasks": len(task_manager.tasks),
        "pending": len([t for t in task_manager.tasks.values() if t.status == 'pending']),
        "processing": len([t for t in task_manager.tasks.values() if t.status == 'processing']),
        "completed": len([t for t in task_manager.tasks.values() if t.status == 'completed']),
        "failed": len([t for t in task_manager.tasks.values() if t.status == 'failed'])
    }
```

### 2. SSE 连接数

```bash
# 查看活跃连接
netstat -an | grep :8000 | grep ESTABLISHED | wc -l
```

### 3. 数据库连接池

```python
# 检查连接池状态
from app.db.database import engine
print(f"Pool size: {engine.pool.size()}")
print(f"Checked out: {engine.pool.checkedout()}")
```

---

## 🔒 安全检查

### 1. 环境变量保护

```bash
# 确保敏感信息不在版本控制中
cat .gitignore | grep .env
# 应包含: .env
```

### 2. CORS 配置

```python
# 生产环境 CORS 配置
CORS_ORIGINS=["https://yourdomain.com"]  # 不要用 "*"
```

### 3. JWT Secret

```bash
# 确保使用强 Secret Key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## ✅ 部署清单

### 部署前
- [ ] 运行数据库迁移脚本
- [ ] 检查所有依赖已安装
- [ ] 配置环境变量
- [ ] 测试本地启动

### 部署后
- [ ] 健康检查通过
- [ ] API 文档可访问
- [ ] 异步任务测试通过
- [ ] SSE 连接测试通过
- [ ] OAuth 重定向测试通过
- [ ] 日志输出正常
- [ ] 性能监控正常

### 前端集成
- [ ] 创建 useTaskProgress composable
- [ ] 创建 TaskProgress 组件
- [ ] 更新统一分析调用
- [ ] 更新元分析调用
- [ ] 更新思维透镜调用
- [ ] 端到端测试

---

## 📚 参考文档

- **后端重构指南**: `backend/ASYNC_REFACTORING_GUIDE.md`
- **前端迁移指南**: `FRONTEND_MIGRATION_GUIDE.md`
- **重构总结**: `backend/ASYNC_REFACTORING_SUMMARY.md`
- **数据库配置**: `backend/DATABASE_SETUP.md`

---

## 🎉 部署完成

所有检查项通过后，异步分析系统即可投入使用！

**关键改进**:
- ✅ 无超时限制
- ✅ 实时进度反馈
- ✅ 快速响应 (< 1秒)
- ✅ Hash 路由支持
- ✅ 向后兼容

**监控建议**:
- 定期检查任务队列大小
- 监控 SSE 连接数
- 检查数据库连接池
- 查看错误日志
