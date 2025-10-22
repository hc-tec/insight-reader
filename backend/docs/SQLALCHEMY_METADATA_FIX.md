# SQLAlchemy Metadata 冲突修复

## 🐛 问题描述

在启动后端时遇到以下错误：

```
sqlalchemy.exc.InvalidRequestError: Attribute name 'metadata' is reserved when using the Declarative API.
```

## 🔍 原因分析

在 `app/models/models.py` 中的 `AnalysisReport` 模型定义了一个名为 `metadata` 的列：

```python
class AnalysisReport(Base):
    __tablename__ = "analysis_reports"

    # ...
    metadata = Column(JSON, nullable=True)  # ❌ 与 SQLAlchemy 保留字段冲突
```

SQLAlchemy 的 Declarative Base 使用 `metadata` 作为保留属性来存储表的元数据信息（Table Metadata），因此不能作为列名使用。

## ✅ 解决方案

将列名 `metadata` 重命名为 `analysis_metadata`。

### 修改的文件

#### 1. `backend/app/models/models.py`

**修改前**:
```python
# 元数据（可选，用于存储额外信息）
metadata = Column(JSON, nullable=True)
```

**修改后**:
```python
# 分析元数据（可选，用于存储额外信息，避免与 SQLAlchemy 的 metadata 冲突）
analysis_metadata = Column(JSON, nullable=True)
```

---

#### 2. `backend/app/db/migrate_add_async_fields.py`

**修改前**:
```python
if not check_column_exists('analysis_reports', 'metadata'):
    logger.info("\n[1/2] 添加 analysis_reports.metadata 字段...")
    if 'postgresql' in settings.database_url:
        conn.execute(text(
            "ALTER TABLE analysis_reports ADD COLUMN metadata JSONB"
        ))
    else:
        conn.execute(text(
            "ALTER TABLE analysis_reports ADD COLUMN metadata TEXT"
        ))
```

**修改后**:
```python
if not check_column_exists('analysis_reports', 'analysis_metadata'):
    logger.info("\n[1/2] 添加 analysis_reports.analysis_metadata 字段...")
    if 'postgresql' in settings.database_url:
        conn.execute(text(
            "ALTER TABLE analysis_reports ADD COLUMN analysis_metadata JSONB"
        ))
    else:
        conn.execute(text(
            "ALTER TABLE analysis_reports ADD COLUMN analysis_metadata TEXT"
        ))
```

---

#### 3. `backend/app/api/unified_analysis_async.py`

**修改位置 1** (保存分析结果):
```python
# 修改前
report.metadata = result['metadata']

# 修改后
report.analysis_metadata = result['metadata']
```

**修改位置 2** (重置分析报告):
```python
# 修改前
report.metadata = None

# 修改后
report.analysis_metadata = None
```

---

#### 4. `backend/app/api/unified_analysis.py`

**修改位置** (保存分析结果):
```python
# 修改前
report.metadata = result['metadata']

# 修改后
report.analysis_metadata = result['metadata']
```

---

#### 5. `backend/DEPLOYMENT_CHECKLIST.md`

更新了迁移脚本的输出示例和手动迁移命令，将 `metadata` 改为 `analysis_metadata`。

---

## 📊 数据库迁移

### 自动迁移

运行以下命令自动添加新字段：

```bash
cd backend
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

### 手动迁移

#### PostgreSQL
```sql
ALTER TABLE analysis_reports ADD COLUMN IF NOT EXISTS analysis_metadata JSONB;
ALTER TABLE meta_analyses ADD COLUMN IF NOT EXISTS generated_title VARCHAR(500);
```

#### SQLite
```sql
ALTER TABLE analysis_reports ADD COLUMN analysis_metadata TEXT;
ALTER TABLE meta_analyses ADD COLUMN generated_title TEXT;
```

---

## ⚠️ 注意事项

### 如果已经运行过旧版迁移脚本

如果您之前已经运行过旧版的迁移脚本，数据库中可能已经存在 `metadata` 列。您需要：

#### 方案 1: 重命名现有列（推荐）

**PostgreSQL**:
```sql
ALTER TABLE analysis_reports RENAME COLUMN metadata TO analysis_metadata;
```

**SQLite** (需要重建表):
```sql
-- SQLite 不支持直接重命名列，需要重建表
BEGIN TRANSACTION;

-- 创建新表
CREATE TABLE analysis_reports_new (
    id INTEGER PRIMARY KEY,
    article_id INTEGER NOT NULL UNIQUE,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    report_data TEXT,
    analysis_metadata TEXT,  -- 新列名
    analysis_version VARCHAR(10) NOT NULL DEFAULT '1.0',
    model_used VARCHAR(50),
    tokens_used INTEGER,
    processing_time_ms INTEGER,
    error_message TEXT,
    retry_count INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    completed_at DATETIME,
    FOREIGN KEY (article_id) REFERENCES articles(id)
);

-- 复制数据
INSERT INTO analysis_reports_new
SELECT
    id, article_id, status, report_data,
    metadata AS analysis_metadata,  -- 旧列 → 新列
    analysis_version, model_used, tokens_used, processing_time_ms,
    error_message, retry_count, created_at, updated_at, completed_at
FROM analysis_reports;

-- 删除旧表
DROP TABLE analysis_reports;

-- 重命名新表
ALTER TABLE analysis_reports_new RENAME TO analysis_reports;

COMMIT;
```

#### 方案 2: 删除旧列并重新迁移

**警告**: 这将丢失 `metadata` 列中的所有数据！

```sql
-- PostgreSQL
ALTER TABLE analysis_reports DROP COLUMN metadata;

-- SQLite
-- SQLite 不支持 DROP COLUMN，需要使用方案 1
```

然后重新运行迁移脚本：
```bash
python -m app.db.migrate_add_async_fields
```

---

## ✅ 验证

### 检查列是否存在

```python
from app.db.database import engine
from sqlalchemy import inspect

inspector = inspect(engine)
columns = inspector.get_columns('analysis_reports')
column_names = [c['name'] for c in columns]

print('analysis_metadata' in column_names)  # 应该输出 True
print('metadata' in column_names)  # 应该输出 False
```

### 测试应用启动

```bash
cd backend
uvicorn app.main:app --reload
```

**预期**: 应用正常启动，无 SQLAlchemy 错误。

---

## 📚 相关资源

- [SQLAlchemy Declarative API - Reserved Names](https://docs.sqlalchemy.org/en/14/orm/declarative_tables.html#orm-declarative-mapper-config-reserved-names)
- SQLAlchemy 保留的属性名:
  - `metadata` - 表元数据
  - `__table__` - 表对象
  - `__mapper__` - 映射器对象
  - 其他以 `__` 开头的名称

---

## 🎉 总结

通过将 `metadata` 重命名为 `analysis_metadata`，我们解决了与 SQLAlchemy Declarative API 的命名冲突问题。此修改影响：

- ✅ 数据库模型定义
- ✅ 数据库迁移脚本
- ✅ API 代码（2 个文件，3 处引用）
- ✅ 部署文档

应用现在可以正常启动并运行！
