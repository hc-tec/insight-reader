# -*- coding: utf-8 -*-
"""
文章深度分析异步任务
"""

from app.celery_app import celery_app
from app.services.unified_analysis_service import UnifiedAnalysisService
from app.db.database import get_db
from app.models.models import Article, AnalysisReport
from app.api.sse import notify_analysis_complete, notify_analysis_progress
import asyncio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def analyze_article_task(self, article_id: int, user_id: int = None):
    """
    异步分析文章任务

    Args:
        self: Celery 任务实例
        article_id: 文章 ID
        user_id: 用户 ID（用于发送 SSE 通知）

    Returns:
        分析报告 ID
    """
    logger.info(f"🚀 开始分析文章 {article_id}...")

    db = next(get_db())

    try:
        # 1. 获取文章
        article = db.query(Article).filter(Article.id == article_id).first()
        if not article:
            raise ValueError(f"文章不存在: {article_id}")

        # 2. 创建或更新分析报告记录
        report = db.query(AnalysisReport).filter(
            AnalysisReport.article_id == article_id
        ).first()

        if not report:
            report = AnalysisReport(
                article_id=article_id,
                status='processing'
            )
            db.add(report)
        else:
            report.status = 'processing'
            report.retry_count += 1

        db.commit()
        logger.info(f"📝 分析报告记录已创建/更新，状态: processing")

        # 3. 发送进度通知（如果有用户ID）
        if user_id:
            asyncio.run(notify_analysis_progress(
                user_id, article_id, "extracting_concepts", 20
            ))

        # 4. 调用 AI 分析服务
        analysis_service = UnifiedAnalysisService()
        result = asyncio.run(analysis_service.analyze_article(
            article.content,
            article.title
        ))

        logger.info(f"✅ AI 分析完成")

        # 5. 发送进度通知
        if user_id:
            asyncio.run(notify_analysis_progress(
                user_id, article_id, "finalizing", 90
            ))

        # 6. 保存分析结果
        report.report_data = result['report']
        report.model_used = result['metadata']['model']
        report.tokens_used = result['metadata']['tokens']
        report.processing_time_ms = result['metadata']['processing_time_ms']
        report.status = 'completed'
        report.completed_at = datetime.utcnow()
        report.error_message = None

        db.commit()
        logger.info(f"💾 分析报告已保存到数据库")

        # 7. 发送完成通知
        if user_id:
            asyncio.run(notify_analysis_complete(user_id, article_id))
            logger.info(f"📬 已通知用户 {user_id} 分析完成")

        return report.id

    except Exception as e:
        logger.error(f"❌ 分析失败: {str(e)}")

        # 更新报告状态为失败
        if 'report' in locals():
            report.status = 'failed'
            report.error_message = str(e)
            db.commit()

        # 重试逻辑
        if self.request.retries < self.max_retries:
            logger.error(f"🔄 准备重试 (第 {self.request.retries + 1} 次)...")
            raise self.retry(exc=e, countdown=60)  # 60秒后重试
        else:
            logger.error(f"❌ 已达到最大重试次数，任务失败")
            raise

    finally:
        db.close()


@celery_app.task
def batch_analyze_articles(article_ids: list, user_id: int = None):
    """
    批量分析文章

    Args:
        article_ids: 文章 ID 列表
        user_id: 用户 ID

    Returns:
        成功分析的文章数量
    """
    logger.info(f"📚 开始批量分析 {len(article_ids)} 篇文章...")

    success_count = 0
    for article_id in article_ids:
        try:
            analyze_article_task.delay(article_id, user_id)
            success_count += 1
        except Exception as e:
            logger.error(f"❌ 文章 {article_id} 分析任务创建失败: {str(e)}")

    logger.info(f"✅ 批量分析任务创建完成，成功: {success_count}/{len(article_ids)}")
    return success_count
