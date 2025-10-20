"""
数据库迁移脚本 - 添加洞察回放功能所需字段

使用方法：
python -m app.db.migrate_insight_replay
"""

import sqlite3
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.config import settings


def migrate():
    """执行数据库迁移"""
    db_path = "insightreader.db"

    print(f"Connecting to database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 1. 检查 articles 表是否有 insight_count 字段
        cursor.execute("PRAGMA table_info(articles)")
        columns = [row[1] for row in cursor.fetchall()]

        if 'insight_count' not in columns:
            print("Adding articles.insight_count column...")
            cursor.execute("""
                ALTER TABLE articles
                ADD COLUMN insight_count INTEGER DEFAULT 0 NOT NULL
            """)
            print("OK: articles.insight_count column added")
        else:
            print("SKIP: articles.insight_count column already exists")

        # 2. 创建 insight_history 表
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='insight_history'
        """)

        if not cursor.fetchone():
            print("Creating insight_history table...")
            cursor.execute("""
                CREATE TABLE insight_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id INTEGER NOT NULL,
                    user_id INTEGER,
                    selected_text TEXT NOT NULL,
                    selected_start INTEGER,
                    selected_end INTEGER,
                    context_before VARCHAR(200),
                    context_after VARCHAR(200),
                    intent VARCHAR(50) NOT NULL,
                    question TEXT,
                    insight TEXT NOT NULL,
                    reasoning TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            print("OK: insight_history table created")

            # 创建索引
            print("Creating indexes...")
            cursor.execute("""
                CREATE INDEX idx_insight_history_article_id
                ON insight_history(article_id)
            """)
            cursor.execute("""
                CREATE INDEX idx_insight_history_user_id
                ON insight_history(user_id)
            """)
            cursor.execute("""
                CREATE INDEX idx_insight_history_created_at
                ON insight_history(created_at)
            """)
            print("OK: indexes created")
        else:
            print("SKIP: insight_history table already exists")

        # 提交事务
        conn.commit()

        print("\nDatabase migration completed!")
        print("\nCurrent table structure:")

        # 显示 articles 表结构
        cursor.execute("PRAGMA table_info(articles)")
        print("\narticles table:")
        for row in cursor.fetchall():
            print(f"  - {row[1]}: {row[2]}")

        # 显示 insight_history 表结构
        cursor.execute("PRAGMA table_info(insight_history)")
        print("\ninsight_history table:")
        for row in cursor.fetchall():
            print(f"  - {row[1]}: {row[2]}")

        # 统计数据
        cursor.execute("SELECT COUNT(*) FROM articles")
        articles_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM insight_history")
        insights_count = cursor.fetchone()[0]

        print(f"\nData statistics:")
        print(f"  - Articles: {articles_count}")
        print(f"  - Insights: {insights_count}")

    except Exception as e:
        print(f"\nMigration failed: {str(e)}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    print("=" * 60)
    print("InsightReader Database Migration Tool")
    print("=" * 60)
    print("\nFunction: Add database fields and tables for insight replay")
    print("\nStarting migration...\n")

    migrate()

    print("\n" + "=" * 60)
    print("Migration completed! You can now start the application")
    print("=" * 60)
