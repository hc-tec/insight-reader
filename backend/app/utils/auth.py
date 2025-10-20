"""JWT 认证工具"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.db.database import get_db
from app.models.models import User

# OAuth2 密码bearer令牌
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire})

    print(f"  生成 Token 使用的 SECRET_KEY 长度: {len(settings.secret_key)}")
    print(f"  生成 Token 使用的算法: {settings.algorithm}")

    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """验证令牌并返回payload"""
    try:
        print(f"  验证使用的 SECRET_KEY 长度: {len(settings.secret_key)}")
        print(f"  验证使用的算法: {settings.algorithm}")
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError as e:
        print(f"  JWT 错误详情: {e}")
        return None


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """获取当前用户（依赖注入）"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭证",
        headers={"WWW-Authenticate": "Bearer"},
    )

    print(f"🔍 验证 Token:")
    print(f"  收到 Token (前50字符): {token[:50]}...")

    payload = verify_token(token)
    if payload is None:
        print(f"  ❌ Token 验证失败: 无效的签名或格式")
        raise credentials_exception

    print(f"  ✅ Token 验证成功")
    print(f"  Payload: {payload}")

    user_id_str: str = payload.get("sub")
    if user_id_str is None:
        print(f"  ❌ Payload 中没有 'sub' 字段")
        raise credentials_exception

    # 将字符串转换为整数
    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        print(f"  ❌ 'sub' 字段不是有效的用户ID: {user_id_str}")
        raise credentials_exception

    print(f"  查询用户 ID: {user_id}")

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        print(f"  ❌ 数据库中未找到用户 ID {user_id}")
        raise credentials_exception

    if not user.is_active:
        print(f"  ❌ 用户已被禁用")
        raise HTTPException(status_code=400, detail="用户已被禁用")

    print(f"  ✅ 找到用户: {user.email}")
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前激活用户"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="用户未激活")
    return current_user
