# 示例文章功能使用指南

## 📖 功能概述

示例文章系统允许管理员标记特定文章作为公开示例，**任何人（包括未登录用户）都可以查看这些示例文章和完整的AI分析结果**。

### ✨ 核心特性

1. **公开访问** - 无需登录即可查看
2. **完整分析** - 展示 Sparks、深度洞察、元视角等所有分析
3. **引导注册** - 通过优质示例吸引用户注册
4. **易于管理** - 管理员可轻松添加/删除示例

---

## 🚀 快速开始

### 步骤1: 数据库迁移

首次使用需要执行数据库迁移：

\`\`\`bash
cd backend
python -m app.db.migrate_add_demo_fields
\`\`\`

这会添加以下字段：
- `is_demo` (BOOLEAN) - 标记是否为示例文章
- `demo_order` (INTEGER) - 控制展示顺序

**回滚迁移**（如需要）：
\`\`\`bash
python -m app.db.migrate_add_demo_fields rollback
\`\`\`

### 步骤2: 标记示例文章

使用管理员 API 标记文章为示例：

\`\`\`http
POST /api/v1/admin/demo/articles/{article_id}/mark
Authorization: Bearer <admin_jwt_token>
Content-Type: application/json

{
  "demo_order": 1,
  "pregenerate_analysis": true
}
\`\`\`

**参数说明：**
- `demo_order`: 展示顺序（可选，数字越小越靠前）
- `pregenerate_analysis`: 是否立即预生成所有分析（推荐 `true`）

### 步骤3: 访问示例

访问以下页面查看示例：
- **列表页**: `http://localhost:3000/demo`
- **详情页**: `http://localhost:3000/demo/{article_id}`

---

## 🔐 管理员权限配置

### 设置管理员

编辑 `backend/app/api/admin_demo.py`：

\`\`\`python
# 第 38 行附近
ADMIN_EMAILS = [
    "admin@insightreader.com",
    "your-email@example.com",  # 添加你的邮箱
]
\`\`\`

**⚠️ 生产环境最佳实践：**
- 使用环境变量存储管理员列表
- 或使用数据库 `users` 表添加 `is_admin` 字段

---

## 📡 API 端点文档

### 公开API（无需认证）

#### 1. 获取示例文章列表
\`\`\`http
GET /api/v1/public/demo/articles?limit=10&offset=0
\`\`\`

**响应：**
\`\`\`json
{
  "total": 5,
  "articles": [
    {
      "id": 1,
      "title": "AI如何改变世界",
      "author": "张三",
      "word_count": 3500,
      "demo_order": 1,
      "has_analysis": true,
      "has_meta_analysis": true,
      "insight_count": 12
    }
  ]
}
\`\`\`

#### 2. 获取示例文章详情
\`\`\`http
GET /api/v1/public/demo/articles/{article_id}
\`\`\`

**响应：**
\`\`\`json
{
  "id": 1,
  "title": "...",
  "content": "...",
  "analysis_report": {
    "sparks": [...],
    "deep_insights": [...],
    "follow_up_questions": [...]
  },
  "meta_analysis": {
    "meta_insights": [...]
  }
}
\`\`\`

#### 3. 获取 Sparks
\`\`\`http
GET /api/v1/public/demo/articles/{article_id}/sparks
\`\`\`

#### 4. 获取深度洞察
\`\`\`http
GET /api/v1/public/demo/articles/{article_id}/insights
\`\`\`

#### 5. 获取元视角分析
\`\`\`http
GET /api/v1/public/demo/articles/{article_id}/meta
\`\`\`

---

### 管理员API（需要管理员权限）

#### 1. 标记为示例
\`\`\`http
POST /api/v1/admin/demo/articles/{article_id}/mark
Authorization: Bearer <token>

{
  "demo_order": 1,
  "pregenerate_analysis": true
}
\`\`\`

#### 2. 取消示例标记
\`\`\`http
DELETE /api/v1/admin/demo/articles/{article_id}/unmark
Authorization: Bearer <token>
\`\`\`

#### 3. 更新展示顺序
\`\`\`http
PUT /api/v1/admin/demo/articles/{article_id}/order?order=2
Authorization: Bearer <token>
\`\`\`

#### 4. 预生成分析
\`\`\`http
POST /api/v1/admin/demo/articles/{article_id}/pregenerate?force_regenerate=false
Authorization: Bearer <token>
\`\`\`

**响应：**
\`\`\`json
{
  "task_id": "abc-123",
  "article_id": 1,
  "status": "processing",
  "message": "预生成任务已提交..."
}
\`\`\`

#### 5. 查看所有示例文章（管理员视图）
\`\`\`http
GET /api/v1/admin/demo/articles
Authorization: Bearer <token>
\`\`\`

---

## 🎨 前端页面

### 1. 示例文章列表页
**路径**: `/demo`
**组件**: `pages/demo/index.vue`

**特性：**
- 展示所有示例文章卡片
- 显示文章统计信息（字数、洞察数等）
- 引导未登录用户注册
- 响应式设计

### 2. 示例文章详情页
**路径**: `/demo/:id`
**组件**: `pages/demo/[id].vue`

**特性：**
- 完整展示文章内容
- AI分析结果（Sparks、深度洞察、追问）
- 元视角分析
- 示例标识条
- 底部注册引导

### 3. 首页入口
**组件**: `components/ArticleInput.vue`

在"快速开始"区域添加了醒目的**"查看完整示例文章"**按钮。

---

## 🛠️ 技术实现细节

### 后端架构

\`\`\`
backend/
├── app/
│   ├── models/models.py              # Article 模型（新增字段）
│   ├── api/
│   │   ├── public_demo.py           # 公开API（无需认证）
│   │   └── admin_demo.py            # 管理员API
│   ├── services/
│   │   └── demo_pregeneration_service.py  # 预生成服务
│   └── db/
│       └── migrate_add_demo_fields.py  # 数据库迁移
\`\`\`

### 前端架构

\`\`\`
frontend/
├── app/
│   ├── pages/
│   │   └── demo/
│   │       ├── index.vue            # 列表页
│   │       └── [id].vue             # 详情页
│   ├── composables/
│   │   └── useDemoArticles.ts      # API 调用封装
│   └── components/
│       └── ArticleInput.vue         # 添加入口按钮
\`\`\`

### 最佳实践

#### 1. 数据库设计
- ✅ 使用索引优化查询性能
- ✅ 使用组合索引（is_demo + demo_order）
- ✅ 使用部分索引（WHERE is_demo = TRUE）

#### 2. API设计
- ✅ 公开API与认证API分离
- ✅ 使用 Pydantic 模型验证响应
- ✅ 统一错误处理
- ✅ 使用 joinedload 避免 N+1 查询

#### 3. 性能优化
- ✅ 预生成所有分析（避免实时计算）
- ✅ 使用异步任务（TaskManager）
- ✅ 可选：添加 Redis 缓存层

#### 4. 安全性
- ✅ 验证文章必须是示例文章
- ✅ 管理员权限检查
- ✅ 详细的操作日志

---

## 📊 使用示例流程

### 管理员添加示例文章

1. **上传文章** - 正常上传一篇文章到系统
2. **获取文章ID** - 记录文章ID（如 `123`）
3. **标记为示例**:
   \`\`\`bash
   curl -X POST "http://localhost:8000/api/v1/admin/demo/articles/123/mark" \\
     -H "Authorization: Bearer <token>" \\
     -H "Content-Type: application/json" \\
     -d '{
       "demo_order": 1,
       "pregenerate_analysis": true
     }'
   \`\`\`
4. **等待预生成完成** - 后台任务会自动生成所有分析
5. **验证** - 访问 `http://localhost:3000/demo` 查看

