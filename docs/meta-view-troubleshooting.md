# 元视角模式 - 故障排查指南

## 🔍 问题：点击开启元视角后看不到面板

### 修复内容 ✅

已修复 `MetaViewTrigger.vue` 的逻辑问题：
- ✅ 分析成功后自动调用 `toggleMetaView()` 打开面板
- ✅ 分析失败时也打开面板以显示错误信息

### 排查步骤

#### 1. 检查浏览器控制台（F12）

打开浏览器开发者工具，查看控制台是否有错误信息：

**预期日志**：
```
✅ 元信息分析完成: {article_id}
```

**可能的错误**：
```javascript
❌ 元信息分析失败: [错误信息]
```

#### 2. 检查后端服务是否运行

确认后端服务在 `http://localhost:8000` 运行：

```bash
cd backend
python -m app.main
```

**测试 API**：
```bash
curl http://localhost:8000/docs
```

应该能看到 FastAPI 的 Swagger 文档页面。

#### 3. 检查环境变量配置

确认后端 `.env` 文件包含必要配置：

```bash
# backend/.env
OPENAI_API_KEY=sk-...                    # 必需
OPENAI_BASE_URL=                         # 可选
DATABASE_URL=sqlite:///./insightreader_v2.db
DEFAULT_MODEL=gpt-4o
```

#### 4. 检查数据库表是否存在

如果数据库表未创建，API 会报错。运行迁移：

```bash
cd backend
# 如果有迁移脚本
python -m app.db.migrate

# 或者手动检查表
sqlite3 insightreader_v2.db
.tables
# 应该看到: meta_analyses, thinking_lens_results, meta_view_feedback
```

#### 5. 检查网络请求

在浏览器开发者工具的 **Network** 标签中：

1. 点击元视角按钮
2. 查看是否有请求发送到 `/api/v1/meta-analysis/analyze`
3. 检查请求状态码：
   - **200**: 成功
   - **422**: 请求参数错误
   - **500**: 服务器错误
   - **CORS错误**: 跨域配置问题

#### 6. 测试 API 端点

使用 curl 或 Postman 直接测试 API：

```bash
curl -X POST http://localhost:8000/api/v1/meta-analysis/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "article_id": 12345,
    "title": "测试文章",
    "author": "测试作者",
    "publish_date": "2025-01-01T00:00:00",
    "full_text": "这是一篇测试文章的内容，用于验证元信息分析功能是否正常工作。",
    "language": "zh"
  }'
```

**预期响应**：
```json
{
  "status": "success",
  "meta_analysis": {
    "id": 1,
    "article_id": 12345,
    "author_intent": {...},
    "timeliness_score": 0.5,
    ...
  }
}
```

## 🐛 常见错误及解决方案

### 错误 1: CORS 跨域错误

**症状**：
```
Access to fetch at 'http://localhost:8000/api/v1/meta-analysis/analyze'
from origin 'http://localhost:3000' has been blocked by CORS policy
```

**解决方案**：
检查后端 `main.py` 的 CORS 配置：

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 或 ["*"] 开发环境
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 错误 2: OpenAI API 密钥无效

**症状**：
```
❌ 元信息分析失败: Incorrect API key provided
```

**解决方案**：
1. 检查 `.env` 文件中的 `OPENAI_API_KEY`
2. 确认密钥格式正确（sk-...）
3. 测试密钥是否有效

### 错误 3: 数据库表不存在

**症状**：
```
sqlalchemy.exc.OperationalError: no such table: meta_analyses
```

**解决方案**：
手动创建表（如果没有迁移脚本）：

