# -*- coding: utf-8 -*-
"""
错误日志记录工具

记录系统错误到文件，便于调试和追踪问题
"""

import os
import json
import traceback
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any


class ErrorLogger:
    """错误日志记录器"""

    def __init__(self, log_dir: str = "logs/errors"):
        """
        初始化错误日志记录器

        Args:
            log_dir: 日志文件保存目录
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def log_error(
        self,
        error_type: str,
        error_message: str,
        context: Optional[Dict[str, Any]] = None,
        exception: Optional[Exception] = None
    ):
        """
        记录错误到文件

        Args:
            error_type: 错误类型（如 "LLM_API_ERROR", "DATABASE_ERROR" 等）
            error_message: 错误描述
            context: 错误上下文信息（如请求参数、用户ID等）
            exception: 异常对象（可选）
        """
        timestamp = datetime.now()
        date_str = timestamp.strftime("%Y-%m-%d")
        time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")

        # 构建错误记录
        error_record = {
            "timestamp": time_str,
            "error_type": error_type,
            "error_message": error_message,
            "context": context or {},
        }

        # 如果有异常对象，添加详细信息
        if exception:
            error_record["exception_type"] = type(exception).__name__
            error_record["exception_str"] = str(exception)
            error_record["traceback"] = traceback.format_exc()

        # 按日期分文件记录
        log_file = self.log_dir / f"errors_{date_str}.jsonl"

        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(error_record, ensure_ascii=False) + "\n")
        except Exception as e:
            # 如果写入失败，至少打印到控制台
            print(f"❌ 无法写入错误日志: {e}")
            print(f"原始错误: {error_record}")

    def log_llm_error(
        self,
        service_name: str,
        model_name: str,
        error: Exception,
        request_data: Optional[Dict[str, Any]] = None
    ):
        """
        记录 LLM 调用错误（专用方法）

        Args:
            service_name: 服务名称（如 "unified_analysis", "meta_analysis"）
            model_name: 模型名称
            error: 异常对象
            request_data: 请求数据（如 messages, temperature 等）
        """
        context = {
            "service": service_name,
            "model": model_name,
            "request_data": request_data or {}
        }

        self.log_error(
            error_type="LLM_API_ERROR",
            error_message=f"LLM调用失败 - {service_name}",
            context=context,
            exception=error
        )

    def log_database_error(
        self,
        operation: str,
        error: Exception,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        记录数据库错误（专用方法）

        Args:
            operation: 操作类型（如 "insert", "query", "update"）
            error: 异常对象
            details: 详细信息
        """
        context = {
            "operation": operation,
            "details": details or {}
        }

        self.log_error(
            error_type="DATABASE_ERROR",
            error_message=f"数据库操作失败 - {operation}",
            context=context,
            exception=error
        )

    def log_validation_error(
        self,
        validation_type: str,
        error_message: str,
        data: Optional[Dict[str, Any]] = None
    ):
        """
        记录数据验证错误（专用方法）

        Args:
            validation_type: 验证类型
            error_message: 错误消息
            data: 相关数据
        """
        context = {
            "validation_type": validation_type,
            "data": data or {}
        }

        self.log_error(
            error_type="VALIDATION_ERROR",
            error_message=error_message,
            context=context
        )

    def get_error_summary(self, date: Optional[str] = None) -> Dict[str, int]:
        """
        获取错误统计摘要

        Args:
            date: 日期字符串（YYYY-MM-DD），默认为今天

        Returns:
            错误类型统计字典
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        log_file = self.log_dir / f"errors_{date}.jsonl"

        if not log_file.exists():
            return {}

        error_counts = {}

        try:
            with open(log_file, "r", encoding="utf-8") as f:
                for line in f:
                    record = json.loads(line)
                    error_type = record.get("error_type", "UNKNOWN")
                    error_counts[error_type] = error_counts.get(error_type, 0) + 1
        except Exception as e:
            print(f"❌ 读取错误日志失败: {e}")

        return error_counts


# 全局单例
_error_logger = None


def get_error_logger() -> ErrorLogger:
    """获取全局错误日志记录器"""
    global _error_logger
    if _error_logger is None:
        _error_logger = ErrorLogger()
    return _error_logger


# 便捷函数
def log_llm_error(
    service_name: str,
    model_name: str,
    error: Exception,
    request_data: Optional[Dict[str, Any]] = None
):
    """记录 LLM 调用错误（便捷函数）"""
    get_error_logger().log_llm_error(service_name, model_name, error, request_data)


def log_database_error(
    operation: str,
    error: Exception,
    details: Optional[Dict[str, Any]] = None
):
    """记录数据库错误（便捷函数）"""
    get_error_logger().log_database_error(operation, error, details)


def log_error(
    error_type: str,
    error_message: str,
    context: Optional[Dict[str, Any]] = None,
    exception: Optional[Exception] = None
):
    """记录通用错误（便捷函数）"""
    get_error_logger().log_error(error_type, error_message, context, exception)
