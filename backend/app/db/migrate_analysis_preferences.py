# -*- coding: utf-8 -*-
"""
数据库迁移脚本：添加 user_analysis_preferences 表
用于存储用户的自动分析偏好设置
"""

import sqlite3
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.config import settings

def run_migration():
    """执行数据库迁移"""
    print("开始迁移：添加 user_analysis_preferences 表...")

    # 从 database_url 中提取路径
    db_path = settings.database_url.replace('sqlite:///', '')

    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 1. 创建 user_analysis_preferences 表
        print("创建 user_analysis_preferences 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_analysis_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,

                -- 分析开关
                auto_basic_analysis INTEGER NOT NULL DEFAULT 1,
                auto_meta_analysis INTEGER NOT NULL DEFAULT 0,
                auto_argument_lens INTEGER NOT NULL DEFAULT 0,
                auto_stance_lens INTEGER NOT NULL DEFAULT 0,

                -- 时间戳
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

                -- 外键约束
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # 2. 创建索引
        print("创建索引...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_analysis_preferences_user_id
            ON user_analysis_preferences(user_id)
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
