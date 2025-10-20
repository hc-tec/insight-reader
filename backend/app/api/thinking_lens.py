"""
思维透镜 API 路由
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.thinking_lens_service import ThinkingLensService
from app.services.meta_analysis_service import MetaAnalysisService
from app.models.models import Article, MetaAnalysis
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


class ApplyLensRequest(BaseModel):
    meta_analysis_id: int
    lens_type: str  # 'argument_structure' | 'author_stance'
    full_text: str
    language: str = "zh"
    force_reanalyze: bool = False


@router.post("/api/v1/thinking-lens/apply")
async def apply_lens(
    request: ApplyLensRequest,
    db: Session = Depends(get_db)
):
    """
    应用思维透镜

    Args:
        request: 透镜请求
        db: 数据库会话

    Returns:
        透镜分析结果
    """

    # 验证 lens_type
    valid_types = ['argument_structure', 'author_stance']
    if request.lens_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"无效的透镜类型。支持的类型: {', '.join(valid_types)}"
        )

    service = ThinkingLensService(db)

    try:
        result = await service.apply_lens(
            meta_analysis_id=request.meta_analysis_id,
            lens_type=request.lens_type,
            full_text=request.full_text,
            language=request.language,
            force_reanalyze=request.force_reanalyze
        )

        return {
            "status": "success",
            "lens_result": result
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"透镜分析失败: {str(e)}")


@router.get("/api/v1/thinking-lens/{meta_analysis_id}/{lens_type}")
async def get_lens_result(
    meta_analysis_id: int,
    lens_type: str,
    db: Session = Depends(get_db)
):
    """
    获取透镜分析结果

    Args:
        meta_analysis_id: 元信息分析ID
        lens_type: 透镜类型
        db: 数据库会话

    Returns:
        透镜分析结果或null
    """

    # 验证 lens_type
    valid_types = ['argument_structure', 'author_stance']
    if lens_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"无效的透镜类型。支持的类型: {', '.join(valid_types)}"
        )

    service = ThinkingLensService(db)
    result = service.get_lens_result(meta_analysis_id, lens_type)

    if result is None:
        return {
            "exists": False,
            "lens_result": None
        }

    return {
        "exists": True,
        "lens_result": result
    }


@router.get("/api/v1/articles/{article_id}/thinking-lens/{lens_type}")
async def get_lens_by_article(
    article_id: int,
    lens_type: str,
    force_reanalyze: bool = False,
    db: Session = Depends(get_db)
):
    """
    通过文章ID获取或生成透镜分析结果

    工作流程：
    1. 获取文章
    2. 确保有 meta_analysis 记录
    3. 检查是否已有透镜结果
    4. 没有则生成新的透镜分析

    Args:
        article_id: 文章ID
        lens_type: 透镜类型 ('argument_structure' | 'author_stance')
        force_reanalyze: 是否强制重新分析
        db: 数据库会话

    Returns:
        透镜分析结果
    """
    # 验证 lens_type
    valid_types = ['argument_structure', 'author_stance']
    if lens_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"无效的透镜类型。支持的类型: {', '.join(valid_types)}"
        )

    # 1. 获取文章
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")

    # 2. 确保有 meta_analysis 记录
    meta_analysis = db.query(MetaAnalysis).filter(
        MetaAnalysis.article_id == article_id
    ).first()

    if not meta_analysis:
        # 创建基础的 meta_analysis 记录（如果需要的话）
        # 或者调用 MetaAnalysisService 进行完整分析
        meta_service = MetaAnalysisService(db)
        try:
            meta_result = await meta_service.analyze_article(
                title=article.title or "",
                author=article.author or "",
                publish_date=article.publish_date.isoformat() if article.publish_date else datetime.utcnow().isoformat(),
                content=article.content,
                user_id=article.user_id,
                source_url=article.source_url,
                language=article.language
            )
            meta_analysis_id = meta_result['id']
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"元信息分析失败: {str(e)}"
            )
    else:
        meta_analysis_id = meta_analysis.id

    # 3. 应用透镜分析
    lens_service = ThinkingLensService(db)

    try:
        result = await lens_service.apply_lens(
            meta_analysis_id=meta_analysis_id,
            lens_type=lens_type,
            full_text=article.content,
            language=article.language,
            force_reanalyze=force_reanalyze
        )

        return {
            "status": "success",
            "lens_result": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"透镜分析失败: {str(e)}"
        )
