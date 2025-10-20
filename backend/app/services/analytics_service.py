"""分析服务 - 处理火花点击和好奇心指纹"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from collections import defaultdict, Counter
import re

from app.models.models import SparkClick, CuriosityFingerprint, InsightCard


class AnalyticsService:
    """分析服务"""

    def __init__(self, db: Session):
        self.db = db

    def record_spark_click(
        self,
        user_id: int,
        spark_type: str,
        spark_text: str,
        article_id: Optional[int] = None
    ) -> SparkClick:
        """
        记录火花点击

        Args:
            user_id: 用户 ID
            spark_type: 火花类型（concept/argument）
            spark_text: 火花文本
            article_id: 文章 ID（可选）

        Returns:
            SparkClick 对象
        """
        click = SparkClick(
            user_id=user_id,
            spark_type=spark_type,
            spark_text=spark_text,
            article_id=article_id,
            clicked_at=datetime.utcnow()
        )
        self.db.add(click)
        self.db.commit()
        self.db.refresh(click)

        print(f"✅ 记录火花点击: {spark_type} - {spark_text[:20]}...")

        # 异步更新好奇心指纹（可选）
        # 为了性能，这里可以使用异步任务队列（Celery）
        # 目前直接同步更新
        self._update_curiosity_fingerprint(user_id)

        return click

    def get_curiosity_fingerprint(self, user_id: int) -> Dict:
        """
        获取用户的好奇心指纹

        Args:
            user_id: 用户 ID

        Returns:
            好奇心指纹数据
        """
        # 先尝试从缓存中获取
        fingerprint = self.db.query(CuriosityFingerprint).filter(
            CuriosityFingerprint.user_id == user_id
        ).first()

        # 如果缓存存在且最近更新（1小时内），直接返回
        if fingerprint:
            time_diff = datetime.utcnow() - fingerprint.last_updated
            if time_diff.total_seconds() < 3600:  # 1小时
                return {
                    "spark_distribution": fingerprint.spark_distribution,
                    "time_series": fingerprint.time_series,
                    "topic_cloud": fingerprint.topic_cloud,
                    "last_updated": fingerprint.last_updated.isoformat()
                }

        # 否则，重新计算
        return self._compute_curiosity_fingerprint(user_id)

    def _update_curiosity_fingerprint(self, user_id: int):
        """更新好奇心指纹缓存"""
        data = self._compute_curiosity_fingerprint(user_id)

        # 查找或创建缓存记录
        fingerprint = self.db.query(CuriosityFingerprint).filter(
            CuriosityFingerprint.user_id == user_id
        ).first()

        if fingerprint:
            # 更新现有记录
            fingerprint.spark_distribution = data["spark_distribution"]
            fingerprint.time_series = data["time_series"]
            fingerprint.topic_cloud = data["topic_cloud"]
            fingerprint.last_updated = datetime.utcnow()
        else:
            # 创建新记录
            fingerprint = CuriosityFingerprint(
                user_id=user_id,
                spark_distribution=data["spark_distribution"],
                time_series=data["time_series"],
                topic_cloud=data["topic_cloud"]
            )
            self.db.add(fingerprint)

        self.db.commit()
        print(f"✅ 好奇心指纹已更新: User {user_id}")

    def _compute_curiosity_fingerprint(self, user_id: int) -> Dict:
        """
        计算好奇心指纹（实时计算）

        Args:
            user_id: 用户 ID

        Returns:
            好奇心指纹数据
        """
        # 查询最近 30 天的火花点击
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        clicks = self.db.query(SparkClick).filter(
            SparkClick.user_id == user_id,
            SparkClick.clicked_at >= thirty_days_ago
        ).order_by(SparkClick.clicked_at.desc()).all()

        # 1. 火花类型分布
        spark_distribution = defaultdict(int)
        for click in clicks:
            spark_distribution[click.spark_type] += 1

        # 2. 时序分析（按天聚合）
        time_series = self._compute_time_series(clicks)

        # 3. 话题云图（从火花文本中提取关键词）
        topic_cloud = self._compute_topic_cloud(clicks, user_id)

        return {
            "spark_distribution": dict(spark_distribution),
            "time_series": time_series,
            "topic_cloud": topic_cloud,
            "last_updated": datetime.utcnow().isoformat()
        }

    def _compute_time_series(self, clicks: List[SparkClick]) -> List[Dict]:
        """
        计算时序数据（最近 30 天）

        Args:
            clicks: 火花点击列表

        Returns:
            时序数据数组
        """
        # 按日期分组
        daily_counts = defaultdict(lambda: defaultdict(int))

        for click in clicks:
            date_str = click.clicked_at.date().isoformat()
            daily_counts[date_str][click.spark_type] += 1

        # 生成最近 30 天的数据（填充缺失日期）
        result = []
        for i in range(30):
            date = (datetime.utcnow() - timedelta(days=i)).date()
            date_str = date.isoformat()

            result.append({
                "date": date_str,
                "counts": dict(daily_counts[date_str]) if date_str in daily_counts else {}
            })

        # 倒序（最早的日期在前）
        result.reverse()
        return result

    def _compute_topic_cloud(self, clicks: List[SparkClick], user_id: int) -> List[Dict]:
        """
        计算话题云图（从火花文本和洞察中提取关键词）

        Args:
            clicks: 火花点击列表
            user_id: 用户 ID

        Returns:
            话题列表
        """
        # 方法 1: 从火花文本中提取（简单版）
        # 统计所有火花文本中的高频词
        all_text = " ".join([click.spark_text for click in clicks])

        # 简单的关键词提取（去除停用词）
        stopwords = {"的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一", "个", "上", "也"}

        # 使用正则提取中文词汇（2-10 字）
        keywords = re.findall(r'[\u4e00-\u9fa5]{2,10}', all_text)

        # 过滤停用词
        keywords = [kw for kw in keywords if kw not in stopwords]

        # 统计频率
        keyword_counts = Counter(keywords)

        # 取 TOP 20
        top_keywords = keyword_counts.most_common(20)

        # 方法 2: 从用户的洞察中提取领域标签（更准确，但需要洞察有 domain 字段）
        # 这里先使用简单方法

        # 归一化权重（最高频的词权重为 1.0）
        if not top_keywords:
            return []

        max_count = top_keywords[0][1]
        result = [
            {
                "topic": keyword,
                "count": count,
                "weight": round(count / max_count, 2)
            }
            for keyword, count in top_keywords
        ]

        return result

    def get_spark_stats(self, user_id: int, days: int = 30) -> Dict:
        """
        获取火花统计数据

        Args:
            user_id: 用户 ID
            days: 统计天数（默认 30 天）

        Returns:
            统计数据
        """
        start_date = datetime.utcnow() - timedelta(days=days)

        clicks = self.db.query(SparkClick).filter(
            SparkClick.user_id == user_id,
            SparkClick.clicked_at >= start_date
        ).all()

        # 按类型统计
        type_counts = defaultdict(int)
        for click in clicks:
            type_counts[click.spark_type] += 1

        # 计算主导类型
        dominant_type = None
        if type_counts:
            dominant_type = max(type_counts.items(), key=lambda x: x[1])[0]

        return {
            "total_clicks": len(clicks),
            "type_counts": dict(type_counts),
            "dominant_type": dominant_type,
            "period_days": days
        }
