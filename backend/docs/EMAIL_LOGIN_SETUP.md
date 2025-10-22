# 📧 邮箱登录（Magic Link）配置指南

本文档详细说明如何配置 InsightReader 的邮箱魔法链接登录功能。

## 📋 功能概述

Magic Link 是一种无密码登录方式：
1. 用户输入邮箱地址
2. 系统发送包含登录链接的邮件
3. 用户点击邮件中的链接即可完成登录
4. 链接有效期为 15 分钟（可配置）

## 🔧 配置步骤

### 1. 配置环境变量

编辑 `backend/.env` 文件，添加邮件服务器配置：

```bash
# ==========================================
# Email Configuration (Magic Links)
# ==========================================

# Gmail 示例
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=your-email@gmail.com
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_TLS=true
MAIL_SSL=false

# Magic Link 有效期（分钟）
MAGIC_LINK_EXPIRATION_MINUTES=15

# 前端 URL（用于生成登录链接）
FRONTEND_URL=http://localhost:3000
```

### 2. 支持的邮件服务商

#### Gmail

1. **启用两步验证**
   - 访问：https://myaccount.google.com/security
   - 找到「两步验证」并启用

2. **生成应用专用密码**
   - 访问：https://myaccount.google.com/apppasswords
   - 选择「邮件」和「其他（自定义名称）」
   - 输入「InsightReader」
   - 复制生成的 16 位密码

3. **配置 .env**
   ```bash
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=abcd efgh ijkl mnop  # 16位应用密码
   MAIL_FROM=your-email@gmail.com
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_TLS=true
   MAIL_SSL=false
   ```

#### Outlook/Hotmail

```bash
MAIL_USERNAME=your-email@outlook.com
MAIL_PASSWORD=your-password
MAIL_FROM=your-email@outlook.com
MAIL_SERVER=smtp-mail.outlook.com
MAIL_PORT=587
MAIL_TLS=true
MAIL_SSL=false
```

#### QQ 邮箱

1. 在 QQ 邮箱设置中开启 SMTP 服务
2. 获取授权码（不是 QQ 密码）

```bash
MAIL_USERNAME=your-qq-number@qq.com
MAIL_PASSWORD=your-authorization-code
MAIL_FROM=your-qq-number@qq.com
MAIL_SERVER=smtp.qq.com
MAIL_PORT=587
MAIL_TLS=true
MAIL_SSL=false
```

#### 163 邮箱

```bash
MAIL_USERNAME=your-email@163.com
MAIL_PASSWORD=your-authorization-code
MAIL_FROM=your-email@163.com
MAIL_SERVER=smtp.163.com
MAIL_PORT=465
MAIL_TLS=false
MAIL_SSL=true
```

#### 自定义 SMTP 服务器

```bash
MAIL_USERNAME=your-email@yourdomain.com
MAIL_PASSWORD=your-password
MAIL_FROM=your-email@yourdomain.com
MAIL_SERVER=smtp.yourdomain.com
MAIL_PORT=587  # 或 465（SSL）
MAIL_TLS=true  # 或 false（如果使用 SSL）
MAIL_SSL=false  # 或 true（如果使用 SSL）
```

### 3. 验证配置