```sql
-- 在 SQLite 中运行
CREATE TABLE meta_analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER UNIQUE NOT NULL,
    author_intent JSON NOT NULL,
    timeliness_score FLOAT NOT NULL,
    timeliness_analysis JSON NOT NULL,
    bias_analysis JSON NOT NULL,
    knowledge_gaps JSON NOT NULL,
    raw_llm_response TEXT,
    analysis_quality JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE thinking_lens_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    meta_analysis_id INTEGER NOT NULL,
    lens_type VARCHAR(50) NOT NULL,
    highlights JSON NOT NULL,
    annotations JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (meta_analysis_id) REFERENCES meta_analyses(id)
);

CREATE TABLE meta_view_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    meta_analysis_id INTEGER,
    lens_result_id INTEGER,
    feedback_type VARCHAR(50) NOT NULL,
    rating INTEGER,
    feedback_data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (meta_analysis_id) REFERENCES meta_analyses(id),
    FOREIGN KEY (lens_result_id) REFERENCES thinking_lens_results(id)
);
```

### 错误 4: 面板不显示（即使请求成功）

**症状**：
- API 请求返回 200
- 控制台显示 "✅ 元信息分析完成"
- 但面板不出现

**解决方案**：
1. 检查 `isMetaViewActive` 状态：
   ```javascript
   // 在浏览器控制台执行
   window.$nuxt.$state.data['meta-view-active']
   ```
   应该为 `true`

2. 检查 z-index 冲突：
   - 面板 z-index: `z-40`
   - 触发按钮 z-index: `z-50`
   - 确保没有其他元素遮挡

3. 强制刷新浏览器缓存（Ctrl+Shift+R）

### 错误 5: LLM 响应格式错误

**症状**：
```
❌ 元信息分析失败: LLM 输出缺少必需字段
```

**解决方案**：
1. 检查 OpenAI API 是否返回 JSON 格式
2. 验证提示词中要求的输出格式
3. 尝试增加 `max_tokens` 参数

## 🔧 调试技巧

### 启用详细日志

在 `useMetaView.ts` 中添加调试日志：

```typescript
const analyzeArticle = async (...) => {
  console.log('🔍 开始分析文章:', { articleId, title })
  isAnalyzing.value = true
  console.log('📊 isAnalyzing =', isAnalyzing.value)

  try {
    const response = await $fetch(...)
    console.log('📦 API 响应:', response)

    metaAnalysisData.value = response.meta_analysis
    console.log('💾 数据已保存:', metaAnalysisData.value)

    return response.meta_analysis
  } catch (error) {
    console.error('💥 详细错误:', error)
    throw error
  }
}
```

### 检查 Vue DevTools

安装 Vue DevTools 浏览器扩展，查看组件状态：

1. 找到 `MetaInfoPanel` 组件
2. 检查 props 和 state
3. 确认 `isMetaViewActive` 和 `metaAnalysisData` 的值

### 模拟数据测试

临时硬编码数据测试 UI：

```typescript
// 在 MetaInfoPanel.vue 中
onMounted(() => {
  // 测试数据
  metaAnalysisData.value = {
    id: 1,
    article_id: 12345,
    author_intent: {
      primary: 'inform',
      confidence: 0.9,
      description: '测试描述',
      indicators: ['测试指标']
    },
    // ... 其他字段
  }
  isMetaViewActive.value = true
})
```

## ✅ 验证清单

完成以下检查确保功能正常：

- [ ] 后端服务运行在 http://localhost:8000
- [ ] 前端服务运行在 http://localhost:3000
- [ ] `.env` 文件配置正确（OPENAI_API_KEY）
- [ ] 数据库表已创建
- [ ] 浏览器控制台无 CORS 错误
- [ ] 点击按钮后看到加载动画
- [ ] 网络请求成功返回 200
- [ ] 控制台显示 "✅ 元信息分析完成"
- [ ] `isMetaViewActive` 状态变为 true
- [ ] 面板从右侧滑入
- [ ] 卡片正确显示分析结果

## 📞 仍然有问题？

如果以上步骤都无法解决问题，请提供：

1. **浏览器控制台完整日志**（包括错误和警告）
2. **Network 标签的请求详情**（请求/响应）
3. **后端服务器日志**
4. **环境信息**：
   - Node.js 版本
   - Python 版本
   - 操作系统
   - 浏览器版本

---

**最后更新**: 2025年
**适用版本**: Meta-View v1.1
