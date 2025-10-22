"""
数据库迁移脚本：为 articles 表添加示例文章相关字段
执行命令: python -m app.db.migrate_add_demo_fields
"""
import sys
from sqlalchemy import text
from app.db.database import engine, SessionLocal
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate():
    """执行迁移"""
    db = SessionLocal()
    try:
        logger.info("开始数据库迁移：添加示例文章字段")

        # 1. 添加 is_demo 字段
        logger.info("添加 is_demo 字段...")
        db.execute(text("""
            ALTER TABLE articles
            ADD COLUMN IF NOT EXISTS is_demo BOOLEAN DEFAULT FALSE NOT NULL
        """))

        # 2. 添加 demo_order 字段（用于控制展示顺序）
        logger.info("添加 demo_order 字段...")
        db.execute(text("""
            ALTER TABLE articles
            ADD COLUMN IF NOT EXISTS demo_order INTEGER DEFAULT NULL
        """))

        # 3. 创建索引（优化查询性能）
        logger.info("创建索引...")
        db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_articles_is_demo
            ON articles(is_demo)
            WHERE is_demo = TRUE
        """))

        # 4. 创建组合索引（按顺序查询示例文章）
        logger.info("创建组合索引...")
        db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_articles_demo_order
            ON articles(is_demo, demo_order)
            WHERE is_demo = TRUE
        """))

        db.commit()
        logger.info("✅ 数据库迁移完成！")

        # 验证迁移结果
        logger.info("验证迁移结果...")
        result = db.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'articles'
            AND column_name IN ('is_demo', 'demo_order')
            ORDER BY column_name
        """))

        logger.info("新增字段信息：")
        for row in result:
            logger.info(f"  - {row[0]}: {row[1]} (nullable={row[2]}, default={row[3]})")

    except Exception as e:
        logger.error(f"❌ 迁移失败: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


def rollback():
    """回滚迁移"""
    db = SessionLocal()
    try:
        logger.info("开始回滚迁移：删除示例文章字段")

        # 删除索引
        logger.info("删除索引...")
        db.execute(text("DROP INDEX IF EXISTS idx_articles_demo_order"))
        db.execute(text("DROP INDEX IF EXISTS idx_articles_is_demo"))

        # 删除字段
        logger.info("删除字段...")
        db.execute(text("ALTER TABLE articles DROP COLUMN IF EXISTS demo_order"))
        db.execute(text("ALTER TABLE articles DROP COLUMN IF EXISTS is_demo"))

        db.commit()
        logger.info("✅ 回滚完成！")

    except Exception as e:
        logger.error(f"❌ 回滚失败: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        rollback()
    else:
        migrate()
