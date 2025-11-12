#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DashScope API客户端工具类
"""

import os
import json
from typing import Dict, Any, List, Optional
from src.utils.logger import Logger
from src.utils.error_handler import ErrorHandler

class DashScopeClient:
    """DashScope API客户端"""
    
    def __init__(self):
        """初始化DashScope客户端"""
        self.logger = Logger("DashScopeClient")
        self.error_handler = ErrorHandler(self.logger)
        
        # 延迟导入dashscope模块
        try:
            import dashscope
            self.dashscope = dashscope
        except ImportError as e:
            raise ImportError("DashScope库未安装，请先安装dashscope包") from e
        
        # 从环境变量获取API密钥
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key:
            raise ValueError("DASHSCOPE_API_KEY环境变量未设置")
        
        # 设置API密钥
        self.dashscope.api_key = self.api_key
        
        self.logger.info("DashScope客户端初始化完成")
    
    def chat_completion(self, model: str, messages: List[Dict[str, str]], 
                       format: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        调用DashScope聊天完成API
        
        Args:
            model: 模型名称
            messages: 消息列表
            format: 返回格式(json等)
            **kwargs: 其他参数
            
        Returns:
            Dict: API响应结果
        """
        try:
            self.logger.info(f"调用DashScope聊天完成API，模型: {model}")
            
            # 构建请求参数
            params = {
                "model": model,
                "messages": messages,
                **kwargs
            }
            
            if format:
                params["result_format"] = format
            
            # 调用API
            response = self.dashscope.Generation.call(**params)
            
            # 检查响应状态
            # 使用更安全的方式处理响应
            self.logger.info("DashScope聊天完成API调用完成")
            
            # 尝试从响应中提取内容
            content = None
            try:
                # 尝试直接访问output属性
                output = getattr(response, 'output', None)
                if output:
                    # 尝试访问choices
                    choices = getattr(output, 'choices', None)
                    if choices and len(choices) > 0:
                        first_choice = choices[0]
                        message = getattr(first_choice, 'message', None)
                        if message:
                            content = getattr(message, 'content', None)
                    
                    # 如果没有从choices中提取到内容，尝试其他方式
                    if not content:
                        content = getattr(output, 'text', None)
                
                # 如果仍然没有内容，尝试将整个响应转换为字符串
                if not content:
                    content = str(response)
            except Exception:
                # 最后尝试将整个响应转换为字符串
                content = str(response)
            
            # 如果内容为空，抛出异常
            if not content:
                raise ValueError("API响应内容为空")
            
            return {
                "message": {
                    "content": content
                }
            }
                
        except Exception as e:
            self.error_handler.handle_error(e, context="调用DashScope聊天完成API时发生错误")
            raise
    
    def text_to_speech(self, model: str, text: str, voice: Optional[str] = None,
                      **kwargs) -> Dict[str, Any]:
        """
        调用DashScope语音合成API
        
        Args:
            model: 模型名称
            text: 要合成的文本
            voice: 声音类型
            **kwargs: 其他参数
            
        Returns:
            Dict: API响应结果
        """
        try:
            self.logger.info(f"调用DashScope语音合成API，模型: {model}")
            
            # 构建请求参数
            params = {
                "model": model,
                "input": text,  # 注意：DashScope语音合成使用input参数而不是text
                **kwargs
            }
            
            if voice:
                params["voice"] = voice
            
            # 调用API
            response = self.dashscope.SpeechSynthesizer.call(**params)
            
            # 检查响应状态
            self.logger.info("DashScope语音合成API调用完成")
            
            # 尝试从响应中提取内容
            try:
                # 尝试直接访问output属性
                output = getattr(response, 'output', None)
                if output:
                    return {"output": output}
                else:
                    return {"result": str(response)}
            except Exception:
                return {"result": str(response)}
                
        except Exception as e:
            self.error_handler.handle_error(e, context="调用DashScope语音合成API时发生错误")
            raise
    
    def text_to_image(self, model: str, prompt: str, negative_prompt: Optional[str] = None,
                     **kwargs) -> Dict[str, Any]:
        """
        调用DashScope文生图API
        
        Args:
            model: 模型名称
            prompt: 正向提示词
            negative_prompt: 负向提示词
            **kwargs: 其他参数
            
        Returns:
            Dict: API响应结果
        """
        try:
            self.logger.info(f"调用DashScope文生图API，模型: {model}")
            
            # 构建请求参数
            params = {
                "model": model,
                "prompt": prompt,
                **kwargs
            }
            
            if negative_prompt:
                params["negative_prompt"] = negative_prompt
            
            # 调用API
            response = self.dashscope.ImageSynthesis.call(**params)
            
            # 检查响应状态
            self.logger.info("DashScope文生图API调用完成")
            
            # 尝试从响应中提取内容
            try:
                # 尝试直接访问output属性
                output = getattr(response, 'output', None)
                if output:
                    return {"output": output}
                else:
                    return {"result": str(response)}
            except Exception:
                return {"result": str(response)}
                
        except Exception as e:
            self.error_handler.handle_error(e, context="调用DashScope文生图API时发生错误")
            raise
    
    def video_generation(self, model: str, prompt: str, image_paths: Optional[List[str]] = None, 
                       audio_path: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        调用DashScope视频生成API
        
        Args:
            model: 模型名称
            prompt: 视频生成提示词
            image_paths: 图像文件路径列表
            audio_path: 音频文件路径
            **kwargs: 其他参数
            
        Returns:
            Dict: API响应结果
        """
        try:
            self.logger.info(f"调用DashScope视频生成API，模型: {model}")
            
            # 构建请求参数
            params = {
                "model": model,
                "prompt": prompt,
                **kwargs
            }
            
            # 添加图像参数
            if image_paths:
                params["image_paths"] = image_paths
            
            # 添加音频参数
            if audio_path:
                params["audio_path"] = audio_path
            
            # 调用API
            response = self.dashscope.VideoSynthesis.call(**params)
            
            # 检查响应状态
            self.logger.info("DashScope视频生成API调用完成")
            
            # 尝试从响应中提取内容
            try:
                # 尝试直接访问output属性
                output = getattr(response, 'output', None)
                if output:
                    return {"output": output}
                else:
                    return {"result": str(response)}
            except Exception:
                return {"result": str(response)}
                
        except Exception as e:
            self.error_handler.handle_error(e, context="调用DashScope视频生成API时发生错误")
            raise