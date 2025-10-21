"""
LLM调用重试装饰器
"""
import time
import logging
from functools import wraps
from typing import Callable, Any
from openai import APIError, APIConnectionError, RateLimitError, Timeout

logger = logging.getLogger(__name__)


def retry_llm_call(max_retries: int = 3, delay: float = 2.0, backoff: float = 2.0):
    """
    LLM调用重试装饰器

    Args:
        max_retries: 最大重试次数
        delay: 初始延迟时间（秒）
        backoff: 指数退避倍数

    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            current_delay = delay

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except (APIError, APIConnectionError, RateLimitError, Timeout) as e:
                    last_exception = e

                    if attempt < max_retries:
                        logger.warning(
                            f"LLM调用失败 (尝试 {attempt + 1}/{max_retries + 1}): {str(e)[:200]}"
                        )
                        logger.info(f"等待 {current_delay} 秒后重试...")
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"LLM调用失败，已达最大重试次数 ({max_retries + 1}): {str(e)[:200]}"
                        )

                except Exception as e:
                    # 非网络/API错误，不重试
                    logger.error(f"LLM调用出现不可重试的错误: {str(e)[:200]}")
                    raise

            # 所有重试都失败，抛出最后一个异常
            raise last_exception

        return wrapper
    return decorator
