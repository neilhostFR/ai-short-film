#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
编剧智能体
负责剧本创作和情节设计
"""

import json
import re
from typing import List, Dict, Any
from src.utils.logger import Logger
from src.utils.error_handler import ErrorHandler
from src.utils.dashscope_client import DashScopeClient
from src.models.story_models import (
    UserInput, StoryConcept, Script, Scene, CharacterProfile
)


class ScreenwriterAgent:
    """编剧智能体类"""
    
    def __init__(self):
        """初始化编剧智能体"""
        self.logger = Logger("ScreenwriterAgent")
        self.error_handler = ErrorHandler(self.logger)
        # 使用DashScope客户端替代Ollama
        self.dashscope_client = DashScopeClient()
        self.model_name = "qwen-plus"  # 使用DashScope的qwen-plus模型
        self.logger.info("编剧智能体初始化完成")
    
    def create_script_from_concept(self, concept: StoryConcept, user_input: UserInput) -> Script:
        """
        基于故事概念创建剧本
        
        Args:
            concept: 故事概念
            user_input: 用户输入
            
        Returns:
            Script: 完整剧本
        """
        self.logger.info(f"开始为概念 '{concept.title}' 创建剧本")
        
        try:
            # 1. 设计剧本结构
            script_structure = self._design_script_structure(concept, user_input)
            
            # 2. 创建分场大纲
            scenes = self._create_scene_outline(concept, user_input, script_structure)
            
            # 3. 生成角色档案
            characters = self._generate_character_profiles(concept, user_input)
            
            # 4. 撰写对话脚本
            scenes_with_dialogue = self._write_dialogues(scenes, characters, concept, user_input)
            
            # 创建完整剧本
            script = Script(
                title=concept.title,
                genre=user_input.genre,
                total_duration=user_input.duration,
                scenes=scenes_with_dialogue,
                characters=characters
            )
            
            self.logger.info(f"剧本 '{concept.title}' 创建完成")
            return script
            
        except Exception as e:
            self.error_handler.handle_error(e, context="创建剧本过程中发生错误")
            raise
    
    def _design_script_structure(self, concept: StoryConcept, user_input: UserInput) -> Dict[str, Any]:
        """
        设计剧本结构
        
        Args:
            concept: 故事概念
            user_input: 用户输入
            
        Returns:
            Dict: 剧本结构信息
        """
        self.logger.info("设计剧本结构...")
        
        # 构建提示词
        prompt = f"""
        请为以下短剧概念设计一个专业的剧本结构：

        故事概念：{concept.title}
        核心冲突：{concept.core_conflict}
        主要角色：{', '.join(concept.main_characters)}
        情感基调：{concept.emotional_tone}
        目标时长：{user_input.duration}秒
        短剧类型：{user_input.genre}

        请严格按照以下JSON格式返回结果：
        {{
            "structure_type": "三幕式/五幕式",
            "acts": [
                {{
                    "act_number": 1,
                    "name": "第一幕名称",
                    "duration": 30,
                    "purpose": "介绍角色和背景，建立冲突"
                }}
            ],
            "total_scenes": 8,
            " pacing_strategy": "快节奏/中等节奏/慢节奏"
        }}
        """.strip()
        
        try:
            # 使用DashScope替代Ollama
            response = self.dashscope_client.chat_completion(
                model=self.model_name,
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
                    structure = json.loads(content)
                except json.JSONDecodeError as e:
                    self.logger.error(f"JSON解析失败，原始内容: {content}")
                    raise e
            else:
                # 如果已经是字典格式，直接使用
                structure = content
                
            self.logger.info("剧本结构设计完成")
            return structure
            
        except Exception as e:
            self.error_handler.handle_error(e, context="设计剧本结构时发生错误")
            # 返回默认结构
            return {
                "structure_type": "三幕式",
                "acts": [
                    {"act_number": 1, "name": "开端", "duration": user_input.duration // 3, "purpose": "介绍角色和背景"},
                    {"act_number": 2, "name": "发展", "duration": user_input.duration // 3, "purpose": "冲突升级"},
                    {"act_number": 3, "name": "结局", "duration": user_input.duration // 3, "purpose": "解决冲突"}
                ],
                "total_scenes": 6,
                "pacing_strategy": "中等节奏"
            }
    
    def _create_scene_outline(self, concept: StoryConcept, user_input: UserInput, 
                             script_structure: Dict[str, Any]) -> List[Scene]:
        """
        创建分场大纲
        
        Args:
            concept: 故事概念
            user_input: 用户输入
            script_structure: 剧本结构
            
        Returns:
            List[Scene]: 场景列表
        """
        self.logger.info("创建分场大纲...")
        
        # 构建提示词
        prompt = f"""
        请为以下短剧概念创建详细的分场大纲：

        故事概念：{concept.title}
        核心冲突：{concept.core_conflict}
        主要角色：{', '.join(concept.main_characters)}
        情感基调：{concept.emotional_tone}
        目标时长：{user_input.duration}秒
        短剧类型：{user_input.genre}
        剧本结构：{script_structure['structure_type']}

        请严格按照以下JSON格式返回结果：
        {{
            "scenes": [
                {{
                    "scene_number": 1,
                    "location": "地点描述",
                    "time": "时间描述",
                    "characters": ["角色1", "角色2"],
                    "summary": "场景摘要",
                    "purpose": "场景目的",
                    "duration": 15
                }}
            ]
        }}
        
        总共需要创建约{script_structure['total_scenes']}个场景，总时长应接近{user_input.duration}秒。
        """.strip()
        
        try:
            # 使用DashScope替代Ollama
            response = self.dashscope_client.chat_completion(
                model=self.model_name,
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
                    scenes_data = json.loads(content)
                except json.JSONDecodeError as e:
                    self.logger.error(f"JSON解析失败，原始内容: {content}")
                    raise e
            else:
                # 如果已经是字典格式，直接使用
                scenes_data = content
            
            scenes = []
            
            for scene_data in scenes_data.get("scenes", []):
                scene = Scene(
                    scene_number=scene_data["scene_number"],
                    location=scene_data["location"],
                    time=scene_data["time"],
                    characters=scene_data["characters"],
                    dialogue=[],  # 对话将在后续步骤中添加
                    actions=[scene_data["summary"]],
                    duration=scene_data["duration"]
                )
                scenes.append(scene)
            
            self.logger.info(f"分场大纲创建完成，共{len(scenes)}个场景")
            return scenes
            
        except Exception as e:
            self.error_handler.handle_error(e, context="创建分场大纲时发生错误")
            # 返回默认场景
            return [
                Scene(
                    scene_number=1,
                    location="默认地点",
                    time="白天",
                    characters=concept.main_characters[:2],
                    dialogue=[],
                    actions=["开场场景"],
                    duration=user_input.duration // 2
                ),
                Scene(
                    scene_number=2,
                    location="另一个地点",
                    time="夜晚",
                    characters=concept.main_characters,
                    dialogue=[],
                    actions=["结尾场景"],
                    duration=user_input.duration // 2
                )
            ]
    
    def _generate_character_profiles(self, concept: StoryConcept, user_input: UserInput) -> List[CharacterProfile]:
        """
        生成角色档案
        
        Args:
            concept: 故事概念
            user_input: 用户输入
            
        Returns:
            List[CharacterProfile]: 角色档案列表
        """
        self.logger.info("生成角色档案...")
        
        # 如果用户提供了角色预设信息，优先使用
        if user_input.character_info:
            characters = []
            for name, info in user_input.character_info.items():
                character = CharacterProfile(
                    name=name,
                    age=30,  # 默认年龄
                    personality_traits=["待定"],
                    background_story=info,
                    voice_characteristics={}
                )
                characters.append(character)
            return characters
        
        # 否则通过AI生成
        prompt = f"""
        请为以下短剧概念创建详细的角色档案：

        故事概念：{concept.title}
        核心冲突：{concept.core_conflict}
        主要角色：{', '.join(concept.main_characters)}
        情感基调：{concept.emotional_tone}
        短剧类型：{user_input.genre}

        请为每个主要角色创建档案，严格按照以下JSON格式返回结果：
        {{
            "characters": [
                {{
                    "name": "角色姓名",
                    "age": 25,
                    "personality_traits": ["特征1", "特征2", "特征3"],
                    "background_story": "角色背景故事",
                    "voice_characteristics": {{
                        "tone": "语调描述",
                        "pace": "语速描述",
                        "accent": "口音描述"
                    }}
                }}
            ]
        }}
        
        重要：age字段必须是纯数字，不要包含其他文字。
        """.strip()
        
        try:
            # 使用DashScope替代Ollama
            response = self.dashscope_client.chat_completion(
                model=self.model_name,
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
                    characters_data = json.loads(content)
                except json.JSONDecodeError as e:
                    self.logger.error(f"JSON解析失败，原始内容: {content}")
                    # 尝试清理内容中的控制字符
                    content = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', content)
                    try:
                        characters_data = json.loads(content)
                    except json.JSONDecodeError as e2:
                        self.logger.error(f"清理后仍然解析失败: {e2}")
                        raise e
            else:
                # 如果已经是字典格式，直接使用
                characters_data = content
            
            characters = []
            
            for char_data in characters_data.get("characters", []):
                # 确保age是整数
                age = char_data["age"]
                if isinstance(age, str):
                    # 尝试从字符串中提取数字
                    age_numbers = re.findall(r'\d+', age)
                    if age_numbers:
                        age = int(age_numbers[0])
                    else:
                        age = 30  # 默认年龄
                
                character = CharacterProfile(
                    name=char_data["name"],
                    age=age,
                    personality_traits=char_data["personality_traits"],
                    background_story=char_data["background_story"],
                    voice_characteristics=char_data["voice_characteristics"]
                )
                characters.append(character)
            
            self.logger.info(f"角色档案生成完成，共{len(characters)}个角色")
            return characters
            
        except Exception as e:
            self.error_handler.handle_error(e, context="生成角色档案时发生错误")
            # 返回默认角色
            return [
                CharacterProfile(
                    name=concept.main_characters[0] if concept.main_characters else "主角",
                    age=30,
                    personality_traits=["勇敢", "聪明"],
                    background_story="主要角色",
                    voice_characteristics={"tone": "坚定", "pace": "中等"}
                )
            ]
    
    def _write_dialogues(self, scenes: List[Scene], characters: List[CharacterProfile], 
                        concept: StoryConcept, user_input: UserInput) -> List[Scene]:
        """
        生成旁白脚本而不是角色对话
        
        Args:
            scenes: 场景列表
            characters: 角色档案列表
            concept: 故事概念
            user_input: 用户输入
            
        Returns:
            List[Scene]: 包含旁白的场景列表
        """
        self.logger.info("生成旁白脚本...")
        
        for scene in scenes:
            self.logger.info(f"为场景 {scene.scene_number} 生成旁白...")
            
            # 构建提示词
            prompt = f"""
            请为以下场景生成旁白叙述：
            
            场景编号：{scene.scene_number}
            地点：{scene.location}
            时间：{scene.time}
            参与角色：{', '.join(scene.characters)}
            场景摘要：{scene.actions[0] if scene.actions else ''}
            
            故事背景：
            概念标题：{concept.title}
            核心冲突：{concept.core_conflict}
            情感基调：{concept.emotional_tone}
            短剧类型：{user_input.genre}
            
            请生成一段连贯的旁白叙述，描述场景中的情况、角色的行为和情感变化。
            旁白应该自然流畅，符合故事的情感基调，并推动情节发展。
            """.strip()
            
            try:
                # 使用DashScope替代Ollama
                response = self.dashscope_client.chat_completion(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                # 检查响应是否有效
                if not response or 'message' not in response or 'content' not in response['message']:
                    raise ValueError("API响应格式不正确")
                
                narration = response['message']['content']
                if not narration:
                    raise ValueError("API响应内容为空")
                
                # 将旁白保存为场景的叙述内容
                scene.narration = narration.strip()
                
            except Exception as e:
                self.error_handler.handle_error(e, context=f"为场景 {scene.scene_number} 生成旁白时发生错误")
                # 添加默认旁白
                scene.narration = f"场景 {scene.scene_number} 的旁白叙述"
        
        self.logger.info("旁白脚本生成完成")
        return scenes