"""魔法链接邮件服务"""
from datetime import datetime, timedelta
from itsdangerous import URLSafeTimedSerializer
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from sqlalchemy.orm import Session
import logging

from app.config import settings
from app.models.models import MagicLink
import secrets

logger = logging.getLogger(__name__)


# 邮件配置
mail_config = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_STARTTLS=settings.mail_tls,
    MAIL_SSL_TLS=settings.mail_ssl,
    MAIL_FROM_NAME=settings.mail_from_name,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

fastmail = FastMail(mail_config)

# Token 序列化器
serializer = URLSafeTimedSerializer(settings.secret_key)


async def create_magic_link(email: str, db: Session) -> str:
    """创建魔法链接"""
    # 生成安全的随机 token
    token = secrets.token_urlsafe(32)

    # 创建过期时间
    expires_at = datetime.utcnow() + timedelta(
        minutes=settings.magic_link_expiration_minutes
    )

    # 保存到数据库
    magic_link = MagicLink(
        email=email,
        token=token,
        expires_at=expires_at,
        used=False
    )
    db.add(magic_link)
    db.commit()

    return token


async def send_magic_link_email(email: str, token: str):
    """发送魔法链接邮件"""
    # 构建登录链接（前端使用 hash 路由）
    login_url = f"{settings.frontend_url}/#/auth/magic?token={token}"

    # 邮件内容
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .container {{
                background: #ffffff;
                border-radius: 8px;
                padding: 40px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .logo {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .logo h1 {{
                color: #2563eb;
                margin: 0;
            }}
            .button {{
                display: inline-block;
                padding: 12px 24px;
                background: #2563eb;
                color: #ffffff;
                text-decoration: none;
                border-radius: 6px;
                font-weight: 600;
                margin: 20px 0;
            }}
            .button:hover {{
                background: #1d4ed8;
            }}
            .footer {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #e5e7eb;
                color: #6b7280;
                font-size: 14px;
            }}
            .warning {{
                background: #fef3c7;
                border-left: 4px solid #f59e0b;
                padding: 12px;
                margin: 20px 0;
                border-radius: 4px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">
                <h1>InsightReader</h1>
            </div>

            <h2>登录你的账户</h2>

            <p>你好！</p>

            <p>点击下面的按钮即可登录 InsightReader：</p>

            <div style="text-align: center;">
                <a href="{login_url}" class="button">立即登录</a>
            </div>

            <div class="warning">
                <strong>⏰ 注意：</strong>此链接将在 {settings.magic_link_expiration_minutes} 分钟后过期。
            </div>

            <p>如果按钮无法点击，请复制下面的链接到浏览器：</p>
            <p style="word-break: break-all; color: #6b7280; font-size: 14px;">
                {login_url}
            </p>

            <div class="footer">
                <p>如果你没有请求此邮件，请忽略它。</p>
                <p>© 2025 InsightReader. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """

    message = MessageSchema(
        subject="登录 InsightReader - 魔法链接",
        recipients=[email],
        body=html_content,
        subtype="html"
    )

    try:
        await fastmail.send_message(message)
        logger.info(f"[Email] 魔法链接邮件已发送到: {email}")
    except Exception as e:
        error_msg = str(e)
        # QQ邮箱的特殊响应：虽然报错但邮件实际已发送成功
        if "Malformed SMTP response line" in error_msg or "\\x00" in error_msg:
            logger.warning(f"[Email] QQ邮箱特殊响应（邮件已发送）: {error_msg[:100]}")
            logger.info(f"[Email] 魔法链接邮件已发送到: {email}")
            # 这是QQ邮箱的正常响应，邮件已发送成功，忽略错误
        else:
            # 其他错误需要抛出
            logger.error(f"[Email] 发送邮件失败: {error_msg}")
            raise


async def verify_magic_link(token: str, db: Session) -> str | None:
    """验证魔法链接并返回邮箱"""
    # 从数据库查找 token
    magic_link = db.query(MagicLink).filter(
        MagicLink.token == token,
        MagicLink.used == False
    ).first()

    if not magic_link:
        return None

    # 检查是否过期
    if datetime.utcnow() > magic_link.expires_at:
        return None

    # 标记为已使用
    magic_link.used = True
    db.commit()

    return magic_link.email


async def cleanup_expired_links(db: Session):
    """清理过期的魔法链接"""
    db.query(MagicLink).filter(
        MagicLink.expires_at < datetime.utcnow()
    ).delete()
    db.commit()
