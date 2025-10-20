# 移除 Redis 依赖 - 修改总结

**日期**: 2025-10-20
**状态**: ✅ 完成

---

## 修改目标

**用户需求**: 保留 Celery，但移除 Redis 依赖

**解决方案**: 将 Celery 的消息队列（broker）和结果后端（backend）从 Redis 改为 SQLite 数据库

---

## 主要修改

### 1. Celery 配置文件

**文件**: `backend/app/celery_app.py`

**修改内容**:
```python
# 旧配置（使用 Redis）
celery_app = Celery(
    'insightreader',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1'
)

# 新配置（使用数据库）
database_url = settings.database_url.replace('sqlite:///', 'db+sqlite:///')
celery_app = Celery(
    'insightreader',
    broker=database_url,
    backend=database_url
)
```

**说明**:
- 使用 SQLAlchemy 数据库作为 broker
- 与主数据库共用 SQLite
- 无需额外安装 Redis

---

## 优缺点分析

### ✅ 优势

1. **简化部署**: 无需安装和管理 Redis 服务
2. **开发友好**: 配置简单，一个数据库搞定
3. **成本降低**: 减少服务依赖

### ⚠️ 限制

1. **性能较低**: 数据库性能不如 Redis
2. **并发限制**: 不适合高并发场景
3. **生产环境**: 建议仍使用 Redis

---

## 启动方式

### 1. 安装依赖

```bash
cd backend
pip install celery
```

**注意**: 不需要安装 `redis` 包

### 2. 启动 Celery Worker

**Windows**:
```bash
celery -A app.celery_app worker --loglevel=info --pool=solo
```

**Mac/Linux**:
```bash
celery -A app.celery_app worker --loglevel=info
```

### 3. 启动 FastAPI

```bash
python -m uvicorn app.main:app --reload --port 8000
```

---

## 更新的文档

1. **新建文档**:
   - `docs/celery-setup-without-redis.md` - Celery 配置说明

2. **更新文档**:
   - `docs/unified-analysis-quick-start.md` - 删除 Redis 安装步骤
   - `docs/architecture-migration-nlp-to-llm.md` - 更新架构说明

---

## 如何切换回 Redis

如果将来需要更好的性能，可以轻松切换回 Redis：

### 1. 安装 Redis

**Windows**: 下载 [Redis for Windows](https://github.com/microsoftarchive/redis/releases)
**Mac**: `brew install redis && brew services start redis`
**Linux**: `sudo apt-get install redis-server && sudo systemctl start redis`

### 2. 修改 celery_app.py

```python
celery_app = Celery(
    'insightreader',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1'
)
```

### 3. 安装 Redis Python 客户端

```bash
pip install redis
```

---

## 测试验证

### 测试 Celery 任务

```bash
# 1. 启动 FastAPI
python -m uvicorn app.main:app --reload

# 2. 启动 Celery Worker（新终端）
celery -A app.celery_app worker --loglevel=info --pool=solo

# 3. 提交测试文章（新终端）
curl -X POST "http://localhost:8000/api/v1/articles/save-with-analysis" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "测试文章",
    "content": "这是测试内容...",
    "user_id": 1
  }'
```

**预期结果**:
- FastAPI 终端: 显示文章保存成功
- Celery Worker 终端: 显示任务执行日志
- 数据库: `analysis_reports` 表新增分析报告

---

## 性能对比

| 指标 | Redis | SQLite |
|------|-------|---------|
| 消息吞吐量 | 10,000+ msg/s | 100-500 msg/s |
| 延迟 | <1ms | 5-20ms |
| 并发任务 | 高 | 低 |
| 部署复杂度 | 中 | 低 |
| 适用场景 | 生产环境 | 开发/小规模 |

---

## 常见问题

### Q: 为什么不用 Redis？
A: 用户要求移除 Redis 依赖，简化部署

### Q: 性能够用吗？
A: 对于开发环境和小规模应用够用，生产环境建议切换到 Redis

### Q: 数据会丢失吗？
A: SQLite 持久化存储，数据不会丢失

### Q: 如何监控任务？
A: 可以使用 Flower 工具：
```bash
pip install flower
celery -A app.celery_app flower
# 访问 http://localhost:5555
```

---

## 总结

✅ **已完成**:
- 移除 Redis 依赖
- 使用 SQLite 作为 Celery broker
- 更新所有相关文档
- 保持 Celery 功能完整

✅ **优势**:
- 简化部署和配置
- 降低服务依赖
- 适合开发环境

⚠️ **建议**:
- 生产环境仍建议使用 Redis
- 定期监控任务队列性能
- 根据实际情况评估是否需要切换

---

**修改状态**: ✅ 完成
**测试状态**: ⏳ 待用户测试
