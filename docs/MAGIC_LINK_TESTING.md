# 🧪 邮箱登录（Magic Link）测试指南

## 📋 测试前准备

### 1. 配置邮件服务

编辑 `backend/.env` 文件：

```bash
# Gmail 示例（推荐用于测试）
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password  # Gmail应用专用密码
MAIL_FROM=your-email@gmail.com
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_TLS=true
MAIL_SSL=false

# Frontend URL
FRONTEND_URL=http://localhost:3000
```

**获取 Gmail 应用专用密码**：
1. 访问 https://myaccount.google.com/security
2. 启用「两步验证」
3. 访问 https://myaccount.google.com/apppasswords
4. 创建新的应用专用密码
5. 将 16 位密码（带空格）复制到 `MAIL_PASSWORD`

### 2. 启动服务

**后端**：
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8882
```

**前端**：
```bash
cd frontend
npm run dev
```

## 🔍 测试步骤

### 测试 1：发送魔法链接

1. **打开登录页面**
   - 访问：http://localhost:3000/login

2. **输入邮箱**
   - 在「邮箱地址」输入框输入你的邮箱
   - 点击「发送登录链接」按钮

3. **查看控制台日志**

   前端控制台应该显示：
   ```
   [Login] 开始发送魔法链接: test@example.com
   [useAuth] 请求魔法链接: test@example.com
   [useAuth] API Base: http://localhost:8882
   [useAuth] 魔法链接请求成功: { message: "魔法链接已发送到你的邮箱", email: "..." }
   [Login] 魔法链接请求结果: { success: true, message: "..." }
   [Login] 魔法链接发送成功
   ```

   后端控制台应该显示：
   ```
   INFO:     127.0.0.1:xxxxx - "POST /api/v1/auth/magic-link/request HTTP/1.1" 200 OK
   ```

4. **检查页面状态**
   - 应该显示绿色的成功提示框
   - 提示「邮件已发送！」
   - 显示「使用其他邮箱」按钮

5. **检查邮箱**
   - 打开你的邮箱
   - 查找来自 InsightReader 的邮件
   - 邮件标题：「登录 InsightReader - 魔法链接」

### 测试 2：验证魔法链接

1. **点击邮件中的登录按钮**
   - 或复制链接到浏览器

2. **查看验证页面**
   - 自动跳转到：http://localhost:3000/auth/magic?token=xxx
   - 显示「验证中...」加载状态

3. **查看控制台日志**

   前端控制台应该显示：
   ```
   [Magic] 收到 token: xxx...
   [Magic] 开始验证魔法链接
   [useAuth] 验证魔法链接, token: xxx...
   [useAuth] 验证 URL: http://localhost:8882/api/v1/auth/magic-link/verify
   [useAuth] 验证成功，用户信息: { id: 1, email: "...", ... }
   [Magic] 验证结果: { success: true, user: {...} }
   [Magic] 验证成功，准备跳转
   ```

   后端控制台应该显示：
   ```
   INFO:     127.0.0.1:xxxxx - "GET /api/v1/auth/magic-link/verify?token=xxx HTTP/1.1" 200 OK
   ```

4. **检查页面状态**
   - 显示绿色的成功图标
   - 提示「登录成功！」
   - 1.5秒后自动跳转到首页

5. **检查登录状态**
   - 跳转到首页：http://localhost:3000/
   - localStorage 中应该有：
     - `insightreader_token`：JWT token
     - `insightreader_user`：用户信息
   - 页面右上角显示用户头像或邮箱

## ⚠️ 常见问题排查

### 问题 1：点击按钮没有反应

**检查步骤**：
1. 打开浏览器开发者工具（F12）
2. 切换到「Console」标签
3. 点击「发送登录链接」按钮
4. 查看控制台输出

**可能的错误**：

#### 错误：`[useAuth] API Base: undefined`
**原因**：前端环境变量未配置
**解决**：创建 `frontend/.env` 文件：
```bash
NUXT_PUBLIC_API_BASE=http://localhost:8882
```

#### 错误：`网络请求失败` 或 `ERR_CONNECTION_REFUSED`
**原因**：后端服务未启动
**解决**：
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8882
```

