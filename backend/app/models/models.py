"""数据库模型定义"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import hashlib

Base = declarative_base()


class User(Base):
    """用户表 - 无密码设计"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), nullable=True)  # 可选，首次登录后设置

    # OAuth 登录信息
    oauth_provider = Column(String(50), nullable=True)  # google, github, null(魔法链接)
    oauth_id = Column(String(255), nullable=True)  # OAuth提供商的用户ID

    # 用户信息
    avatar_url = Column(String(500), nullable=True)

    # 状态
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # 关系
    insights = relationship("InsightCard", back_populates="user", cascade="all, delete-orphan")
    knowledge_nodes = relationship("KnowledgeNode", back_populates="user", cascade="all, delete-orphan")
    knowledge_edges = relationship("KnowledgeEdge", back_populates="user", cascade="all, delete-orphan")
    spark_clicks = relationship("SparkClick", back_populates="user", cascade="all, delete-orphan")
    curiosity_fingerprint = relationship("CuriosityFingerprint", back_populates="user", uselist=False, cascade="all, delete-orphan")
    analysis_preferences = relationship("UserAnalysisPreferences", back_populates="user", uselist=False, cascade="all, delete-orphan")


class MagicLink(Base):
    """魔法链接表 - 用于邮箱登录"""
    __tablename__ = "magic_links"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), index=True, nullable=False)
    token = Column(String(255), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False, nullable=False)


class InsightCard(Base):
    """洞察卡片表"""
    __tablename__ = "insight_cards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # 文章信息
    article_title = Column(String(500), nullable=True)
    article_content = Column(Text, nullable=True)

    # 选中内容和上下文
    selected_text = Column(Text, nullable=False)
    context = Column(Text, nullable=True)

    # 意图和问题
    intent = Column(String(50), nullable=False)  # explain, analyze, counter
    custom_question = Column(String(500), nullable=True)

    # AI 生成的洞察
    insight = Column(Text, nullable=False)

    # 元数据
    model_used = Column(String(100), nullable=True)
    tokens = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # 标签
    tags = Column(String(500), nullable=True)

    # 关系
    user = relationship("User", back_populates="insights")


class KnowledgeNode(Base):
    """知识节点表 - 用于知识图谱"""
    __tablename__ = "knowledge_nodes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # 节点信息
    label = Column(String(255), nullable=False)  # 概念名称
    type = Column(String(50), nullable=False)  # concept / entity
    size = Column(Integer, default=1)  # 节点大小（基于关联洞察数量）
    color = Column(String(7), nullable=True)  # 十六进制颜色
    domain = Column(String(100), nullable=True, index=True)  # 所属领域

    # 关联信息
    insight_id = Column(Integer, ForeignKey("insight_cards.id"), nullable=True)
    review_count = Column(Integer, default=0)  # 被回顾次数

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系
    user = relationship("User", back_populates="knowledge_nodes")


class KnowledgeEdge(Base):
    """知识关系表 - 用于知识图谱"""
    __tablename__ = "knowledge_edges"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # 关系连接
    source_id = Column(String(36), ForeignKey("knowledge_nodes.id"), nullable=False, index=True)
    target_id = Column(String(36), ForeignKey("knowledge_nodes.id"), nullable=False, index=True)

    # 关系信息
    type = Column(String(50), nullable=False)  # related / contrast / depends_on
    weight = Column(Float, default=0.5)  # 关系强度 (0-1)
    label = Column(String(255), nullable=True)  # 关系描述

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关系
    user = relationship("User", back_populates="knowledge_edges")


class SparkClick(Base):
    """火花点击日志表 - 用于好奇心指纹分析"""
    __tablename__ = "spark_clicks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # 火花信息
    spark_type = Column(String(50), nullable=False)  # concept / argument / entity
    spark_text = Column(Text, nullable=False)
    article_id = Column(Integer, nullable=True)  # 关联的文章 ID（如果有）

    # 时间戳
    clicked_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # 关系
    user = relationship("User", back_populates="spark_clicks")


