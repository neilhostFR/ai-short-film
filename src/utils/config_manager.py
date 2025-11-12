#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置管理工具类
"""

import os
import yaml
from typing import Any, Dict


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: str = "config/app_config.yaml"):
        """初始化配置管理器"""
        self.config_path = config_path
        self.config_data = {}
        self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as file:
                self.config_data = yaml.safe_load(file) or {}
        else:
            # 创建默认配置
            self.config_data = self._get_default_config()
            self.save_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "app": {
                "name": "AI Short Film Generator",
                "version": "1.0.0",
                "debug": False
            },
            "models": {
                "language_model": "dashscope",
                "llm_model_name": "qwen-plus",
                "visual_model": "wan2.2-t2i-plus",
                "audio_model": "Qwen3-TTS",
                "video_model": "wanx2.1-vace-plus"
            },
            "paths": {
                "output_dir": "./output",
                "temp_dir": "./temp",
                "logs_dir": "./logs"
            },
            "api": {
                "host": "localhost",
                "port": 8000
            }
        }
    
    def save_config(self):
        """保存配置文件"""
        # 确保配置目录存在
        config_dir = os.path.dirname(self.config_path)
        if config_dir and not os.path.exists(config_dir):
            os.makedirs(config_dir)
            
        with open(self.config_path, 'w', encoding='utf-8') as file:
            yaml.dump(self.config_data, file, default_flow_style=False, allow_unicode=True)
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """获取配置项"""
        keys = key_path.split('.')
        value = self.config_data
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any):
        """设置配置项"""
        keys = key_path.split('.')
        config_ref = self.config_data
        
        # 导航到倒数第二层
        for key in keys[:-1]:
            if key not in config_ref:
                config_ref[key] = {}
            config_ref = config_ref[key]
        
        # 设置最后一层的值
        config_ref[keys[-1]] = value