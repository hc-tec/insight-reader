"""配置管理"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""

    # OpenAI API 配置
    openai_base_url: str = ""
    openai_api_key: str = ""

    # 应用配置
    app_name: str = "InsightReader API"
    app_version: str = "2.0.0"
    debug: bool = False

    # 数据库配置
    database_url: str = "sqlite:///./insightreader_v2.db"

    # JWT 认证配置
    secret_key: str = "" # 用于签名 JWT token
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7天

    # AI 配置
    max_context_length: int = 2000
    default_model: str = "gpt-4o"
    simple_model: str = "gpt-4o-mini"
    reasoning_model: str = "deepseek-reasoner"  # 推理模型（支持思维链）
    max_tokens: int = 1000
    temperature: float = 0.7

    # CORS
    cors_origins: list[str] = []

    # Google OAuth
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8888/api/v1/auth/google/callback"

    # GitHub OAuth
    github_client_id: str = ""
    github_client_secret: str = ""
    github_redirect_uri: str = "http://localhost:8000/api/v1/auth/github/callback"

    # Email (Magic Links)
    mail_username: str = ""
    mail_password: str = ""
    mail_from: str = ""
    mail_server: str = "smtp.gmail.com"
    mail_port: int = 587
    mail_tls: bool = True
    mail_ssl: bool = False

    # Magic Link Settings
    magic_link_expiration_minutes: int = 15
    frontend_url: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 全局配置实例
settings = Settings()
