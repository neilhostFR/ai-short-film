#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
角色扮演智能体
负责角色深度塑造和个性化表达
"""

import json
import requests
import time
import os
import re
from typing import List, Dict, Any, Optional
from src.utils.logger import Logger
from src.utils.error_handler import ErrorHandler
from src.utils.dashscope_client import DashScopeClient
from src.models.story_models import CharacterProfile, Script


class CharacterAgent:
    """角色扮演智能体类"""
    
    def __init__(self):
        """初始化角色扮演智能体"""
        self.logger = Logger("CharacterAgent")
        self.error_handler = ErrorHandler(self.logger)
        # 使用DashScope客户端替代Ollama
        self.dashscope_client = DashScopeClient()
        self.text_model_name = "qwen-plus"  # 文本生成模型
        self.image_model_name = "wan2.2-t2i-plus"  # 文生图模型
        # 确保输出目录存在
        self.output_dir = "./output/characters"
        os.makedirs(self.output_dir, exist_ok=True)
        self.logger.info("角色扮演智能体初始化完成")
    
    def enhance_characters_from_script(self, script: Script) -> List[CharacterProfile]:
        """
        基于剧本增强角色档案
        
        Args:
            script: 剧本对象
            
        Returns:
            List[CharacterProfile]: 增强后的角色档案列表
        """
        self.logger.info(f"开始增强剧本 '{script.title}' 中的角色档案")
        
        # 如果剧本中没有角色，直接返回空列表
        if not script.characters:
            self.logger.info("剧本中没有角色，跳过角色增强阶段")
            return []
        
        enhanced_characters = []
        
        try:
            # 首先收集所有角色信息，以便在生成视觉描述时保持一致性
            all_characters_info = []
            for character in script.characters:
                all_characters_info.append({
                    "name": character.name,
                    "age": character.age,
                    "personality_traits": character.personality_traits,
                    "background_story": character.background_story
                })
            
            for character in script.characters:
                # 1. 增强角色档案
                enhanced_character = self._enhance_character_profile(character, script)
                
                # 2. 生成角色视觉形象（传递所有角色信息以确保风格一致性）
                visual_description = self._generate_character_visual_description(enhanced_character, script, all_characters_info)
                
                # 3. 调用DashScope文生图模型生成角色图像
                image_path = self._generate_character_image(visual_description, character.name)
                
                # 4. 更新角色档案
                enhanced_character.visual_description = visual_description
                enhanced_character.image_path = image_path
                
                enhanced_characters.append(enhanced_character)
            
            self.logger.info(f"角色档案增强完成，共处理{len(enhanced_characters)}个角色")
            return enhanced_characters
            
        except Exception as e:
            self.error_handler.handle_error(e, context="增强角色档案过程中发生错误")
            raise
    
    def _enhance_character_profile(self, character: CharacterProfile, script: Script) -> CharacterProfile:
        """
        增强角色档案
        
        Args:
            character: 角色档案
            script: 剧本对象
            
        Returns:
            CharacterProfile: 增强后的角色档案
        """
        self.logger.info(f"增强角色 '{character.name}' 的档案")
        
        # 构建提示词
        prompt = f"""
        请基于以下剧本信息，为角色创建更详细的档案：

        剧本标题：{script.title}
        剧本类型：{script.genre}
        情感基调：{script.emotional_tone}

        当前角色信息：
        姓名：{character.name}
        年龄：{character.age}
        性格特征：{', '.join(character.personality_traits)}
        背景故事：{character.background_story}

        请严格按照以下JSON格式返回结果：
        {{
            "name": "{character.name}",
            "age": {character.age},
            "personality_traits": ["特征1", "特征2", "特征3", "特征4", "特征5"],
            "background_story": "更详细的背景故事",
            "motivations": ["动机1", "动机2"],
            "fears": ["恐惧1", "恐惧2"],
            "relationships": [
                {{
                    "character": "相关角色名",
                    "relationship": "关系描述"
                }}
            ],
            "character_arc": "角色在故事中的成长弧线",
            "voice_characteristics": {{
                "tone": "{character.voice_characteristics.get('tone', '待定')}",
                "pace": "{character.voice_characteristics.get('pace', '待定')}",
                "accent": "{character.voice_characteristics.get('accent', '待定')}",
                "speech_patterns": "说话习惯描述"
            }}
        }}
        """.strip()
        
        try:
            # 使用DashScope替代Ollama
            response = self.dashscope_client.chat_completion(
                model=self.text_model_name,
                messages=[{"role": "user", "content": prompt}],
                format="json"
            )
            
            # 检查响应是否有效
            if not response or 'message' not in response or 'content' not in response['message']:
                raise ValueError("API响应格式不正确")
            
            content = response['message']['content']
            if not content:
                raise ValueError("API响应内容为空")
            
            # 如果内容是字符串，尝试解析JSON
            if isinstance(content, str):
                # 清理内容，确保是有效的JSON格式
                content = content.strip()
                if content.startswith("```json"):
                    content = content[7:]  # 移除 ```json 前缀
                if content.endswith("```"):
                    content = content[:-3]  # 移除 ``` 后缀
                content = content.strip()
                
                try:
                    enhanced_data = json.loads(content)
                except json.JSONDecodeError as e:
                    self.logger.error(f"JSON解析失败，原始内容: {content}")
                    raise e
            else:
                # 如果已经是字典格式，直接使用
                enhanced_data = content
            
            # 创建增强后的角色档案
            enhanced_character = CharacterProfile(
                name=enhanced_data["name"],
                age=enhanced_data["age"],
                personality_traits=enhanced_data["personality_traits"],
                background_story=enhanced_data["background_story"],
                voice_characteristics=enhanced_data["voice_characteristics"],
                motivations=enhanced_data.get("motivations", []),
                fears=enhanced_data.get("fears", []),
                relationships=enhanced_data.get("relationships", []),
                character_arc=enhanced_data.get("character_arc", "")
            )
            
            self.logger.info(f"角色 '{character.name}' 档案增强完成")
            return enhanced_character
            
        except Exception as e:
            self.error_handler.handle_error(e, context=f"增强角色 '{character.name}' 档案时发生错误")
            # 返回原始角色档案
            return character
    
    def _generate_character_visual_description(self, character: CharacterProfile, script: Script, all_characters_info: List[Dict]) -> str:
        """
        生成角色视觉形象描述
        
        Args:
            character: 角色档案
            script: 剧本对象
            all_characters_info: 所有角色信息列表（用于保持风格一致性）
            
        Returns:
            str: 角色视觉形象描述
        """
        self.logger.info(f"生成角色 '{character.name}' 的视觉形象描述")
        
        # 构建所有角色信息的字符串
        all_characters_str = "\n".join([
            f"  - {char['name']}: {char['age']}岁, 性格特征: {', '.join(char['personality_traits'][:3])}"
            for char in all_characters_info
        ])
        
        # 构建提示词
        prompt = f"""
        请为以下角色生成详细的视觉描述，用于图像生成：
        
        剧本标题: {script.title}
        剧本类型: {script.genre}
        视觉风格: {script.visual_style}
        情感基调: {script.emotional_tone}
        
        剧本中的所有角色:
{all_characters_str}
        
        角色信息:
        姓名: {character.name}
        年龄: {character.age}
        性格特征: {', '.join(character.personality_traits)}
        背景故事: {character.background_story}
        
        请提供详细的视觉描述，包括：
        1. 外貌特征（面部、发型、体型等）
        2. 服装样式（全身服装）
        3. 表情和姿态
        4. 与剧本视觉风格匹配的细节
        
        重要要求：
        - 确保剧本中所有角色的视觉一致性
        - 所有角色应具有相同艺术风格（如写实、风格化、电影感等）
        - 匹配剧本指定的视觉风格: {script.visual_style}
        - 视觉风格应与专业动画或电影角色设计一致
        - 生成角色的全身肖像
        - 图像只能包含角色，不能有背景或其他物体
        - 角色应居中，背景为中性且易于移除的颜色
        
        描述应详细具体，适合用于图像生成模型。请用英文回复。
        """.strip()
        
        try:
            # 使用DashScope替代Ollama
            response = self.dashscope_client.chat_completion(
                model=self.text_model_name,
                messages=[{"role": "user", "content": prompt}]
            )
            
            visual_description = response['message']['content']
            # 清理描述中的特殊字符
            visual_description = re.sub(r'[^\x00-\x7F]+', '', visual_description)  # 移除非ASCII字符
            visual_description = re.sub(r'\n+', ' ', visual_description)  # 替换换行符为空格
            visual_description = re.sub(r'\s+', ' ', visual_description).strip()  # 规范化空格
            
            self.logger.info(f"角色 '{character.name}' 视觉形象描述生成完成")
            return visual_description
            
        except Exception as e:
            self.error_handler.handle_error(e, context=f"生成角色 '{character.name}' 视觉形象描述时发生错误")
            return f"character {character.name}, detailed visual description"
    
    def _generate_character_image(self, visual_description: str, character_name: str) -> str:
        """
        调用DashScope文生图模型生成角色图像
        
        Args:
            visual_description: 视觉描述
            character_name: 角色名称
            
        Returns:
            str: 生成图像的路径
        """
        self.logger.info(f"调用DashScope文生图模型生成角色 '{character_name}' 的图像")
        
        try:
            # 构建专门用于生成全身照的提示词
            image_prompt = f"{visual_description}, full body portrait, character centered, plain background, no background objects, white or transparent background, professional character design"
            
            # 调用DashScope文生图API
            response = self.dashscope_client.text_to_image(
                model=self.image_model_name,
                prompt=image_prompt
            )
            
            # 检查响应是否成功
            if response and 'results' in response and response['results']:
                image_url = response['results'][0]['url']
                
                # 下载图像到本地
                image_response = requests.get(image_url)
                if image_response.status_code == 200:
                    image_path = f"{self.output_dir}/{character_name}.png"
                    with open(image_path, 'wb') as f:
                        f.write(image_response.content)
                    self.logger.info(f"角色 '{character_name}' 图像生成完成: {image_path}")
                    return image_path
                else:
                    raise Exception(f"下载图像失败: {image_response.status_code}")
            else:
                raise Exception("图像生成失败，未返回有效结果")
                
        except Exception as e:
            self.error_handler.handle_error(e, context=f"生成角色 '{character_name}' 图像时发生错误")
            default_path = f"{self.output_dir}/{character_name}_default.png"
            # 创建一个默认的空文件
            with open(default_path, 'w') as f:
                f.write("Default character image placeholder")
            return default_path