1. **启动后端服务**
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload --port 8882
   ```

2. **检查日志**
   - 如果邮件配置不完整，后端会在启动时输出警告

3. **测试发送**
   - 访问前端登录页面：http://localhost:3000/login
   - 输入你的邮箱地址
   - 点击「发送登录链接」
   - 检查邮箱是否收到邮件

## 📧 邮件模板

系统会发送格式化的 HTML 邮件，包含：
- InsightReader Logo 和品牌信息
- 大号「立即登录」按钮
- 链接有效期提示（15分钟）
- 备用文本链接
- 安全提示

## 🔍 故障排除

### 问题：邮件服务未配置

**错误信息**：`邮件服务未配置`

**解决方案**：
- 确保 `.env` 文件中设置了 `MAIL_USERNAME` 和 `MAIL_PASSWORD`
- 重启后端服务

### 问题：SMTP 认证失败

**错误信息**：`发送邮件失败: Authentication failed`

**解决方案**：
1. Gmail：确认已启用两步验证并使用应用专用密码
2. QQ/163：确认已开启 SMTP 服务并使用授权码
3. 检查用户名和密码是否正确

### 问题：连接超时

**错误信息**：`Connection timed out`

**解决方案**：
1. 检查防火墙设置，确保允许端口 587 或 465
2. 尝试切换 MAIL_TLS 和 MAIL_SSL 设置
3. 检查网络连接

### 问题：邮件被标记为垃圾邮件

**解决方案**：
1. 使用自己的域名邮箱（而不是免费邮箱）
2. 配置 SPF、DKIM、DMARC 记录
3. 使用专业的邮件发送服务（如 SendGrid、Mailgun）

### 问题：链接已过期

**错误信息**：`魔法链接无效或已过期`

**解决方案**：
- Magic Link 默认 15 分钟有效期
- 如需延长，修改 `.env` 中的 `MAGIC_LINK_EXPIRATION_MINUTES`
- 重新请求发送新的登录链接

## 🚀 生产环境建议

### 1. 使用专业邮件服务

对于生产环境，建议使用专业的邮件发送服务：

#### SendGrid

```bash
MAIL_USERNAME=apikey
MAIL_PASSWORD=your-sendgrid-api-key
MAIL_FROM=noreply@yourdomain.com
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_TLS=true
MAIL_SSL=false
```

#### Mailgun

```bash
MAIL_USERNAME=postmaster@yourdomain.com
MAIL_PASSWORD=your-mailgun-password
MAIL_FROM=noreply@yourdomain.com
MAIL_SERVER=smtp.mailgun.org
MAIL_PORT=587
MAIL_TLS=true
MAIL_SSL=false
```

#### Amazon SES

```bash
MAIL_USERNAME=your-ses-smtp-username
MAIL_PASSWORD=your-ses-smtp-password
MAIL_FROM=noreply@yourdomain.com
MAIL_SERVER=email-smtp.us-east-1.amazonaws.com
MAIL_PORT=587
MAIL_TLS=true
MAIL_SSL=false
```

### 2. 安全最佳实践

- ✅ 使用环境变量存储敏感信息
- ✅ 不要将 `.env` 文件提交到版本控制
- ✅ 使用强密码或应用专用密码
- ✅ 定期轮换密码
- ✅ 启用邮件发送速率限制
- ✅ 监控邮件发送日志

### 3. 性能优化

- 使用异步邮件发送（已实现）
- 配置邮件队列（如 Celery + Redis）
- 设置邮件发送重试机制
- 监控邮件送达率

## 🔐 数据库表结构

Magic Link 数据保存在 `magic_links` 表中：

```sql
CREATE TABLE magic_links (
    id INTEGER PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    token VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🧹 定期清理

系统会保存所有的 Magic Link 记录。建议定期清理过期记录：

```python
# 在 backend/app/services/magic_link_service.py 中
await cleanup_expired_links(db)
```

可以配置定时任务（如 APScheduler）自动清理。

## 📚 相关文件

- 后端 API：`backend/app/api/auth.py` - Magic Link 端点
- 邮件服务：`backend/app/services/magic_link_service.py` - 邮件发送逻辑
- 前端登录：`frontend/app/pages/login.vue` - 登录页面
- 前端验证：`frontend/app/pages/auth/magic.vue` - Magic Link 验证页面
- 认证逻辑：`frontend/app/composables/useAuth.ts` - 前端认证 Composable

## ❓ 常见问题

### Q: Magic Link 可以使用多次吗？
A: 不可以。每个 Magic Link 只能使用一次，使用后会被标记为已使用。

### Q: 可以修改邮件模板吗？
A: 可以。编辑 `backend/app/services/magic_link_service.py` 中的 `send_magic_link_email` 函数。

### Q: 支持哪些邮件服务器？
A: 支持所有标准的 SMTP 服务器，包括 Gmail、Outlook、QQ、163、企业邮箱等。

### Q: 如何更改链接有效期？
A: 修改 `.env` 中的 `MAGIC_LINK_EXPIRATION_MINUTES` 变量。

### Q: 邮件发送失败会返回错误吗？
A: 会。API 会返回详细的错误信息，前端会显示给用户。

## 🎯 下一步

配置完成后，你可以：
1. 访问登录页面测试邮箱登录
2. 配置 Google OAuth 和 GitHub OAuth（可选）
3. 自定义邮件模板
4. 配置邮件发送监控

---

**需要帮助？** 查看完整文档：[docs/README.md](./README.md)
