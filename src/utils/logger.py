#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
日志工具类
"""

import logging
import os
from datetime import datetime


class Logger:
    """日志管理器"""
    
    def __init__(self, name: str = "AIShortFilm", log_dir: str = "./logs"):
        """初始化日志管理器"""
        self.name = name
        self.log_dir = log_dir
        
        # 确保日志目录存在
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 创建logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # 避免重复添加处理器
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """设置日志处理器"""
        # 创建文件处理器
        log_file = os.path.join(
            self.log_dir, 
            f"{self.name}_{datetime.now().strftime('%Y%m%d')}.log"
        )
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 创建格式器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 添加处理器到logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def debug(self, message: str):
        """记录debug级别日志"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """记录info级别日志"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """记录warning级别日志"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """记录error级别日志"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """记录critical级别日志"""
        self.logger.critical(message)