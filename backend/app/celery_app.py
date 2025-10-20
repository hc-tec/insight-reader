# -*- coding: utf-8 -*-
"""
Celery 异步任务队列配置
使用数据库作为 broker 和 backend（不需要 Redis）
"""

from celery import Celery
from app.config import settings

# 使用 SQLAlchemy 作为 broker 和 backend
# 格式: db+scheme://user:password@host:port/dbname
database_url = settings.database_url.replace('sqlite:///', 'db+sqlite:///')

# 创建 Celery 应用
celery_app = Celery(
    'insightreader',
    broker=database_url,  # 使用数据库作为消息队列
    backend=database_url  # 使用数据库作为结果存储
)

# Celery 配置
celery_app.conf.update(
    # 序列化
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',

    # 时区
    timezone='UTC',
    enable_utc=True,

    # 任务配置
    task_track_started=True,  # 跟踪任务启动
    task_time_limit=90,  # 任务超时时间（90秒）
    task_soft_time_limit=60,  # 软超时（60秒后发送警告）

    # 结果配置
    result_expires=3600,  # 结果保留1小时

    # 数据库 broker 配置
    broker_connection_retry_on_startup=True,

    # 任务路由（自动发现任务）
    imports=(
        'app.tasks.analysis_tasks',
    ),
)

# 任务优先级配置
celery_app.conf.task_default_priority = 5
celery_app.conf.task_queue_max_priority = 10

print("✅ Celery 配置加载完成（使用数据库作为 broker）")
