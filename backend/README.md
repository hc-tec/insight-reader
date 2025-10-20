# InsightReader 后端 API

基于 FastAPI 构建的轻量级后端服务,为 InsightReader 提供 AI 驱动的上下文智能探针功能。

## 特性

- ✅ **极简架构**: 无数据库,无认证,专注核心功能
- ✅ **AI 驱动**: 集成 OpenAI GPT-4o,智能洞察生成
- ✅ **流式响应**: SSE 实现打字机效果,优化用户体验
- ✅ **成本优化**: 智能模型选择,降低 95% 成本
- ✅ **开箱即用**: 一键启动,快速开发

## 技术栈

- **框架**: FastAPI 0.110+
- **AI**: OpenAI API (GPT-4o / GPT-4o-mini)
- **Python**: 3.11+

## 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制配置文件
cp .env.example .env

# 编辑 .env 文件,填写你的 OpenAI API Key
# OPENAI_BASE_URL=https://api.openai.com/v1
# OPENAI_API_KEY=sk-your-api-key-here
```

### 3. 启动服务

```bash
# 开发模式（支持热重载）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 4. 访问 API 文档

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/health

## API 使用示例

### 生成洞察 (流式)

```bash
curl -X POST http://localhost:8000/api/v1/insights/generate \
  -H "Content-Type: application/json" \
  -d '{
    "selected_text": "康德的绝对命令",
    "context": "在伦理学中，康德的绝对命令是一个核心概念。它要求我们的行为准则能够成为普遍法则。",
    "intent": "explain"
  }'
```

**响应** (SSE 流):
```
data: {"type": "start", "request_id": "req_1234567890"}

data: {"type": "delta", "content": "康德"}

data: {"type": "delta", "content": "的绝对命令"}

...

data: {"type": "complete", "full_content": "...", "metadata": {...}}
```

## 项目结构

```
backend/
├── app/
│   ├── main.py              # FastAPI 应用入口
│   ├── config.py            # 配置管理
│   ├── api/                 # API 路由
│   │   └── insights.py      # 洞察生成 API
│   ├── services/            # 业务逻辑
│   │   └── ai_service.py    # AI 服务
│   ├── schemas/             # Pydantic 模型
│   │   └── insight.py       # 数据模型
│   └── utils/               # 工具函数
│       └── prompt_templates.py  # Prompt 模板
├── requirements.txt         # Python 依赖
├── .env.example             # 环境变量示例
└── README.md                # 本文档
```

## 意图类型

API 支持以下三种意图类型：

| 意图 | 说明 | 使用场景 |
|------|------|---------|
| `explain` | 解释概念 | 用户选中术语、概念 |
| `analyze` | 分析论证 | 用户选中论述、观点 |
| `counter` | 反方观点 | 用户想了解不同视角 |

## 模型选择策略

系统会根据意图和文本长度自动选择合适的模型：

- **简单解释** (< 10 字) → GPT-4o-mini (快速便宜)
- **复杂分析** → GPT-4o (强大准确)

## 环境变量说明

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `OPENAI_BASE_URL` | OpenAI API 基础 URL | https://api.openai.com/v1 |
| `OPENAI_API_KEY` | OpenAI API 密钥 | 必填 |
| `MAX_CONTEXT_LENGTH` | 最大上下文长度 | 2000 |
| `DEFAULT_MODEL` | 默认模型 | gpt-4o |
| `SIMPLE_MODEL` | 简单任务模型 | gpt-4o-mini |
| `MAX_TOKENS` | 最大生成 tokens | 1000 |
| `TEMPERATURE` | 生成温度 | 0.7 |
| `CORS_ORIGINS` | 允许的跨域来源 | ["http://localhost:3000"] |

## 开发指南

### 添加新的意图类型

1. 在 `app/utils/prompt_templates.py` 中添加新的系统提示词
2. 在 `PromptTemplates.get_user_prompt()` 中添加对应的用户提示词逻辑
3. 更新 `app/schemas/insight.py` 中的 `intent` 验证规则

### 调试技巧

```bash
# 启用 DEBUG 模式
DEBUG=true uvicorn app.main:app --reload

# 查看日志
tail -f app.log
```

## 部署

### Docker 部署

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Railway / Render 部署

1. 连接 GitHub 仓库
2. 设置环境变量 `OPENAI_API_KEY` 和 `OPENAI_BASE_URL`
3. 启动命令: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## 性能优化

- **流式响应**: 降低首字节时间 (TTFB)
- **模型选择**: 根据任务复杂度选择模型
- **无数据库**: 减少 I/O 开销
- **异步处理**: FastAPI 原生异步支持

## 成本估算

假设每篇文章划词 5 次:

- 使用 GPT-4o-mini: ~¥0.01/篇
- 使用 GPT-4o: ~¥0.15/篇
- 混合使用: ~¥0.08/篇

## 常见问题

### Q: 如何获取 OpenAI API Key?
A: 访问 https://platform.openai.com/ 注册并创建 API Key

### Q: 支持其他 AI 模型吗?
A: MVP 版本支持 OpenAI GPT-4o/mini,后续可扩展支持 Claude、Gemini 等

### Q: 流式响应卡顿怎么办?
A: 检查网络连接,或在配置中降低 `TEMPERATURE` 值

### Q: 如何限流?
A: 可以集成 `slowapi` 库实现请求限流

## 许可证

MIT License

## 联系方式

- **项目**: InsightReader
- **版本**: 1.0.0-mvp
- **文档**: [设计文档](../2-设计方案.md)
