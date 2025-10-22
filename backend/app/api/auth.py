"""用户认证 API - 无密码设计"""
import logging

logger = logging.getLogger(__name__)

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime
from urllib.parse import urlencode

from app.db.database import get_db
from app.models.models import User
from app.schemas.user import UserResponse, Token, MagicLinkRequest
from app.utils.auth import create_access_token, get_current_active_user
from app.services.oauth_service import oauth, get_google_user_info, get_github_user_info
from app.services.magic_link_service import (
    create_magic_link,
    send_magic_link_email,
    verify_magic_link
)
from app.config import settings

router = APIRouter()


# ==================== Google OAuth ====================

@router.get("/google/login")
async def google_login(request: Request):
    """Google OAuth 登录 - 重定向到 Google"""
    redirect_uri = settings.google_redirect_uri
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    """Google OAuth 回调"""
    try:
        # 获取 access token
        token = await oauth.google.authorize_access_token(request)

        # 获取用户信息
        user_info = await get_google_user_info(token)

        if not user_info or not user_info.get('email'):
            # 重定向到前端错误页面
            return RedirectResponse(
                url=f"{settings.frontend_url}/login?error=无法从Google获取用户信息"
            )

        # 查找或创建用户
        user = db.query(User).filter(User.email == user_info['email']).first()

        if user:
            # 更新登录时间和信息
            user.last_login = datetime.utcnow()
            if not user.oauth_provider:
                user.oauth_provider = 'google'
                user.oauth_id = user_info['id']
            if user_info.get('avatar'):
                user.avatar_url = user_info['avatar']
        else:
            # 创建新用户
            user = User(
                email=user_info['email'],
                username=user_info.get('name'),
                oauth_provider='google',
                oauth_id=user_info['id'],
                avatar_url=user_info.get('avatar'),
                is_active=True
            )
            db.add(user)

        db.commit()
        db.refresh(user)

        # 生成 JWT token（sub 必须是字符串）
        access_token = create_access_token(data={"sub": str(user.id)})

        # 调试日志
        logger.info(f" Google 登录成功:")
        logger.info(f"  用户ID: {user.id}")
        logger.info(f"  邮箱: {user.email}")
        logger.info(f"  Token (前50字符): {access_token[:50]}...")

        # 重定向到前端，带上 token 和用户信息（hash 路由）
        redirect_url = f"{settings.frontend_url}/#/auth/callback?token={access_token}"
        return RedirectResponse(url=redirect_url)

    except Exception as e:
        # 重定向到前端错误页面（hash 路由）
        error_msg = f"Google登录失败: {str(e)}"
        return RedirectResponse(
            url=f"{settings.frontend_url}/#/login?error={error_msg}"
        )


# ==================== GitHub OAuth ====================

@router.get("/github/login")
async def github_login(request: Request):
    """GitHub OAuth 登录 - 重定向到 GitHub"""
    redirect_uri = settings.github_redirect_uri
    return await oauth.github.authorize_redirect(request, redirect_uri)


@router.get("/github/callback")
async def github_callback(request: Request, db: Session = Depends(get_db)):
    """GitHub OAuth 回调"""
    try:
        # 获取 access token
        token = await oauth.github.authorize_access_token(request)

        # 获取用户信息
        user_info = await get_github_user_info(token)

        if not user_info or not user_info.get('email'):
            # 重定向到前端错误页面
            return RedirectResponse(
                url=f"{settings.frontend_url}/login?error=无法从GitHub获取用户信息（请确保邮箱公开）"
            )

        # 查找或创建用户
        user = db.query(User).filter(User.email == user_info['email']).first()

        if user:
            # 更新登录时间和信息
            user.last_login = datetime.utcnow()
            if not user.oauth_provider:
                user.oauth_provider = 'github'
                user.oauth_id = user_info['id']
            if user_info.get('avatar'):
                user.avatar_url = user_info['avatar']
        else:
            # 创建新用户
            user = User(
                email=user_info['email'],
                username=user_info.get('name'),
                oauth_provider='github',
                oauth_id=user_info['id'],
                avatar_url=user_info.get('avatar'),
                is_active=True
            )
            db.add(user)

        db.commit()
        db.refresh(user)

        # 生成 JWT token（sub 必须是字符串）
        access_token = create_access_token(data={"sub": str(user.id)})

        # 重定向到前端，带上 token（hash 路由）
        redirect_url = f"{settings.frontend_url}/#/auth/callback?token={access_token}"
        return RedirectResponse(url=redirect_url)

    except Exception as e:
        # 重定向到前端错误页面（hash 路由）
        error_msg = f"GitHub登录失败: {str(e)}"
        return RedirectResponse(
            url=f"{settings.frontend_url}/#/login?error={error_msg}"
        )


# ==================== Magic Link ====================

@router.post("/magic-link/request")
async def request_magic_link(
    request_data: MagicLinkRequest,
    db: Session = Depends(get_db)
):
    """请求魔法链接"""
    email = request_data.email

    # 检查邮件配置是否完整
    if not settings.mail_username or not settings.mail_password:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="邮件服务未配置"
        )

    try:
        # 创建魔法链接 token
        token = await create_magic_link(email, db)

        # 发送邮件
        await send_magic_link_email(email, token)

        return {
            "message": "魔法链接已发送到你的邮箱",
            "email": email
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"发送邮件失败: {str(e)}"
        )


@router.get("/magic-link/verify")
async def verify_magic_link_endpoint(
    token: str,
    db: Session = Depends(get_db)
):
    """验证魔法链接并登录"""
    # 验证 token
    email = await verify_magic_link(token, db)

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="魔法链接无效或已过期"
        )

    # 查找或创建用户
    user = db.query(User).filter(User.email == email).first()

    if user:
        # 更新登录时间
        user.last_login = datetime.utcnow()
    else:
        # 创建新用户
        user = User(
            email=email,
            oauth_provider=None,  # 魔法链接登录
            oauth_id=None,
            is_active=True
        )
        db.add(user)

    db.commit()
    db.refresh(user)

    # 生成 JWT token（sub 必须是字符串）
    access_token = create_access_token(data={"sub": str(user.id)})

    return Token(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


# ==================== 通用接口 ====================

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """获取当前用户信息"""
    return UserResponse.model_validate(current_user)


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_active_user)):
    """登出（前端删除 token 即可）"""
    return {"message": "登出成功"}
