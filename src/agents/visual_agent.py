#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
视觉生成智能体
负责将剧本转换为视觉脚本，生成场景视觉描述、镜头角度和视觉效果等
"""

import json
import os
import requests
from typing import List, Dict, Any
from src.utils.logger import Logger
from src.utils.error_handler import ErrorHandler
from src.utils.dashscope_client import DashScopeClient
from src.models.story_models import Script, VisualScript, Scene


class VisualAgent:
    """视觉生成智能体类"""
    
    def __init__(self):
        """初始化视觉生成智能体"""
        self.logger = Logger("VisualAgent")
        self.error_handler = ErrorHandler(self.logger)
        # 使用DashScope客户端替代Ollama
        self.dashscope_client = DashScopeClient()
        self.text_model_name = "qwen-plus"  # 文本生成模型
        self.image_model_name = "wan2.2-t2i-plus"  # 文生图模型
        # 确保输出目录存在
        self.output_dir = "./output/scenes"
        os.makedirs(self.output_dir, exist_ok=True)
        self.logger.info("视觉生成智能体初始化完成")
    
    def generate_visual_script(self, script: Script) -> VisualScript:
        """
        根据剧本生成视觉脚本
        
        Args:
            script: 剧本对象
            
        Returns:
            VisualScript: 视觉脚本对象
        """
        self.logger.info(f"开始为剧本 '{script.title}' 生成视觉脚本")
        
        try:
            # 为每个场景生成视觉描述
            scene_descriptions = self._generate_scene_descriptions(script)
            
            # 生成镜头角度
            camera_angles = self._generate_camera_angles(script)
            
            # 生成视觉效果
            visual_effects = self._generate_visual_effects(script)
            
            # 生成风格参考
            style_references = self._generate_style_references(script)
            
            # 为每个场景生成图片
            scene_images = self._generate_scene_images(script, scene_descriptions)
            
            # 创建视觉脚本对象
            visual_script = VisualScript(
                scene_descriptions=scene_descriptions,
                camera_angles=camera_angles,
                visual_effects=visual_effects,
                style_references=style_references,
                scene_images=scene_images
            )
            
            self.logger.info(f"剧本 '{script.title}' 的视觉脚本生成完成")
            return visual_script
            
        except Exception as e:
            self.error_handler.handle_error(e, context="生成视觉脚本过程中发生错误")
            raise
    
    def _generate_scene_descriptions(self, script: Script) -> List[Dict[str, str]]:
        """
        为每个场景生成详细的视觉描述
        
        Args:
            script: 剧本对象
            
        Returns:
            List[Dict[str, str]]: 场景描述列表
        """
        self.logger.info("生成场景视觉描述")
        
        scene_descriptions = []
        
        for scene in script.scenes:
            try:
                # 构建提示词
                prompt = f"""
                请为以下场景生成详细的视觉描述：
                
                剧本标题：{script.title}
                剧本类型：{script.genre}
                情感基调：{script.emotional_tone}
                视觉风格：{script.visual_style}
                
                场景信息：
                编号：{scene.scene_number}
                地点：{scene.location}
                时间：{scene.time}
                出现场角：{', '.join(scene.characters) if scene.characters else '无特定角色'}
                动作描述：{', '.join(scene.actions)}
                
                请提供以下信息：
                1. 场景环境的详细描述（建筑、装饰、光线等）
                2. {'每个角色的外观和服装描述' if scene.characters else '场景中可能涉及的人物或生物描述'}
                3. 场景的整体氛围和色调
                4. 任何重要的视觉元素或道具
                
                请以JSON格式返回结果，格式如下：
                {{
                    "scene_number": "{scene.scene_number}",
                    "environment": "环境描述",
                    "characters": "{'角色外观和服装描述' if scene.characters else '场景中人物或生物描述'}",
                    "atmosphere": "整体氛围描述",
                    "key_elements": "重要视觉元素"
                }}
                """.strip()
                
                # 使用DashScope替代Ollama
                response = self.dashscope_client.chat_completion(
                    model=self.text_model_name,
                    messages=[{"role": "user", "content": prompt}]
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
                        scene_desc = json.loads(content)
                    except json.JSONDecodeError as e:
                        self.logger.error(f"JSON解析失败，原始内容: {content}")
                        raise e
                else:
                    # 如果已经是字典格式，直接使用
                    scene_desc = content
                
                # 确保所有字段都是字符串类型
                scene_desc["scene_number"] = str(scene_desc["scene_number"])
                scene_desc["characters"] = str(scene_desc["characters"])
                scene_desc["key_elements"] = str(scene_desc["key_elements"])
                scene_descriptions.append(scene_desc)
                
            except Exception as e:
                self.error_handler.handle_error(e, context=f"生成场景 {scene.scene_number} 视觉描述时发生错误")
                # 添加默认描述
                scene_descriptions.append({
                    "scene_number": str(scene.scene_number),
                    "environment": f"场景 {scene.scene_number} 的环境描述",
                    "characters": "默认角色描述" if scene.characters else "默认场景描述",
                    "atmosphere": "默认氛围",
                    "key_elements": "默认视觉元素"
                })
        
        self.logger.info("场景视觉描述生成完成")
        return scene_descriptions
    
    def _generate_camera_angles(self, script: Script) -> List[str]:
        """
        生成适合剧本的镜头角度建议
        
        Args:
            script: 剧本对象
            
        Returns:
            List[str]: 镜头角度列表
        """
        self.logger.info("生成镜头角度建议")
        
        try:
            # 构建提示词
            prompt = f"""
            请为以下剧本生成适合的镜头角度建议：

            剧本标题：{script.title}
            剧本类型：{script.genre}
            情感基调：{script.emotional_tone}
            视觉风格：{script.visual_style}

            场景概要：
            """
            
            for scene in script.scenes:
                prompt += f"- 场景 {scene.scene_number}: {scene.location}, {scene.time}, 角色: {', '.join(scene.characters)}\n"
            
            prompt += """
            请提供10个适合该剧本的镜头角度建议，每个建议一行，格式为：
            镜头类型: 使用场景和目的
            
            例如：
            特写镜头: 用于捕捉角色面部表情，表现内心情感
            广角镜头: 用于展示场景全貌，营造空间感
            """
            
            # 使用DashScope替代Ollama
            response = self.dashscope_client.chat_completion(
                model=self.text_model_name,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # 解析响应为列表
            camera_angles = [line.strip() for line in response['message']['content'].split('\n') if line.strip()]
            
            self.logger.info("镜头角度建议生成完成")
            return camera_angles[:10]  # 限制为10个建议
            
        except Exception as e:
            self.error_handler.handle_error(e, context="生成镜头角度建议时发生错误")
            # 返回默认镜头角度
            return [
                "特写镜头: 用于捕捉角色面部表情，表现内心情感",
                "中景镜头: 用于展现角色互动和身体语言",
                "广角镜头: 用于展示场景全貌，营造空间感",
                "俯视镜头: 用于表现角色的渺小或环境的宏大",
                "仰视镜头: 用于表现角色的威严或力量感"
            ]
    
    def _generate_visual_effects(self, script: Script) -> List[str]:
        """
        生成适合剧本的视觉效果建议
        
        Args:
            script: 剧本对象
            
        Returns:
            List[str]: 视觉效果列表
        """
        self.logger.info("生成视觉效果建议")
        
        try:
            # 构建提示词
            prompt = f"""
            请为以下剧本生成适合的视觉效果建议：

            剧本标题：{script.title}
            剧本类型：{script.genre}
            情感基调：{script.emotional_tone}
            视觉风格：{script.visual_style}

            场景概要：
            """
            
            for scene in script.scenes:
                prompt += f"- 场景 {scene.scene_number}: {scene.location}, {scene.time}, 角色: {', '.join(scene.characters)}\n"
            
            prompt += """
            请提供8个适合该剧本的视觉效果建议，每个建议一行，格式为：
            效果类型: 使用场景和目的
            
            例如：
            柔光效果: 用于回忆场景，营造温馨怀旧氛围
            颗粒感: 用于增强画面质感，营造电影感
            """
            
            # 使用DashScope替代Ollama
            response = self.dashscope_client.chat_completion(
                model=self.text_model_name,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # 解析响应为列表
            visual_effects = [line.strip() for line in response['message']['content'].split('\n') if line.strip()]
            
            self.logger.info("视觉效果建议生成完成")
            return visual_effects[:8]  # 限制为8个建议
            
        except Exception as e:
            self.error_handler.handle_error(e, context="生成视觉效果建议时发生错误")
            # 返回默认视觉效果
            return [
                "柔光效果: 用于回忆场景，营造温馨怀旧氛围",
                "颗粒感: 用于增强画面质感，营造电影感",
                "色彩分级: 用于统一画面色调，增强视觉风格",
                "景深效果: 用于突出主体，引导观众注意力"
            ]
    
    def _generate_style_references(self, script: Script) -> List[str]:
        """
        生成视觉风格参考建议
        
        Args:
            script: 剧本对象
            
        Returns:
            List[str]: 风格参考列表
        """
        self.logger.info("生成视觉风格参考建议")
        
        try:
            # 构建提示词
            prompt = f"""
            请为以下剧本生成视觉风格参考建议：

            剧本标题：{script.title}
            剧本类型：{script.genre}
            情感基调：{script.emotional_tone}
            视觉风格：{script.visual_style}

            请提供5个适合该剧本的视觉风格参考，每个建议一行，格式为：
            作品名称: 风格特点和参考价值
            
            例如：
            《Her》: 柔和的色彩搭配和未来感设计，适合表现人与AI的情感连接
            """
            
            # 使用DashScope替代Ollama
            response = self.dashscope_client.chat_completion(
                model=self.text_model_name,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # 解析响应为列表
            style_references = [line.strip() for line in response['message']['content'].split('\n') if line.strip()]
            
            self.logger.info("视觉风格参考建议生成完成")
            return style_references[:5]  # 限制为5个建议
            
        except Exception as e:
            self.error_handler.handle_error(e, context="生成视觉风格参考建议时发生错误")
            # 返回默认风格参考
            return [
                "写实风格: 真实细腻的画面表现，增强观众代入感",
                "电影质感: 专业级色彩处理和光影效果，提升作品品质"
            ]
    
    def _generate_scene_images(self, script: Script, scene_descriptions: List[Dict[str, str]]) -> List[str]:
        """
        为每个场景生成图片
        
        Args:
            script: 剧本对象
            scene_descriptions: 场景描述列表
            
        Returns:
            List[str]: 场景图片路径列表
        """
        self.logger.info("生成场景图片")
        
        scene_images = []
        
        for scene_desc in scene_descriptions:
            try:
                # 构建提示词
                prompt = f"""
                请为以下场景生成图片：

                剧本标题：{script.title}
                剧本类型：{script.genre}
                情感基调：{script.emotional_tone}
                视觉风格：{script.visual_style}

                场景描述：
                ```
                {scene_desc["environment"]}
                {scene_desc["atmosphere"]}
                {scene_desc["key_elements"]}
                ```

                请提供一张不包含人物角色的场景图片，只展示环境和背景元素。
                """
                
                # 使用DashScope文生图API
                response = self.dashscope_client.text_to_image(
                    model=self.image_model_name,
                    prompt=prompt
                )
                
                # 检查响应是否有效
                if not response or 'results' not in response or not response['results']:
                    raise ValueError("API响应格式不正确")
                
                image_url = response['results'][0]['url']
                if not image_url:
                    raise ValueError("API响应内容为空")
                
                # 下载图片
                image_path = os.path.join(self.output_dir, f"scene_{scene_desc['scene_number']}.png")
                image_response = requests.get(image_url)
                if image_response.status_code == 200:
                    with open(image_path, "wb") as f:
                        f.write(image_response.content)
                else:
                    raise Exception(f"下载图片失败: {image_response.status_code}")
                
                scene_images.append(image_path)
                
            except Exception as e:
                self.error_handler.handle_error(e, context=f"生成场景 {scene_desc['scene_number']} 图片时发生错误")
                # 添加默认图片路径
                scene_images.append("default_scene.png")
        
        self.logger.info("场景图片生成完成")
        return scene_images
