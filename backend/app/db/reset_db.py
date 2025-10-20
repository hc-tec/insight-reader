"""重新初始化数据库"""
import os
from pathlib import Path

# 获取数据库文件路径
db_file = Path(__file__).parent.parent.parent / "insightreader.db"

print(f"数据库文件路径: {db_file}")

# 删除旧数据库
if db_file.exists():
    try:
        os.remove(db_file)
        print("✅ 已删除旧数据库文件")
    except PermissionError:
        print("❌ 无法删除数据库文件（可能正在被使用）")
        print("请先停止后端服务器，然后重新运行此脚本")
        exit(1)
else:
    print("⏭️  数据库文件不存在")

# 初始化新数据库
print("\n开始创建新数据库...")

from app.db.database import init_db

init_db()

print("✅ 数据库初始化完成！")
print("\n新数据库结构包含以下字段：")
print("  - users.oauth_provider (OAuth 提供商)")
print("  - users.oauth_id (OAuth 用户ID)")
print("  - users.avatar_url (用户头像)")
print("  - users.last_login (最后登录时间)")
print("  - magic_links 表 (魔法链接)")
print("\n已移除字段：")
print("  - users.hashed_password (不再使用密码)")
