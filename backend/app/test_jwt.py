"""测试 JWT token 生成和验证"""
from app.utils.auth import create_access_token, verify_token
from app.config import settings

print("=" * 50)
print("JWT 配置测试")
print("=" * 50)

# 1. 检查配置
print(f"\n📋 当前配置:")
print(f"  SECRET_KEY: {'[已设置]' if settings.secret_key else '[未设置或为空]'}")
print(f"  SECRET_KEY 长度: {len(settings.secret_key)}")
print(f"  算法: {settings.algorithm}")

if not settings.secret_key:
    print("\n❌ 错误: SECRET_KEY 未设置!")
    print("请在 .env 文件中添加:")
    print('SECRET_KEY="your-very-long-secret-key-here"')
    exit(1)

if len(settings.secret_key) < 32:
    print("\n⚠️  警告: SECRET_KEY 太短，建议至少 32 个字符")

# 2. 测试 token 生成
print("\n🔐 测试 Token 生成:")
test_data = {"sub": 123}
token = create_access_token(test_data)
print(f"  生成的 Token: {token[:50]}...")

# 3. 测试 token 验证
print("\n✅ 测试 Token 验证:")
payload = verify_token(token)
if payload:
    print(f"  验证成功!")
    print(f"  Payload: {payload}")
else:
    print(f"  ❌ 验证失败!")

print("\n" + "=" * 50)