#### 错误：`503 Service Unavailable: 邮件服务未配置`
**原因**：`.env` 中未配置 MAIL_USERNAME 或 MAIL_PASSWORD
**解决**：检查并配置邮件服务器信息

### 问题 2：没有收到邮件

**检查步骤**：

1. **查看后端日志**
   - 是否有错误信息？
   - 是否显示邮件发送成功？

2. **检查垃圾邮件文件夹**
   - Gmail 可能会将邮件标记为垃圾邮件

3. **检查邮件配置**
   ```bash
   # 后端控制台运行
   python
   >>> from app.config import settings
   >>> print(settings.mail_username)
   >>> print(settings.mail_server)
   >>> print(settings.mail_port)
   ```

4. **测试 SMTP 连接**
   ```python
   # test_email.py
   import smtplib
   from email.mime.text import MIMEText

   server = smtplib.SMTP('smtp.gmail.com', 587)
   server.starttls()
   server.login('your-email@gmail.com', 'your-app-password')
   print("SMTP 连接成功！")
   server.quit()
   ```

### 问题 3：链接已过期

**原因**：Magic Link 默认有效期为 15 分钟

**解决**：
1. 返回登录页面重新发送
2. 或修改 `.env` 延长有效期：
   ```bash
   MAGIC_LINK_EXPIRATION_MINUTES=30  # 30分钟
   ```

### 问题 4：验证失败

**检查数据库**：
```bash
# SQLite
sqlite3 backend/insightreader_v2.db
SELECT * FROM magic_links ORDER BY created_at DESC LIMIT 5;

# 查看 token 是否存在、是否已使用、是否过期
```

**可能的原因**：
- Token 已使用（used = True）
- Token 已过期（expires_at < 当前时间）
- Token 不存在（数据库中找不到）

## 🔧 手动测试 API

### 测试发送魔法链接

```bash
curl -X POST http://localhost:8882/api/v1/auth/magic-link/request \
  -H "Content-Type: application/json" \
  -d '{"email": "your-email@example.com"}'
```

**期望响应**：
```json
{
  "message": "魔法链接已发送到你的邮箱",
  "email": "your-email@example.com"
}
```

### 测试验证魔法链接

```bash
# 从数据库或邮件中获取 token
TOKEN="your-magic-link-token"

curl -X GET "http://localhost:8882/api/v1/auth/magic-link/verify?token=$TOKEN"
```

**期望响应**：
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "email": "your-email@example.com",
    "username": null,
    "avatar_url": null,
    "is_active": true
  }
}
```

## 📊 监控和日志

### 前端日志位置

打开浏览器控制台（F12 → Console），查找以下标记的日志：
- `[Login]` - 登录页面
- `[Magic]` - 验证页面
- `[useAuth]` - 认证逻辑

### 后端日志

后端控制台会显示：
- API 请求日志
- SMTP 连接日志
- 错误堆栈信息

### 数据库检查

```sql
-- 查看最近的魔法链接
SELECT
  email,
  token,
  used,
  expires_at,
  created_at
FROM magic_links
ORDER BY created_at DESC
LIMIT 10;

-- 清理过期的链接
DELETE FROM magic_links
WHERE expires_at < datetime('now');
```

## ✅ 成功标准

测试通过的标准：

1. ✅ 可以成功发送魔法链接邮件
2. ✅ 邮件包含正确的登录链接
3. ✅ 点击链接可以自动验证并登录
4. ✅ 登录后自动跳转到首页
5. ✅ 登录状态持久化（刷新页面仍然保持登录）
6. ✅ JWT token 正确保存到 localStorage
7. ✅ 后续 API 请求自动携带 Authorization header

## 🚀 下一步

测试通过后：
1. 配置生产环境的邮件服务（SendGrid、Mailgun 等）
2. 自定义邮件模板
3. 添加邮件发送速率限制
4. 配置定时任务清理过期链接
5. 监控邮件送达率

---

**需要帮助？** 查看完整文档：[EMAIL_LOGIN_SETUP.md](../backend/docs/EMAIL_LOGIN_SETUP.md)
