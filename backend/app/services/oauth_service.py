"""OAuth 社交登录服务"""
import logging
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from app.config import settings

logger = logging.getLogger(__name__)

# 初始化 OAuth
config = Config(environ={
    'GOOGLE_CLIENT_ID': settings.google_client_id,
    'GOOGLE_CLIENT_SECRET': settings.google_client_secret,
    'GITHUB_CLIENT_ID': settings.github_client_id,
    'GITHUB_CLIENT_SECRET': settings.github_client_secret,
})

oauth = OAuth(config)

# 注册 Google OAuth
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

# 注册 GitHub OAuth
oauth.register(
    name='github',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
    api_base_url='https://api.github.com/',
    client_kwargs={
        'scope': 'user:email'
    }
)


async def get_google_user_info(token: dict) -> dict:
    """从 Google token 获取用户信息"""
    try:
        # Google ID token 已经包含用户信息
        user_info = token.get('userinfo')
        if user_info:
            return {
                'id': user_info.get('sub'),
                'email': user_info.get('email'),
                'name': user_info.get('name'),
                'avatar': user_info.get('picture')
            }
        return {}
    except Exception as e:
        logger.error(f"Error getting Google user info: {e}")
        return {}


async def get_github_user_info(token: dict) -> dict:
    """从 GitHub token 获取用户信息"""
    try:
        import httpx

        access_token = token.get('access_token')
        if not access_token:
            return {}

        # 获取用户信息
        async with httpx.AsyncClient() as client:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json'
            }

            # 获取基本信息
            user_response = await client.get(
                'https://api.github.com/user',
                headers=headers
            )
            user_data = user_response.json()

            # 获取邮箱（如果公开邮箱为空）
            email = user_data.get('email')
            if not email:
                emails_response = await client.get(
                    'https://api.github.com/user/emails',
                    headers=headers
                )
                emails = emails_response.json()
                # 找到主邮箱
                for email_obj in emails:
                    if email_obj.get('primary'):
                        email = email_obj.get('email')
                        break

            return {
                'id': str(user_data.get('id')),
                'email': email,
                'name': user_data.get('name') or user_data.get('login'),
                'avatar': user_data.get('avatar_url')
            }
    except Exception as e:
        logger.error(f"Error getting GitHub user info: {e}")
        return {}
