"""FastAPI 主应用"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.config import settings
from app.api import insights, auth, collections, sparks, dashboard, analytics, meta_analysis, thinking_lens, articles, insight_history, sse, unified_analysis, preferences
from app.db.database import init_db

# 创建 FastAPI 应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="上下文智能探针 API - V2.0 版本"
)

# Session 中间件（OAuth 需要）
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key,
    session_cookie="insightreader_session",
    max_age=3600,  # 1小时
    same_site="lax",
    https_only=False  # 开发环境设为 False，生产环境改为 True
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 启动时初始化数据库
@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据库"""
    init_db()
    print("✅ 数据库初始化完成")

# 注册路由
app.include_router(insights.router, prefix="/api/v1", tags=["insights"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(collections.router, prefix="/api/v1/collections", tags=["collections"])
app.include_router(sparks.router, tags=["sparks"])
app.include_router(dashboard.router, tags=["dashboard"])
app.include_router(analytics.router, tags=["analytics"])
app.include_router(meta_analysis.router, tags=["meta-analysis"])
app.include_router(thinking_lens.router, tags=["thinking-lens"])
app.include_router(articles.router, tags=["articles"])
app.include_router(insight_history.router, tags=["insight-history"])
app.include_router(sse.router, tags=["sse"])
app.include_router(unified_analysis.router, tags=["unified-analysis"])
app.include_router(preferences.router, tags=["preferences"])


@app.get("/")
async def root():
    """根路由"""
    return {
        "message": "InsightReader API",
        "version": settings.app_version,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "version": settings.app_version
    }
