# 管理员设置指南

## 📋 概述

InsightReader 支持两种方式设置管理员：
1. **环境变量方式**（✅ 推荐，生产环境最佳实践）
2. **代码修改方式**（快速测试用）

---

## ✅ 方法一：环境变量设置（推荐）

### 步骤 1: 编辑 `.env` 文件

在 `backend/.env` 文件中添加或修改以下内容：

```bash
# ==========================================
# Admin Configuration
# ==========================================

# 管理员邮箱列表（逗号分隔，支持多个）
ADMIN_EMAILS=your-email@example.com,another-admin@example.com
```

**示例：**
```bash
# 单个管理员
ADMIN_EMAILS=admin@insightreader.com

# 多个管理员（逗号分隔）
ADMIN_EMAILS=admin@insightreader.com,john@example.com,jane@example.com
```

### 步骤 2: 重启后端服务

```bash
# 如果后端正在运行，先停止（Ctrl+C）
# 然后重新启动
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 步骤 3: 验证管理员权限

1. **使用管理员邮箱登录**
   - 确保你使用的登录邮箱与 `ADMIN_EMAILS` 中的邮箱一致

2. **测试管理员 API**
   ```bash
   # 获取你的 JWT token（登录后从浏览器控制台或响应中获取）
   curl -X GET "http://localhost:8000/api/v1/admin/demo/articles" \
     -H "Authorization: Bearer <your-jwt-token>"
   ```

3. **期望结果**
   - ✅ 成功：返回示例文章列表
   - ❌ 失败：返回 403 错误 "需要管理员权限"

---

## ⚡ 方法二：代码修改方式（仅用于快速测试）

### 步骤 1: 修改代码

编辑 `backend/app/config.py`，找到第 43 行：

```python
# 管理员配置
admin_emails: str = "admin@insightreader.com"  # 逗号分隔的管理员邮箱列表
```

修改为：

```python
# 管理员配置
admin_emails: str = "your-email@example.com,another-admin@example.com"
```

### 步骤 2: 重启后端

**注意：** 这种方式不推荐用于生产环境，因为：
- ❌ 硬编码在代码中，不安全
- ❌ 需要修改代码并重新部署
- ❌ 难以在不同环境中切换

---

## 🔍 验证管理员身份

### 方式 1: 通过日志查看

启动后端后，尝试访问管理员 API，查看日志：

**成功：**
```
[Admin] 管理员身份验证成功: admin@example.com
```

**失败：**
```
[Admin] 未授权访问尝试: user@example.com (管理员列表: admin@example.com)
```

### 方式 2: 通过 API 测试

使用 Postman 或 curl 测试：

```bash
# 1. 登录获取 token
curl -X POST "http://localhost:8000/api/v1/auth/magic-link" \
  -H "Content-Type: application/json" \
  -d '{"email": "your-admin-email@example.com"}'

# 2. 使用 token 访问管理员 API
curl -X GET "http://localhost:8000/api/v1/admin/demo/articles" \
  -H "Authorization: Bearer <your-token>"
```

**成功响应：**
```json
{
  "total": 0,
  "articles": []
}
```

**失败响应（403）：**
```json
{
  "detail": "需要管理员权限"
}
```

---

## 🎯 访问管理员页面

设置好管理员权限后，你可以通过以下方式访问管理页面：

### 方式 1: 通过用户菜单（推荐）

1. 使用管理员邮箱登录系统
2. 点击右上角的用户头像/菜单
3. 在下拉菜单中会看到 "示例文章管理" 选项（仅管理员可见）
4. 点击即可进入管理页面

**注意：**
- 只有管理员才能看到这个菜单项
- 菜单项有紫色的星星图标，容易识别
- 普通用户看不到此选项

### 方式 2: 直接访问 URL

```
http://localhost:3000/#/admin/demo
```

**注意：** 直接访问 URL 时，后端仍会验证管理员权限。如果不是管理员，API 调用会返回 403 错误。

### 前端配置（可选）

为了在前端正确显示管理员菜单，需要在 `frontend/.env` 中配置：

```bash
# 应与后端 ADMIN_EMAILS 保持一致
NUXT_PUBLIC_ADMIN_EMAILS=admin@insightreader.com,other-admin@example.com
```

**说明：**
- 前端配置用于控制菜单显示（用户体验优化）
- 实际权限验证仍在后端进行（安全保障）
- 两者应保持一致以获得最佳体验

---

## 📝 管理员可用的 API

一旦设置了管理员权限，你可以访问以下 API：

### 1. 标记文章为示例
```http
POST /api/v1/admin/demo/articles/{article_id}/mark
```

### 2. 取消示例标记
```http
DELETE /api/v1/admin/demo/articles/{article_id}/unmark
```

### 3. 更新展示顺序
```http
PUT /api/v1/admin/demo/articles/{article_id}/order?order=1
```

### 4. 预生成分析
```http
POST /api/v1/admin/demo/articles/{article_id}/pregenerate
```

### 5. 查看所有示例文章
```http
GET /api/v1/admin/demo/articles
```

详细 API 文档：`http://localhost:8000/docs#/管理员-示例文章`

