# -*- coding: utf-8 -*-
"""
数据库迁移脚本：添加 analysis_reports 表
用于统一深度分析引擎
"""

import sqlite3
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.config import settings

def run_migration():
    """执行数据库迁移"""
    print("开始迁移：添加 analysis_reports 表...")

    # 从 database_url 中提取路径
    db_path = settings.database_url.replace('sqlite:///', '')

    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 1. 创建 analysis_reports 表
        print("创建 analysis_reports 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_id INTEGER NOT NULL UNIQUE,

                -- 分析状态
                status VARCHAR(20) NOT NULL DEFAULT 'pending',

                -- 分析报告数据 (JSON)
                report_data TEXT,

                -- 版本控制
                analysis_version VARCHAR(10) NOT NULL DEFAULT '1.0',

                -- LLM 元信息
                model_used VARCHAR(50),
                tokens_used INTEGER,
                processing_time_ms INTEGER,

                -- 错误信息
                error_message TEXT,
                retry_count INTEGER NOT NULL DEFAULT 0,

                -- 时间戳
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,

                -- 外键约束
                FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
            )
        """)

        # 2. 创建索引
        print("创建索引...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_analysis_reports_article_id
            ON analysis_reports(article_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_analysis_reports_status
            ON analysis_reports(status)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_analysis_reports_created_at
            ON analysis_reports(created_at)
        """)

        # 3. 提交更改
        conn.commit()
        print("迁移成功完成!")

    except Exception as e:
        print(f"迁移失败: {str(e)}")
        conn.rollback()
        raise

    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()
