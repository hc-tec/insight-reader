"""数据库迁移：添加 OAuth 字段到 users 表"""
import sqlite3
from pathlib import Path

# 数据库路径
db_path = Path(__file__).parent.parent / "insightreader.db"

def migrate():
    """迁移数据库结构"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print("开始迁移数据库...")

        # 1. 检查并添加 oauth_provider 字段
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN oauth_provider VARCHAR(50)")
            print("✅ 添加 oauth_provider 字段")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("⏭️  oauth_provider 字段已存在，跳过")
            else:
                raise

        # 2. 检查并添加 oauth_id 字段
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN oauth_id VARCHAR(255)")
            print("✅ 添加 oauth_id 字段")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("⏭️  oauth_id 字段已存在，跳过")
            else:
                raise

        # 3. 检查并添加 avatar_url 字段
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN avatar_url VARCHAR(500)")
            print("✅ 添加 avatar_url 字段")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("⏭️  avatar_url 字段已存在，跳过")
            else:
                raise

        # 4. 检查并添加 last_login 字段
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN last_login DATETIME")
            cursor.execute("UPDATE users SET last_login = created_at WHERE last_login IS NULL")
            print("✅ 添加 last_login 字段")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("⏭️  last_login 字段已存在，跳过")
            else:
                raise

        # 5. 将 username 改为可选（通过设置默认值）
        # SQLite 不支持直接修改列属性，但我们可以允许 NULL 值
        # 新用户会在模型层处理

        # 6. 删除 hashed_password 列（SQLite 需要重建表）
        # 检查是否存在 hashed_password 列
        cursor.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]

        if 'hashed_password' in columns:
            print("🔄 重建 users 表以移除 hashed_password 字段...")

            # 创建临时表
            cursor.execute("""
                CREATE TABLE users_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    username VARCHAR(100),
                    oauth_provider VARCHAR(50),
                    oauth_id VARCHAR(255),
                    avatar_url VARCHAR(500),
                    created_at DATETIME NOT NULL,
                    last_login DATETIME NOT NULL,
                    is_active BOOLEAN NOT NULL DEFAULT 1
                )
            """)

            # 复制数据（只复制新表中存在的列）
            cursor.execute("""
                INSERT INTO users_new (id, email, username, oauth_provider, oauth_id, avatar_url, created_at, last_login, is_active)
                SELECT id, email, username, oauth_provider, oauth_id, avatar_url, created_at,
                       COALESCE(last_login, created_at), is_active
                FROM users
            """)

            # 删除旧表
            cursor.execute("DROP TABLE users")

            # 重命名新表
            cursor.execute("ALTER TABLE users_new RENAME TO users")

            # 重新创建索引
            cursor.execute("CREATE UNIQUE INDEX ix_users_email ON users (email)")
            cursor.execute("CREATE INDEX ix_users_id ON users (id)")

            print("✅ 成功移除 hashed_password 字段")
        else:
            print("⏭️  hashed_password 字段不存在，跳过")

        # 7. 创建 magic_links 表（如果不存在）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS magic_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email VARCHAR(255) NOT NULL,
                token VARCHAR(255) UNIQUE NOT NULL,
                created_at DATETIME NOT NULL,
                expires_at DATETIME NOT NULL,
                used BOOLEAN NOT NULL DEFAULT 0
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_magic_links_token ON magic_links (token)")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_magic_links_email ON magic_links (email)")
        print("✅ 创建 magic_links 表")

        conn.commit()
        print("\n🎉 数据库迁移完成！")

    except Exception as e:
        conn.rollback()
        print(f"\n❌ 迁移失败: {e}")
        raise

    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