class CuriosityFingerprint(Base):
    """好奇心指纹缓存表"""
    __tablename__ = "curiosity_fingerprints"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)

    # 缓存数据（JSON 格式）
    spark_distribution = Column(JSON, nullable=False)  # {"concept": 120, "argument": 85}
    time_series = Column(JSON, nullable=False)  # [{"date": "2025-01-01", "counts": {...}}]
    topic_cloud = Column(JSON, nullable=False)  # [{"topic": "AI", "count": 45}]

    # 时间戳
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系
    user = relationship("User", back_populates="curiosity_fingerprint")


class Article(Base):
    """文章表 - 保存用户阅读的文章"""
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # 可选，支持匿名阅读

    # 文章基本信息
    title = Column(String(500), nullable=False)
    author = Column(String(200), nullable=True)
    source_url = Column(String(1000), nullable=True)  # 文章来源URL
    publish_date = Column(DateTime, nullable=True)

    # 文章内容
    content = Column(Text, nullable=False)  # 完整文章内容
    content_hash = Column(String(64), index=True, nullable=False)  # MD5哈希，用于去重

    # 元数据
    language = Column(String(10), default='zh', nullable=False)
    word_count = Column(Integer, nullable=True)  # 字数统计
    insight_count = Column(Integer, default=0, nullable=False)  # 洞察次数

    # 示例文章标记
    is_demo = Column(Boolean, default=False, nullable=False, index=True)  # 是否为示例文章
    demo_order = Column(Integer, nullable=True)  # 示例文章展示顺序（NULL表示非示例）

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    last_read_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    read_count = Column(Integer, default=1, nullable=False)  # 阅读次数

    # 关系
    user = relationship("User", backref="articles")
    meta_analysis = relationship("MetaAnalysis", back_populates="article", uselist=False, cascade="all, delete-orphan")
    insight_history = relationship("InsightHistory", back_populates="article", cascade="all, delete-orphan")
    analysis_report = relationship("AnalysisReport", back_populates="article", uselist=False, cascade="all, delete-orphan")


class AnalysisReport(Base):
    """统一深度分析报告表 - 存储文章的完整AI分析结果"""
    __tablename__ = "analysis_reports"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False, unique=True, index=True)

    # 分析状态
    status = Column(String(20), default='pending', nullable=False, index=True)
    # 状态值: pending, processing, completed, failed

    # 分析报告数据 (JSONB格式)
    report_data = Column(JSON, nullable=True)
    # 报告结构见设计文档中的 JSON Schema

    # 版本控制
    analysis_version = Column(String(10), default='1.0', nullable=False)

    # LLM 元信息
    model_used = Column(String(50), nullable=True)  # 使用的模型名称
    tokens_used = Column(Integer, nullable=True)  # 消耗的 token 数
    processing_time_ms = Column(Integer, nullable=True)  # 处理时间（毫秒）

    # 错误信息
    error_message = Column(Text, nullable=True)  # 错误详情
    retry_count = Column(Integer, default=0, nullable=False)  # 重试次数

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)  # 完成时间

    # 关系
    article = relationship("Article", back_populates="analysis_report")


class InsightHistory(Base):
    """洞察历史表 - 记录用户的每次 AI 洞察"""
    __tablename__ = "insight_history"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    # 选中的文本
    selected_text = Column(Text, nullable=False)  # 用户选中的原文
    selected_start = Column(Integer, nullable=True)  # 在文章中的起始位置（字符索引）
    selected_end = Column(Integer, nullable=True)  # 结束位置

    # 上下文（用于重新定位）
    context_before = Column(String(200), nullable=True)  # 前50字
    context_after = Column(String(200), nullable=True)  # 后50字

    # 问题和答案
    intent = Column(String(50), nullable=False)  # 'explain' | 'summarize' | 'question' | ...
    question = Column(Text, nullable=True)  # 如果是自定义问题
    insight = Column(Text, nullable=False)  # AI 的回答
    reasoning = Column(Text, nullable=True)  # 推理过程（如果有）

    # 元数据
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # 关系
    article = relationship("Article", back_populates="insight_history")
    user = relationship("User", backref="insight_history_items")


