# Celery 配置说明（不使用 Redis）

**更新日期**: 2025-10-20

---

## 配置方案

本项目使用 **SQLite 数据库** 作为 Celery 的消息代理（broker）和结果后端（backend），不需要安装 Redis。

### 优势
- ✅ 无需额外安装 Redis 服务
- ✅ 开发环境配置简单
- ✅ 与主数据库共用 SQLite

### 限制
- ⚠️ 性能低于 Redis（适合开发和小规模应用）
- ⚠️ 不推荐用于高并发生产环境

---

## 启动 Celery Worker

### Windows
```bash
cd D:\AIProject\InsightReader\backend
celery -A app.celery_app worker --loglevel=info --pool=solo
```

### Mac/Linux
```bash
cd backend
celery -A app.celery_app worker --loglevel=info
```

---

## 测试 Celery 任务

启动 FastAPI 和 Celery Worker 后，可以测试分析任务：

```bash
# 提交文章并触发分析
curl -X POST "http://localhost:8000/api/v1/articles/save-with-analysis" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "测试文章",
    "content": "这是一篇测试文章内容...",
    "user_id": 1
  }'
```

观察 Celery Worker 终端，应该会看到任务执行日志。

---

## 如果需要切换到 Redis

如果将来需要更好的性能，可以轻松切换到 Redis：

### 1. 安装 Redis

**Windows**: 下载 [Redis for Windows](https://github.com/microsoftarchive/redis/releases)

**Mac**: `brew install redis && brew services start redis`

**Linux**: `sudo apt-get install redis-server && sudo systemctl start redis`

### 2. 修改 celery_app.py

```python
# 改为使用 Redis
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

## 常见问题

### Q: Celery Worker 启动失败
A: 检查数据库文件是否存在，确保路径正确

### Q: 任务一直 pending 不执行
A: 确保 Celery Worker 正在运行，检查终端日志

### Q: 性能问题
A: 考虑切换到 Redis（见上方说明）

---

## 监控 Celery 任务

可以使用 Flower 监控工具：

```bash
pip install flower
celery -A app.celery_app flower
```

访问: `http://localhost:5555`

---

## 总结

当前配置：
- **Broker**: SQLite 数据库
- **Backend**: SQLite 数据库
- **优势**: 无需 Redis，配置简单
- **适用场景**: 开发环境、小规模应用

如需高性能，建议切换到 Redis。