### 用户访问示例

1. **访问首页** - `http://localhost:3000/`
2. **点击**"查看完整示例文章"按钮
3. **浏览列表** - 查看所有示例文章
4. **点击文章** - 查看完整内容和AI分析
5. **注册** - 被优质示例吸引，点击注册

---

## 🐛 常见问题

### Q1: 示例文章列表为空？
**A:** 确保已执行数据库迁移，并且至少标记了一篇文章为示例。

### Q2: 预生成分析失败？
**A:** 检查后端日志，确保：
- OpenAI API 配置正确
- 文章内容不为空
- 后台任务正常运行

### Q3: 非管理员如何标记示例？
**A:** 只有管理员邮箱才能使用管理员API。请联系管理员或修改代码中的 `ADMIN_EMAILS` 列表。

### Q4: 如何取消示例标记？
**A:**
\`\`\`bash
curl -X DELETE "http://localhost:8000/api/v1/admin/demo/articles/123/unmark" \\
  -H "Authorization: Bearer <token>"
\`\`\`

### Q5: 示例文章会被删除吗？
**A:** 不会。取消示例标记只是将 `is_demo` 设为 `FALSE`，文章本身不会被删除，分析结果也会保留。

---

## 📈 后续优化建议

1. **缓存层** - 添加 Redis 缓存示例文章数据
2. **访问统计** - 记录示例文章访问量，帮助优化示例选择
3. **管理界面** - 开发可视化的管理后台
4. **自动刷新** - 定期自动更新示例文章的分析结果
5. **多语言** - 支持不同语言的示例文章
6. **分类标签** - 为示例文章添加分类（科技、财经、文化等）

---

## 📝 更新日志

### v1.0.0 (2025-10-23)
- ✅ 实现公开示例文章系统
- ✅ 添加管理员API
- ✅ 添加预生成服务
- ✅ 完成前端页面（列表 + 详情）
- ✅ 添加首页入口

---

## 📞 技术支持

如有问题，请查看：
- **后端日志**: 查看 `backend/` 目录下的运行日志
- **前端控制台**: 打开浏览器开发者工具查看错误
- **API 文档**: 访问 `http://localhost:8000/docs` 查看 Swagger 文档
