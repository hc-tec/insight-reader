"""
示例文章预生成服务
为示例文章预先生成所有类型的分析结果

**最佳实践：**
- 复用现有服务（DRY原则）
- 事务管理（确保原子性）
- 详细的日志记录
- 错误恢复机制
"""

import logging
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.models import Article, AnalysisReport, MetaAnalysis
from app.services.unified_analysis_service import UnifiedAnalysisService
from app.services.meta_analysis_service import MetaAnalysisService
from typing import Dict, Optional
import asyncio

logger = logging.getLogger(__name__)


class DemoPregenerationService:
    """示例文章预生成服务"""

    def __init__(self):
        """初始化服务"""
        # 不在这里初始化服务，而是在需要时创建
        pass

    async def pregenerate_all(
        self,
        article_id: int,
        db: Session,
        force_regenerate: bool = False
    ) -> Dict:
        """
        为示例文章预生成所有分析

        Args:
            article_id: 文章ID
            db: 数据库会话
            force_regenerate: 是否强制重新生成（即使已存在）

        Returns:
            生成结果摘要
            {
                "article_id": int,
                "status": "success" | "partial" | "failed",
                "generated": ["unified_analysis", "meta_analysis"],
                "errors": ["..."],
                "metadata": {...}
            }

        **最佳实践：**
        - 使用事务保证数据一致性
        - 即使部分失败也保存成功的结果
        - 详细的错误信息
        """
        logger.info(f"[PreGen] 开始预生成文章 {article_id} 的所有分析")

        result = {
            "article_id": article_id,
            "status": "success",
            "generated": [],
            "errors": [],
            "metadata": {}
        }

        try:
            # 1. 验证文章存在
            article = db.query(Article).filter(Article.id == article_id).first()

            if not article:
                logger.error(f"[PreGen] 文章不存在: {article_id}")
                result["status"] = "failed"
                result["errors"].append("文章不存在")
                return result

            if not article.is_demo:
                logger.warning(f"[PreGen] 文章 {article_id} 不是示例文章")
                result["errors"].append("文章未标记为示例")

            # 2. 生成统一深度分析
            try:
                await self._generate_unified_analysis(
                    article,
                    db,
                    force_regenerate,
                    result
                )
            except Exception as e:
                logger.error(f"[PreGen] 统一分析生成失败: {e}", exc_info=True)
                result["errors"].append(f"统一分析失败: {str(e)}")

            # 3. 生成元视角分析
            try:
                await self._generate_meta_analysis(
                    article,
                    db,
                    force_regenerate,
                    result
                )
            except Exception as e:
                logger.error(f"[PreGen] 元视角分析生成失败: {e}", exc_info=True)
                result["errors"].append(f"元视角分析失败: {str(e)}")

            # 4. 确定最终状态
            if result["errors"]:
                result["status"] = "partial" if result["generated"] else "failed"
            else:
                result["status"] = "success"

            logger.info(
                f"[PreGen] 文章 {article_id} 预生成完成，"
                f"状态: {result['status']}, "
                f"已生成: {result['generated']}, "
                f"错误: {len(result['errors'])}"
            )

            return result

        except Exception as e:
            logger.error(f"[PreGen] 预生成过程失败: {e}", exc_info=True)
            result["status"] = "failed"
            result["errors"].append(f"预生成失败: {str(e)}")
            return result

    async def _generate_unified_analysis(
        self,
        article: Article,
        db: Session,
        force: bool,
        result: Dict
    ):
        """
        生成统一深度分析（Sparks + 深度洞察 + 追问）

        **最佳实践：**
        - 检查是否已存在（除非强制重新生成）
        - 使用独立事务（部分失败不影响其他分析）
        """
        # 检查是否已存在
        existing = db.query(AnalysisReport).filter(
            AnalysisReport.article_id == article.id
        ).first()

        if existing and not force:
            logger.info(f"[PreGen] 统一分析已存在，跳过（article_id={article.id}）")
            result["generated"].append("unified_analysis_cached")
            return

        if existing and force:
            logger.info(f"[PreGen] 强制重新生成统一分析（article_id={article.id}）")
            db.delete(existing)
            db.commit()

        # 创建服务实例（每次调用时创建）
        unified_service = UnifiedAnalysisService()

        # 调用统一分析服务
        logger.info(f"[PreGen] 开始生成统一分析（article_id={article.id}）")
        analysis_result = await unified_service.analyze_article(
            article.content,
            article.title
        )

        # 解析报告数据
        report_data = analysis_result.get("report", {})
        metadata = analysis_result.get("metadata", {})

        # 保存到数据库
        analysis_report = AnalysisReport(
            article_id=article.id,
            sparks=report_data.get("sparks", []),
            deep_insights=report_data.get("deep_insights", []),
            follow_up_questions=report_data.get("follow_up_questions", []),
            model_used=metadata.get("model"),
            processing_time_ms=metadata.get("processing_time_ms")
        )

        db.add(analysis_report)
        db.commit()

        result["generated"].append("unified_analysis")
        result["metadata"]["unified_analysis"] = metadata

        logger.info(
            f"[PreGen] 统一分析生成成功（article_id={article.id}），"
            f"Sparks: {len(report_data.get('sparks', []))}, "
            f"洞察: {len(report_data.get('deep_insights', []))}"
        )

    async def _generate_meta_analysis(
        self,
        article: Article,
        db: Session,
        force: bool,
        result: Dict
    ):
        """
        生成元视角分析

        **最佳实践：**
        - 依赖统一分析结果（如果没有则跳过或警告）
        - 独立事务管理
        """
        # 检查是否已存在
        existing = db.query(MetaAnalysis).filter(
            MetaAnalysis.article_id == article.id
        ).first()

        if existing and not force:
            logger.info(f"[PreGen] 元视角分析已存在，跳过（article_id={article.id}）")
            result["generated"].append("meta_analysis_cached")
            return

        if existing and force:
            logger.info(f"[PreGen] 强制重新生成元视角分析（article_id={article.id}）")
            db.delete(existing)
            db.commit()

        # 检查是否有统一分析报告（元视角依赖它）
        analysis_report = db.query(AnalysisReport).filter(
            AnalysisReport.article_id == article.id
        ).first()

        if not analysis_report:
            logger.warning(
                f"[PreGen] 元视角分析需要统一分析报告作为输入，"
                f"但文章 {article.id} 没有统一分析，跳过"
            )
            result["errors"].append("元视角分析需要先生成统一分析")
            return

        # 创建服务实例（每次调用时创建，传入 db）
        meta_service = MetaAnalysisService(db)

        # 调用元视角分析服务
        logger.info(f"[PreGen] 开始生成元视角分析（article_id={article.id}）")

        # 准备参数
        publish_date_str = article.publish_date.isoformat() if article.publish_date else datetime.utcnow().isoformat()

        meta_result = await meta_service.analyze_article(
            title=article.title,
            author=article.author or "未知作者",
            publish_date=publish_date_str,
            content=article.content,
            user_id=article.user_id,
            source_url=article.source_url,
            language=article.language,
            force_reanalyze=force  # 如果强制重新生成，则强制重新分析
        )

        result["generated"].append("meta_analysis")

        # 从返回结果中提取元洞察数量
        meta_insights = meta_result.get("meta_insights", [])
        result["metadata"]["meta_analysis"] = {
            "meta_insights_count": len(meta_insights)
        }

        logger.info(
            f"[PreGen] 元视角分析生成成功（article_id={article.id}），"
            f"元洞察数: {len(meta_insights)}"
        )


# 全局单例
pregeneration_service = DemoPregenerationService()
