#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
错误处理工具类
"""

from typing import Optional
from enum import Enum


class ErrorLevel(Enum):
    """错误级别枚举"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorHandler:
    """错误处理器"""
    
    def __init__(self, logger=None):
        """初始化错误处理器"""
        self.logger = logger
    
    def handle_error(self, 
                    error: Exception, 
                    level: ErrorLevel = ErrorLevel.ERROR,
                    context: Optional[str] = None):
        """处理错误"""
        error_msg = f"错误类型: {type(error).__name__}, 错误信息: {str(error)}"
        if context:
            error_msg = f"{context} - {error_msg}"
        
        if self.logger:
            if level == ErrorLevel.INFO:
                self.logger.info(error_msg)
            elif level == ErrorLevel.WARNING:
                self.logger.warning(error_msg)
            elif level == ErrorLevel.ERROR:
                self.logger.error(error_msg)
            elif level == ErrorLevel.CRITICAL:
                self.logger.critical(error_msg)
        else:
            print(f"[{level.value.upper()}] {error_msg}")
        
        # 根据错误级别决定是否重新抛出异常
        if level in [ErrorLevel.ERROR, ErrorLevel.CRITICAL]:
            raise error
    
    def create_error_report(self, errors: list) -> str:
        """创建错误报告"""
        if not errors:
            return "没有错误报告"
        
        report = "错误报告:\n"
        report += "=" * 50 + "\n"
        
        for i, error in enumerate(errors, 1):
            report += f"{i}. {error}\n"
        
        report += "=" * 50 + "\n"
        return report