---

## 🛠️ 常见问题

### Q1: 我修改了 `.env` 文件，但管理员权限还是不生效？

**A:** 确保你已经重启了后端服务。环境变量只在启动时加载。

```bash
# 停止后端（Ctrl+C）
# 重新启动
uvicorn app.main:app --reload
```

---

### Q2: 如何添加多个管理员？

**A:** 在 `ADMIN_EMAILS` 中使用逗号分隔：

```bash
ADMIN_EMAILS=admin1@example.com,admin2@example.com,admin3@example.com
```

**注意：** 逗号前后可以有空格，系统会自动处理：
```bash
# 这两种写法都可以
ADMIN_EMAILS=admin1@example.com, admin2@example.com, admin3@example.com
ADMIN_EMAILS=admin1@example.com,admin2@example.com,admin3@example.com
```

---

### Q3: 管理员邮箱必须和登录邮箱一致吗？

**A:** 是的。系统会检查当前登录用户的邮箱是否在管理员列表中。

**示例：**
```bash
# .env 文件
ADMIN_EMAILS=admin@example.com

# 只有使用 admin@example.com 登录的用户才有管理员权限
```

---

### Q4: 如何查看当前配置的管理员列表？

**A:** 查看后端日志，当有未授权访问时会显示：

```
[Admin] 未授权访问尝试: user@example.com (管理员列表: admin@example.com, john@example.com)
```

或者直接查看 `.env` 文件中的 `ADMIN_EMAILS` 配置。

---

### Q5: 可以在生产环境中使用代码修改方式吗？

**A:** ❌ 不推荐。生产环境应该使用环境变量方式，因为：
- 更安全（不会提交到代码仓库）
- 更灵活（不同环境可以有不同配置）
- 符合 [12-Factor App](https://12factor.net/config) 最佳实践

---

### Q6: 如果忘记设置管理员邮箱会怎样？

**A:** 如果 `ADMIN_EMAILS` 为空或未设置，访问管理员 API 会返回 500 错误：

```json
{
  "detail": "系统配置错误：未设置管理员"
}
```

同时后端日志会显示：
```
[Admin] 管理员邮箱列表为空，请检查配置
```

---

## 🔒 安全建议

1. **不要将管理员邮箱提交到代码仓库**
   - ✅ 使用 `.env` 文件（已在 `.gitignore` 中）
   - ❌ 不要硬编码在代码中

2. **定期审查管理员列表**
   - 移除离职员工的邮箱
   - 只授予必要的人员管理员权限

3. **使用强密码 / 启用 2FA**
   - 管理员账户应该使用更高安全级别
   - 建议使用 OAuth 登录（Google/GitHub）

4. **记录管理员操作**
   - 系统已自动记录所有管理员操作日志
   - 定期审查日志文件

---

## 📊 配置示例

### 开发环境

```bash
# backend/.env
ADMIN_EMAILS=dev@example.com,test@example.com
```

### 生产环境

```bash
# backend/.env (生产服务器)
ADMIN_EMAILS=admin@company.com,cto@company.com
```

### Docker 环境

```yaml
# docker-compose.yml
services:
  backend:
    environment:
      - ADMIN_EMAILS=admin@example.com,manager@example.com
```

---

## ✅ 快速检查清单

设置管理员前请确认：

**后端配置：**
- [ ] 已复制 `backend/.env.example` 为 `backend/.env`
- [ ] 在 `backend/.env` 中设置了 `ADMIN_EMAILS`
- [ ] 邮箱格式正确（无拼写错误）
- [ ] 多个邮箱使用逗号分隔
- [ ] 已重启后端服务

**前端配置（可选，用于显示管理员菜单）：**
- [ ] 已复制 `frontend/.env.example` 为 `frontend/.env`
- [ ] 在 `frontend/.env` 中设置了 `NUXT_PUBLIC_ADMIN_EMAILS`
- [ ] 前端配置与后端保持一致
- [ ] 已重启前端开发服务器

**验证步骤：**
- [ ] 使用管理员邮箱登录系统
- [ ] 在用户菜单中看到 "示例文章管理" 选项
- [ ] 能成功访问管理页面（`/admin/demo`）
- [ ] 测试了管理员 API 访问权限

---

## 🎓 相关文档

- [示例文章功能使用指南](./DEMO_ARTICLES_GUIDE.md)
- [API 文档](http://localhost:8000/docs)
- [FastAPI 依赖注入](https://fastapi.tiangolo.com/tutorial/dependencies/)
