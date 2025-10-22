"""
测试 SMTP 连接脚本
用于验证邮件配置是否正确
"""
import asyncio
from app.config import settings
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

async def test_smtp():
    """测试 SMTP 连接和邮件发送"""

    print("=" * 60)
    print("📧 测试 SMTP 连接")
    print("=" * 60)

    # 显示配置
    print("\n当前配置：")
    print(f"  服务器: {settings.mail_server}")
    print(f"  端口: {settings.mail_port}")
    print(f"  用户名: {settings.mail_username}")
    print(f"  密码: {'*' * len(settings.mail_password) if settings.mail_password else '(未设置)'}")
    print(f"  发件人: {settings.mail_from}")
    print(f"  TLS: {settings.mail_tls}")
    print(f"  SSL: {settings.mail_ssl}")

    # 创建邮件配置
    try:
        mail_config = ConnectionConfig(
            MAIL_USERNAME=settings.mail_username,
            MAIL_PASSWORD=settings.mail_password,
            MAIL_FROM=settings.mail_from,
            MAIL_PORT=settings.mail_port,
            MAIL_SERVER=settings.mail_server,
            MAIL_STARTTLS=settings.mail_tls,
            MAIL_SSL_TLS=settings.mail_ssl,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True
        )

        fastmail = FastMail(mail_config)

        print("\n✅ 邮件配置创建成功")

        # 发送测试邮件
        print("\n📨 发送测试邮件...")

        message = MessageSchema(
            subject="InsightReader 测试邮件",
            recipients=[settings.mail_username],  # 发给自己
            body="""
            <h1>测试邮件</h1>
            <p>这是一封来自 InsightReader 的测试邮件。</p>
            <p>如果你收到这封邮件，说明 SMTP 配置正确！</p>
            <hr>
            <p style="color: gray; font-size: 12px;">
                服务器: {}<br>
                端口: {}<br>
                加密方式: {}
            </p>
            """.format(
                settings.mail_server,
                settings.mail_port,
                "SSL" if settings.mail_ssl else ("TLS" if settings.mail_tls else "无")
            ),
            subtype="html"
        )

        await fastmail.send_message(message)

        print("\n✅ 测试邮件发送成功！")
        print(f"   请检查邮箱: {settings.mail_username}")
        print("\n" + "=" * 60)

    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        print("\n常见问题：")
        print("  1. 检查 QQ 邮箱是否开启了 SMTP 服务")
        print("  2. 确认授权码（不是QQ密码）是否正确")
        print("  3. 对于 QQ 邮箱，使用端口 465 + SSL")
        print("  4. 检查防火墙是否阻止了端口")
        print("\n" + "=" * 60)
        raise

if __name__ == "__main__":
    asyncio.run(test_smtp())
