#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
音频生成智能体
负责将剧本转换为音频脚本，生成背景音乐、音效和角色台词等
"""

import json
import os
from typing import List, Dict, Any
from src.utils.logger import Logger
from src.utils.error_handler import ErrorHandler
from src.utils.dashscope_client import DashScopeClient
from src.models.story_models import Script, AudioScript, Scene


class AudioAgent:
    """音频生成智能体类"""
    
    def __init__(self):
        """初始化音频生成智能体"""
        self.logger = Logger("AudioAgent")
        self.error_handler = ErrorHandler(self.logger)
        # 使用DashScope客户端替代Ollama
        self.dashscope_client = DashScopeClient()
        self.text_model_name = "qwen-plus"  # 文本生成模型
        self.audio_model_name = "qwen3-tts-flash-realtime"  # 语音合成模型
        # 确保输出目录存在
        self.output_dir = "./output/audio"
        os.makedirs(self.output_dir, exist_ok=True)
        self.logger.info("音频生成智能体初始化完成")
    
    def generate_audio_script(self, script: Script) -> AudioScript:
        """
        根据剧本生成音频脚本
        
        Args:
            script: 剧本对象
            
        Returns:
            AudioScript: 音频脚本对象
        """
        self.logger.info(f"开始为剧本 '{script.title}' 生成音频脚本")
        
        try:
            # 生成背景音乐描述
            background_music = self._generate_background_music(script)
            
            # 生成音效描述
            sound_effects = self._generate_sound_effects(script)
            
            # 生成角色台词
            voice_lines = self._generate_voice_lines(script)
            
            # 为剧本生成场景对话音频
            scene_audio_files = self.generate_speech_for_script(script)
            
            # 创建音频脚本对象
            audio_script = AudioScript(
                background_music=background_music,
                sound_effects=sound_effects,
                voice_lines=voice_lines
            )
            
            self.logger.info(f"剧本 '{script.title}' 的音频脚本生成完成")
            return audio_script
            
        except Exception as e:
            self.error_handler.handle_error(e, context="生成音频脚本过程中发生错误")
            raise
    
    def _generate_background_music(self, script: Script) -> List[str]:
        """
        为剧本生成背景音乐建议
        
        Args:
            script: 剧本对象
            
        Returns:
            List[str]: 背景音乐描述列表
        """
        self.logger.info("生成背景音乐建议")
        
        try:
            # 构建提示词
            prompt = f"""
            请为以下剧本生成适合的背景音乐建议：

            剧本标题：{script.title}
            剧本类型：{script.genre}
            情感基调：{script.emotional_tone}
            视觉风格：{script.visual_style}

            场景概要：
            """
            
            for scene in script.scenes:
                prompt += f"- 场景 {scene.scene_number}: {scene.location}, {scene.time}, 角色: {', '.join(scene.characters)}\n"
            
            prompt += """
            请提供8个适合该剧本的背景音乐建议，每个建议一行，格式为：
            音乐风格: 使用场景和情感表达
            
            例如：
            温柔钢琴曲: 用于表现角色内心独白或回忆场景
            轻快电子乐: 用于表现科技感或未来感场景
            """
            
            # 使用DashScope替代Ollama
            response = self.dashscope_client.chat_completion(
                model=self.text_model_name,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # 解析响应为列表
            background_music = [line.strip() for line in response['message']['content'].split('\n') if line.strip()]
            
            self.logger.info("背景音乐建议生成完成")
            return background_music[:8]  # 限制为8个建议
            
        except Exception as e:
            self.error_handler.handle_error(e, context="生成背景音乐建议时发生错误")
            # 返回默认背景音乐
            return [
                "温柔钢琴曲: 用于表现角色内心独白或回忆场景",
                "轻快电子乐: 用于表现科技感或未来感场景",
                "悬疑氛围音乐: 用于表现紧张或神秘场景",
                "温暖弦乐: 用于表现情感升华或温馨场景"
            ]
    
    def _generate_sound_effects(self, script: Script) -> List[str]:
        """
        为剧本生成音效建议
        
        Args:
            script: 剧本对象
            
        Returns:
            List[str]: 音效描述列表
        """
        self.logger.info("生成音效建议")
        
        try:
            # 构建提示词
            prompt = f"""
            请为以下剧本生成适合的音效建议：

            剧本标题：{script.title}
            剧本类型：{script.genre}
            情感基调：{script.emotional_tone}
            视觉风格：{script.visual_style}

            场景概要：
            """
            
            for scene in script.scenes:
                prompt += f"- 场景 {scene.scene_number}: {scene.location}, {scene.time}, 角色: {', '.join(scene.characters)}\n"
            
            prompt += """
            请提供10个适合该剧本的音效建议，每个建议一行，格式为：
            音效类型: 使用场景和目的
            
            例如：
            键盘敲击声: 表现角色在电脑前工作
            门开关声: 表现场景转换或角色进出
            """
            
            # 使用DashScope替代Ollama
            response = self.dashscope_client.chat_completion(
                model=self.text_model_name,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # 解析响应为列表
            sound_effects = [line.strip() for line in response['message']['content'].split('\n') if line.strip()]
            
            self.logger.info("音效建议生成完成")
            return sound_effects[:10]  # 限制为10个建议
            
        except Exception as e:
            self.error_handler.handle_error(e, context="生成音效建议时发生错误")
            # 返回默认音效
            return [
                "键盘敲击声: 表现角色在电脑前工作",
                "门开关声: 表现场景转换或角色进出",
                "脚步声: 表现角色移动",
                "心跳声: 表现紧张或激动情绪",
                "风声: 表现户外场景或孤独氛围"
            ]
    
    def _generate_voice_lines(self, script: Script) -> List[Dict[str, str]]:
        """
        为剧本生成旁白而不是角色台词
        
        Args:
            script: 剧本对象
            
        Returns:
            List[Dict[str, str]]: 旁白内容列表，格式为 {"narrator": 旁白内容}
        """
        self.logger.info("生成旁白内容")
        
        voice_lines = []
        
        for scene in script.scenes:
            # 使用场景中的旁白内容
            if hasattr(scene, 'narration') and scene.narration:
                voice_lines.append({"narrator": scene.narration})
            else:
                # 如果没有旁白，使用默认内容
                voice_lines.append({"narrator": f"场景 {scene.scene_number} 的旁白叙述"})
        
        self.logger.info("旁白内容生成完成")
        return voice_lines
    
    def generate_speech_from_text(self, text: str, character_name: str = "default") -> str:
        """
        使用DashScope将文本转换为语音
        
        Args:
            text: 要转换的文本
            character_name: 角色名称（用于选择合适的声音）
            
        Returns:
            str: 生成的音频文件路径
        """
        try:
            self.logger.info(f"为角色 '{character_name}' 生成语音: {text[:50]}...")
            
            # 根据角色选择合适的声音
            voice_mapping = {
                "default": "zhixiang",  # 默认声音
                "male": "zhiwei",       # 男性声音
                "female": "zhiyan"      # 女性声音
            }
            
            voice = voice_mapping.get(character_name.lower(), voice_mapping["default"])
            
            # 调用DashScope语音合成API
            response = self.dashscope_client.text_to_speech(
                model=self.audio_model_name,
                text=text,
                voice=voice
            )
            
            # 保存音频文件
            audio_file_path = f"{self.output_dir}/{character_name}_speech.wav"
            
            # 从响应中获取音频数据并保存
            if response and 'output' in response and 'audio' in response['output']:
                audio_data = response['output']['audio']
                # 如果audio_data是base64编码的字符串，需要解码
                if isinstance(audio_data, str):
                    import base64
                    audio_data = base64.b64decode(audio_data)
                
                with open(audio_file_path, "wb") as f:
                    f.write(audio_data)
            else:
                # 如果没有返回音频数据，创建一个默认的音频文件
                with open(audio_file_path, "w") as f:
                    f.write("Default audio placeholder")
            
            self.logger.info(f"语音生成完成: {audio_file_path}")
            return audio_file_path
            
        except Exception as e:
            self.error_handler.handle_error(e, context=f"为角色 '{character_name}' 生成语音时发生错误")
            # 返回默认音频文件路径
            default_audio_path = f"{self.output_dir}/{character_name}_default.wav"
            with open(default_audio_path, "w") as f:
                f.write("Default audio placeholder")
            return default_audio_path
    
    def generate_speech_for_script(self, script: Script) -> Dict[str, str]:
        """
        为剧本中的所有场景生成旁白音频
        
        Args:
            script: 剧本对象
            
        Returns:
            Dict[str, str]: 场景到音频文件路径的映射
        """
        self.logger.info(f"为剧本 '{script.title}' 中的所有场景生成旁白音频")
        
        scene_audio_files = {}
        
        # 为每个场景生成旁白音频
        for scene in script.scenes:
            # 使用场景中的旁白内容
            if hasattr(scene, 'narration') and scene.narration:
                scene_narration_text = scene.narration
            else:
                # 如果没有旁白，使用默认内容
                scene_narration_text = f"场景 {scene.scene_number} 的旁白叙述"
            
            # 为场景生成音频
            if scene_narration_text.strip():
                audio_file_path = self.generate_speech_from_scene(scene_narration_text, scene.scene_number)
                scene_audio_files[f"scene_{scene.scene_number}"] = audio_file_path
        
        self.logger.info("剧本场景旁白音频生成完成")
        return scene_audio_files
    
    def generate_speech_from_scene(self, text: str, scene_number: int) -> str:
        """
        为场景对话生成音频
        
        Args:
            text: 场景对话文本
            scene_number: 场景编号
            
        Returns:
            str: 生成的音频文件路径
        """
        try:
            self.logger.info(f"为场景 {scene_number} 生成对话音频: {text[:50]}...")
            
            # 使用默认声音生成场景对话音频
            voice = "zhixiang"  # 默认声音
            
            # 调用DashScope语音合成API
            response = self.dashscope_client.text_to_speech(
                model=self.audio_model_name,
                text=text,
                voice=voice
            )
            
            # 保存音频文件
            audio_file_path = f"{self.output_dir}/scene_{scene_number}_dialog.wav"
            
            # 从响应中获取音频数据并保存
            if response and 'output' in response and 'audio' in response['output']:
                audio_data = response['output']['audio']
                # 如果audio_data是base64编码的字符串，需要解码
                if isinstance(audio_data, str):
                    import base64
                    audio_data = base64.b64decode(audio_data)
                
                with open(audio_file_path, "wb") as f:
                    f.write(audio_data)
            else:
                # 如果没有返回音频数据，创建一个默认的音频文件
                with open(audio_file_path, "w") as f:
                    f.write("Default scene dialog audio placeholder")
            
            self.logger.info(f"场景 {scene_number} 对话音频生成完成: {audio_file_path}")
            return audio_file_path
            
        except Exception as e:
            self.error_handler.handle_error(e, context=f"为场景 {scene_number} 生成对话音频时发生错误")
            # 返回默认音频文件路径
            default_audio_path = f"{self.output_dir}/scene_{scene_number}_default.wav"
            with open(default_audio_path, "w") as f:
                f.write("Default scene dialog audio placeholder")
            return default_audio_path
