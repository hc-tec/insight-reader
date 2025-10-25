"""
添加 parent_id 到 InsightHistory 表
用于支持追问对话链

运行方式：
python -m app.db.add_parent_id_to_insight_history
"""

from sqlalchemy import create_engine, text
from app.config import Settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate():
    settings = Settings()
    engine = create_engine(settings.database_url)

    with engine.connect() as conn:
        try:
            # 检查列是否已存在 (SQLite 兼容)
            result = conn.execute(text("PRAGMA table_info(insight_history)"))
            columns = [row[1] for row in result.fetchall()]

            if 'parent_id' in columns:
                logger.info("✅ parent_id 列已存在，跳过迁移")
                return

            # 添加 parent_id 列
            logger.info("🔄 添加 parent_id 列到 insight_history 表...")
            conn.execute(text("""
                ALTER TABLE insight_history
                ADD COLUMN parent_id INTEGER NULL
            """))

            # 添加索引以提高查询性能
            logger.info("🔄 添加索引...")
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_insight_history_parent_id ON insight_history(parent_id)
            """))

            conn.commit()
            logger.info("✅ 迁移完成！parent_id 列已成功添加")

        except Exception as e:
            conn.rollback()
            logger.error(f"❌ 迁移失败: {str(e)}")
            raise

if __name__ == "__main__":
    migrate()
