# 数据库配置指南

## 概述

InsightReader 支持两种数据库：

- **SQLite**：开发环境，零配置，快速启动
- **PostgreSQL**：生产环境，高性能，适合大规模部署

系统会**自动根据环境变量选择数据库**：

- 如果设置了 `STORAGE_DATABASE_URL` → 使用 PostgreSQL
- 如果未设置 `STORAGE_DATABASE_URL` → 使用 SQLite（默认）

---

## 开发环境配置（SQLite）

### 1. 零配置启动

SQLite 是默认数据库，无需任何配置即可启动：

```bash
# 直接启动即可
python -m uvicorn app.main:app --reload
```

数据库文件会自动创建在项目根目录：`insightreader_v2.db`

### 2. 特点

- ✅ 零配置，开箱即用
- ✅ 单文件数据库，便于备份和迁移
- ✅ 适合本地开发和测试
- ⚠️ 不支持并发写入
- ⚠️ 性能有限，不适合生产环境

---

## 生产环境配置（PostgreSQL）

### 1. 安装 PostgreSQL

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

#### macOS
```bash
brew install postgresql
brew services start postgresql
```

#### Windows
下载并安装：https://www.postgresql.org/download/windows/

### 2. 创建数据库和用户

```bash
# 进入 PostgreSQL 命令行
sudo -u postgres psql

# 创建数据库
CREATE DATABASE insightreader;

# 创建用户并设置密码
CREATE USER insightreader_user WITH PASSWORD 'your_secure_password';

# 授予权限
GRANT ALL PRIVILEGES ON DATABASE insightreader TO insightreader_user;

# 退出
\q
```

### 3. 配置环境变量

在 `.env` 文件中添加：

```bash
STORAGE_DATABASE_URL=postgresql://insightreader_user:your_secure_password@localhost:5432/insightreader
```

**URL 格式：**
```
postgresql://用户名:密码@主机:端口/数据库名
```

**示例：**
- 本地开发：`postgresql://user:pass@localhost:5432/dbname`
- Docker：`postgresql://user:pass@postgres:5432/dbname`
- 云服务：`postgresql://user:pass@your-db-host.com:5432/dbname`

### 4. 安装 Python 驱动

系统会自动选择最佳的 PostgreSQL 驱动：

- **psycopg (v3)**: 纯 Python 实现，优先使用，适合 Serverless 环境（Vercel、AWS Lambda 等）
- **psycopg2-binary**: 编译版本，本地开发环境的备选方案

```bash
# 两个驱动都已包含在 requirements.txt 中
pip install -r requirements.txt
```

**自动驱动选择逻辑**：
1. 优先尝试使用 `psycopg` (v3) - 纯 Python，无需编译，适合 Serverless
2. 如果 `psycopg` 不可用，回退到 `psycopg2-binary` - 适合本地开发

### 5. 启动应用

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

启动时会看到：
```
[OK] Using PostgreSQL database
[OK] Using psycopg (v3) driver for PostgreSQL
```

或（如果使用 psycopg2）：
```
[OK] Using PostgreSQL database
[OK] Using psycopg2 driver for PostgreSQL
```

### 6. 初始化数据库表

#### 方法1: 使用初始化脚本（推荐）

```bash
# 确保设置了环境变量
export STORAGE_DATABASE_URL=postgresql://user:password@localhost:5432/insightreader

# 运行初始化脚本
python init_database.py
```

你会看到：
```
============================================================
Database Initialization Script
============================================================

Database URL: postgresql://user:password@localhost:5432/insightreader
Database Type: PostgreSQL

Initializing database tables...

[SUCCESS] Database tables created successfully!

Created tables:
  - users
  - articles
  - insights
  - collections
  - sparks
  - meta_analysis
  - thinking_lens
  - insight_history
  - preferences

============================================================
```

#### 方法2: 启动应用自动初始化

首次启动应用时，会自动尝试创建所有表：

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

应用启动后，会自动创建缺失的表。

#### 方法3: 手动初始化（Python）

```python
from app.db.database import init_db
init_db()
```

---

## 环境变量完整配置

### .env 文件示例

```bash
# 数据库配置（二选一）

# 选项1: PostgreSQL（生产环境）
STORAGE_DATABASE_URL=postgresql://user:password@localhost:5432/insightreader

# 选项2: SQLite（开发环境，无需配置）
# 自动使用: sqlite:///./insightreader_v2.db

# 其他配置...
OPENAI_API_KEY=your-api-key
SECRET_KEY=your-secret-key
```

---

## 数据库迁移

### 从 SQLite 迁移到 PostgreSQL

如果你已经在 SQLite 中有数据，需要迁移到 PostgreSQL：

#### 方法1: 使用工具迁移

```bash
# 安装 pgloader
sudo apt install pgloader

# 迁移数据
pgloader insightreader_v2.db postgresql://user:pass@localhost/insightreader
```

#### 方法2: 手动导出/导入

```bash
# 1. 导出 SQLite 数据（示例）
sqlite3 insightreader_v2.db .dump > data.sql

# 2. 转换并导入到 PostgreSQL
# （需要处理 SQL 语法差异）
```

---

## Docker 部署示例

### docker-compose.yml

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: insightreader
      POSTGRES_USER: insightreader_user
      POSTGRES_PASSWORD: your_secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: .
    environment:
      STORAGE_DATABASE_URL: postgresql://insightreader_user:your_secure_password@postgres:5432/insightreader
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      SECRET_KEY: ${SECRET_KEY}
    depends_on:
      - postgres
    ports:
      - "8000:8000"

volumes:
  postgres_data:
```

---

## Serverless 部署（Vercel/AWS Lambda）

### 特殊说明

在 Serverless 环境中部署时，需要注意：

1. **驱动选择**：系统会自动使用 `psycopg` (v3) 驱动
   - ✅ 纯 Python 实现，无需编译
   - ✅ 在 Vercel、AWS Lambda 等环境中完美运行
   - ✅ `psycopg2-binary` 在这些环境中通常无法使用

2. **数据库连接**：
   - 推荐使用连接池服务（如 Supabase、PlanetScale、Neon）
   - 避免直接连接传统 PostgreSQL（连接数限制）
   - 使用环境变量配置 `STORAGE_DATABASE_URL`

3. **Vercel 部署示例**：

```bash
# .env.production
STORAGE_DATABASE_URL=postgresql://user:pass@db.supabase.co:5432/postgres
OPENAI_API_KEY=sk-...
SECRET_KEY=your-secret-key
```

4. **初始化数据库表**：

在首次部署到Vercel前，需要先初始化PostgreSQL数据库表。有两种方法：

**方法A: 本地初始化（推荐）**

```bash
# 1. 在本地设置生产环境数据库URL
export STORAGE_DATABASE_URL=postgresql://user:pass@your-prod-db:5432/dbname

# 2. 运行初始化脚本
cd backend
python init_database.py
```

**方法B: 使用Vercel CLI**

```bash
# 1. 安装Vercel CLI
npm i -g vercel

# 2. 设置环境变量并运行初始化
vercel env pull .env.production
cd backend
python init_database.py
```

5. **部署到Vercel**：

```bash
git add .
git commit -m "Setup database"
git push
```

6. **验证部署**：

部署成功后，检查Vercel日志应该看到：
```
[OK] Using PostgreSQL database
[OK] Using psycopg (v3) driver for PostgreSQL
[OK] Database initialization completed
```

### 常见Vercel部署错误

#### ❌ 错误: "relation 'users' does not exist"

**原因**: 数据库表没有初始化

**解决方案**:
```bash
# 本地连接到生产数据库并初始化
export STORAGE_DATABASE_URL=postgresql://...
python init_database.py
```

#### ❌ 错误: "No module named 'psycopg2'"

**原因**: 使用了错误的PostgreSQL驱动

**解决方案**: 确保 `requirements.txt` 包含 `psycopg==3.1.18`（已修复）

---

## 常见问题

### Q: 如何查看当前使用的数据库和驱动？

**A:** 启动应用时，控制台会打印：

- `[OK] Using PostgreSQL database` + `[OK] Using psycopg (v3) driver` 或
- `[OK] Using SQLite database: sqlite:///./insightreader_v2.db`

### Q: SQLite 和 PostgreSQL 可以同时使用吗？

**A:** 不可以，只能选择一种。优先级：`STORAGE_DATABASE_URL` > 默认 SQLite

### Q: 如何在开发中临时使用 PostgreSQL？

**A:** 在 `.env` 文件中设置 `STORAGE_DATABASE_URL`，或通过环境变量：

```bash
STORAGE_DATABASE_URL=postgresql://... python -m uvicorn app.main:app --reload
```

### Q: PostgreSQL 连接失败怎么办？

**A:** 检查：

1. PostgreSQL 服务是否运行：`sudo systemctl status postgresql`
2. 用户名、密码是否正确
3. 数据库是否已创建
4. 防火墙是否允许连接
5. `pg_hba.conf` 是否配置正确

### Q: Vercel 部署时出现 "No module named 'psycopg2'" 错误？

**A:** 这是正常的。系统会自动使用 `psycopg` (v3) 驱动：

1. 确保 `requirements.txt` 包含 `psycopg==3.1.18`
2. 重新部署应用
3. 检查日志应该看到 `[OK] Using psycopg (v3) driver`

### Q: 本地开发时想使用 psycopg2 而不是 psycopg？

**A:** 可以卸载 psycopg：

```bash
pip uninstall psycopg
```

系统会自动回退到 psycopg2-binary。但建议保留两个驱动，让系统自动选择。

### Q: 如何备份数据？

**SQLite:**
```bash
# 直接复制数据库文件
cp insightreader_v2.db insightreader_v2.db.backup
```

**PostgreSQL:**
```bash
# 使用 pg_dump
pg_dump -U insightreader_user -d insightreader > backup.sql

# 恢复
psql -U insightreader_user -d insightreader < backup.sql
```

---

## 性能对比

| 特性 | SQLite | PostgreSQL |
|------|--------|------------|
| 配置复杂度 | ⭐ 极简 | ⭐⭐⭐ 中等 |
| 并发性能 | ⭐⭐ 有限 | ⭐⭐⭐⭐⭐ 优秀 |
| 数据量支持 | ⭐⭐⭐ 中等 | ⭐⭐⭐⭐⭐ 海量 |
| 事务支持 | ⭐⭐⭐ 基础 | ⭐⭐⭐⭐⭐ 完整 |
| 适用场景 | 开发/测试 | 生产环境 |

---

## 技术细节

### 代码实现

数据库切换逻辑在 `app/config.py` 中：

```python
# 优先使用PostgreSQL，否则回退到SQLite
if settings.storage_database_url:
    settings.database_url = settings.storage_database_url
else:
    settings.database_url = "sqlite:///./insightreader_v2.db"
```

### 连接参数

`app/db/database.py` 会根据数据库类型自动调整连接参数：

```python
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)
```

- SQLite 需要 `check_same_thread=False`
- PostgreSQL 不需要此参数

---

## 总结

- **开发**：直接启动，使用 SQLite
- **生产**：设置 `STORAGE_DATABASE_URL`，使用 PostgreSQL
- **切换**：修改 `.env` 文件，重启应用即可

有问题？查看 `.env.example` 文件获取完整配置示例。