class MetaAnalysis(Base):
    """元信息分析表 - 用于元视角模式"""
    __tablename__ = "meta_analyses"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), unique=True, nullable=False, index=True)

    # 作者意图分析
    author_intent = Column(JSON, nullable=False)
    # {
    #   "primary": "inform|persuade|entertain|provoke",
    #   "confidence": 0.85,
    #   "description": "...",
    #   "indicators": ["...", "..."]
    # }

    # 时效性评估
    timeliness_score = Column(Float, nullable=False)
    timeliness_analysis = Column(JSON, nullable=False)
    # {
    #   "category": "evergreen",
    #   "decay_rate": "low",
    #   "best_before": null,
    #   "context_dependencies": []
    # }

    # 潜在偏见检测
    bias_analysis = Column(JSON, nullable=False)
    # {
    #   "detected": false,
    #   "types": [],
    #   "severity": "low",
    #   "examples": [],
    #   "overall_balance": "balanced"
    # }

    # 知识缺口提示
    knowledge_gaps = Column(JSON, nullable=False)
    # {
    #   "prerequisites": ["..."],
    #   "assumptions": ["..."],
    #   "missing_context": ["..."],
    #   "related_concepts": ["..."]
    # }

    # 原始 LLM 响应 (用于调试和改进)
    raw_llm_response = Column(Text, nullable=True)

    # 分析质量指标
    analysis_quality = Column(JSON, nullable=True)
    # {
    #   "confidence_score": 0.88,
    #   "processing_time_ms": 3500,
    #   "llm_model": "gpt-4o",
    #   "prompt_version": "v1.0"
    # }

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系
    article = relationship("Article", back_populates="meta_analysis")
    thinking_lens_results = relationship("ThinkingLensResult", back_populates="meta_analysis", cascade="all, delete-orphan")
    feedbacks = relationship("MetaViewFeedback", back_populates="meta_analysis", cascade="all, delete-orphan")


class ThinkingLensResult(Base):
    """思维透镜结果表"""
    __tablename__ = "thinking_lens_results"

    id = Column(Integer, primary_key=True, index=True)
    meta_analysis_id = Column(Integer, ForeignKey("meta_analyses.id"), nullable=False, index=True)
    lens_type = Column(String(50), nullable=False)  # 'argument_structure' | 'author_stance'

    # 高亮数据
    highlights = Column(JSON, nullable=False)
    # [
    #   {
    #     "start": 50,
    #     "end": 120,
    #     "text": "...",
    #     "category": "claim",
    #     "color": "#dbeafe",
    #     "tooltip": "..."
    #   }
    # ]

    # 注释和统计
    annotations = Column(JSON, nullable=True)
    # {
    #   "summary": "...",
    #   "key_insights": ["...", "..."],
    #   "statistics": {...}
    # }

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关系
    meta_analysis = relationship("MetaAnalysis", back_populates="thinking_lens_results")
    feedbacks = relationship("MetaViewFeedback", back_populates="lens_result", cascade="all, delete-orphan")


class MetaViewFeedback(Base):
    """用户反馈表 - 用于元视角功能改进"""
    __tablename__ = "meta_view_feedback"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    meta_analysis_id = Column(Integer, ForeignKey("meta_analyses.id"), nullable=True)
    lens_result_id = Column(Integer, ForeignKey("thinking_lens_results.id"), nullable=True)

    # 反馈类型
    feedback_type = Column(String(50), nullable=False)  # 'meta_info_card' | 'lens_highlight' | 'overall'

    # 反馈内容
    rating = Column(Integer, nullable=True)  # 1-5
    comment = Column(Text, nullable=True)
    feedback_data = Column(JSON, nullable=True)
    # {
    #   "helpful": true,
    #   "accurate": false,
    #   "specific_issue": "..."
    # }

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # 关系
    user = relationship("User")
    meta_analysis = relationship("MetaAnalysis", back_populates="feedbacks")
    lens_result = relationship("ThinkingLensResult", back_populates="feedbacks")


class UserAnalysisPreferences(Base):
    """用户分析偏好设置表 - 控制自动分析开关"""
    __tablename__ = "user_analysis_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)

    # 分析开关
    auto_basic_analysis = Column(Boolean, default=True, nullable=False)  # 基础分析
    auto_meta_analysis = Column(Boolean, default=False, nullable=False)  # 元视角分析
    auto_argument_lens = Column(Boolean, default=False, nullable=False)  # 论证透镜
    auto_stance_lens = Column(Boolean, default=False, nullable=False)  # 意图透镜

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系
    user = relationship("User", back_populates="analysis_preferences")
