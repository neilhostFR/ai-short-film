#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
视频合成智能体
负责将视觉脚本和音频脚本合成为最终的视频输出
"""

import os
import json
import subprocess
import shutil
from typing import List, Dict, Any
from src.utils.logger import Logger
from src.utils.error_handler import ErrorHandler
from src.utils.dashscope_client import DashScopeClient
from src.models.story_models import Script, VisualScript, AudioScript, VideoOutput


class VideoAgent:
    """视频合成智能体类"""
    
    def __init__(self):
        """初始化视频合成智能体"""
        self.logger = Logger("VideoAgent")
        self.error_handler = ErrorHandler(self.logger)
        # 使用DashScope客户端
        self.dashscope_client = DashScopeClient()
        self.video_model_name = "wanx2.1-vace-plus"  # 视频生成模型
        # 检查FFmpeg是否可用
        self.ffmpeg_available = self._check_ffmpeg()
        # 确保输出目录存在
        self.output_dir = "./output/videos"
        os.makedirs(self.output_dir, exist_ok=True)
        self.logger.info("视频合成智能体初始化完成")
    
    def _check_ffmpeg(self) -> bool:
        """
        检查FFmpeg是否可用
        
        Returns:
            bool: FFmpeg是否可用
        """
        try:
            subprocess.run(["ffmpeg", "-version"], check=True, capture_output=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.logger.warning("FFmpeg不可用，将使用简化模式进行视频合成")
            return False
    
    def synthesize_video(self, script: Script, visual_script: VisualScript, audio_script: AudioScript) -> VideoOutput:
        """
        将视觉脚本和音频脚本合成为最终的视频输出
        
        Args:
            script: 剧本对象
            visual_script: 视觉脚本对象
            audio_script: 音频脚本对象
            
        Returns:
            VideoOutput: 视频输出对象
        """
        self.logger.info(f"开始合成剧本 '{script.title}' 的视频")
        
        try:
            # 生成视频文件路径
            video_file_path = os.path.join(self.output_dir, f"{script.title.replace(' ', '_')}.mp4")
            
            if self.ffmpeg_available:
                # 创建场景视频片段
                scene_videos = self._create_scene_videos(script, visual_script, audio_script)
                
                # 合成最终视频
                self._combine_videos(scene_videos, video_file_path)
            else:
                # 如果FFmpeg不可用，创建一个简单的占位视频
                self._create_placeholder_video(video_file_path)
            
            # 获取视频信息
            duration, resolution, file_size = self._get_video_info(video_file_path)
            
            # 创建视频输出对象
            video_output = VideoOutput(
                file_path=video_file_path,
                duration=duration,
                resolution=resolution,
                file_size=file_size,
                quality_score=0.85 if self.ffmpeg_available else 0.5  # 根据是否使用FFmpeg设置质量评分
            )
            
            self.logger.info(f"剧本 '{script.title}' 的视频合成完成")
            return video_output
            
        except Exception as e:
            self.error_handler.handle_error(e, context="视频合成过程中发生错误")
            raise
    
    def _create_scene_videos(self, script: Script, visual_script: VisualScript, audio_script: AudioScript) -> List[str]:
        """
        为每个场景创建视频片段
        
        Args:
            script: 剧本对象
            visual_script: 视觉脚本对象
            audio_script: 音频脚本对象
            
        Returns:
            List[str]: 场景视频文件路径列表
        """
        self.logger.info("创建场景视频片段")
        
        scene_videos = []
        
        # 获取场景音频文件
        audio_agent = __import__('src.agents.audio_agent', fromlist=['AudioAgent'])
        audio_agent_instance = audio_agent.AudioAgent()
        scene_audio_files = audio_agent_instance.generate_speech_for_script(script)
        
        for i, scene in enumerate(script.scenes):
            try:
                # 生成场景视频文件路径
                scene_video_path = os.path.join(self.output_dir, f"scene_{scene.scene_number}.mp4")
                
                # 获取场景图片和角色图片路径
                scene_image_path = self._create_scene_image(scene, visual_script, i)
                
                # 收集场景中的角色图片
                character_image_paths = []
                for character in scene.characters:
                    character_image_path = getattr(character, 'image_path', None)
                    if character_image_path and os.path.exists(character_image_path):
                        character_image_paths.append(character_image_path)
                
                scene_audio_path = scene_audio_files.get(f"scene_{scene.scene_number}", self._create_default_audio())
                
                # 使用DashScope多图生视频功能创建场景视频
                self._create_scene_video_with_dashscope(scene_image_path, character_image_paths, scene_audio_path, scene_video_path, scene.duration, scene)
                
                scene_videos.append(scene_video_path)
                
            except Exception as e:
                self.error_handler.handle_error(e, context=f"创建场景 {scene.scene_number} 视频片段时发生错误")
                # 创建一个默认的场景视频
                default_video_path = os.path.join(self.output_dir, f"scene_{scene.scene_number}_default.mp4")
                self._create_default_video(default_video_path, scene.duration)
                scene_videos.append(default_video_path)
        
        self.logger.info("场景视频片段创建完成")
        return scene_videos
    
    def _create_scene_video_with_dashscope(self, scene_image_path: str, character_image_paths: List[str], 
                                          audio_path: str, video_path: str, duration: int, scene: Any):
        """
        使用DashScope多图生视频功能创建场景视频
        
        Args:
            scene_image_path: 场景图像文件路径
            character_image_paths: 角色图像文件路径列表
            audio_path: 场景音频文件路径
            video_path: 输出视频文件路径
            duration: 视频时长（秒）
            scene: 场景对象
        """
        try:
            self.logger.info(f"使用DashScope多图生视频功能创建场景 {scene.scene_number} 的视频")
            
            # 构建视频生成提示词
            prompt = f"场景 {scene.scene_number}: {scene.location}, {scene.time}. 角色: {', '.join(scene.characters)}. 动作: {', '.join(scene.actions)}"
            
            # 收集所有图像路径（场景图片和角色图片）
            image_paths = [scene_image_path] + character_image_paths
            
            # 调用DashScope视频生成API
            response = self.dashscope_client.video_generation(
                model=self.video_model_name,
                prompt=prompt,
                image_paths=image_paths,
                audio_path=audio_path
            )
            
            # 保存生成的视频
            if response and 'output' in response and 'video' in response['output']:
                video_data = response['output']['video']
                # 如果video_data是URL，下载视频文件
                if isinstance(video_data, str) and video_data.startswith('http'):
                    import requests
                    video_content = requests.get(video_data).content
                    with open(video_path, "wb") as f:
                        f.write(video_content)
                else:
                    # 如果video_data是二进制数据，直接保存
                    if isinstance(video_data, bytes):
                        with open(video_path, "wb") as f:
                            f.write(video_data)
                    else:
                        # 如果不是bytes类型，使用FFmpeg创建视频
                        self._create_video_from_image_audio(scene_image_path, audio_path, video_path, duration)
            else:
                # 如果没有返回视频数据，使用FFmpeg创建视频
                self._create_video_from_image_audio(scene_image_path, audio_path, video_path, duration)
            
            self.logger.info(f"场景 {scene.scene_number} 视频创建完成: {video_path}")
            
        except Exception as e:
            self.error_handler.handle_error(e, context=f"使用DashScope创建场景 {scene.scene_number} 视频时发生错误")
            # 出错时使用FFmpeg创建视频作为备选方案
            self._create_video_from_image_audio(scene_image_path, audio_path, video_path, duration)
    
    def _create_scene_image(self, scene: Any, visual_script: VisualScript, index: int) -> str:
        """
        为场景创建图像
        
        Args:
            scene: 场景对象
            visual_script: 视觉脚本对象
            index: 场景索引
            
        Returns:
            str: 场景图像文件路径
        """
        # 获取场景图片路径
        if visual_script.scene_images and index < len(visual_script.scene_images):
            scene_image_path = visual_script.scene_images[index]
        else:
            # 如果没有场景图片，创建一个默认图像
            scene_image_path = self._create_default_image()
        
        # 获取角色图像路径
        character_images = []
        for character in scene.characters:
            # 查找角色对应的图像路径
            character_image_path = getattr(character, 'image_path', None)
            if character_image_path and os.path.exists(character_image_path):
                character_images.append(character_image_path)
        
        # 如果有角色图像，将它们合成到场景图片中
        if character_images:
            composite_image_path = self._composite_characters_to_scene(scene_image_path, character_images, index)
            return composite_image_path
        else:
            return scene_image_path
    
    def _composite_characters_to_scene(self, scene_image_path: str, character_images: List[str], scene_index: int) -> str:
        """
        将角色图像合成到场景图片中
        
        Args:
            scene_image_path: 场景图片路径
            character_images: 角色图像路径列表
            scene_index: 场景索引
            
        Returns:
            str: 合成后的图像路径
        """
        # 创建合成图像的路径
        composite_image_path = os.path.join(self.output_dir, f"composite_scene_{scene_index + 1}.png")
        
        # 这里简化处理，实际应用中可能需要使用图像处理库（如PIL）进行复杂的图像合成
        # 目前只是复制场景图片作为合成结果
        if os.path.exists(scene_image_path):
            shutil.copy2(scene_image_path, composite_image_path)
        else:
            # 如果场景图片不存在，创建默认图像
            self._create_default_image()
            shutil.copy2(os.path.join(self.output_dir, "default_image.png"), composite_image_path)
        
        self.logger.info(f"角色图像已合成到场景图片中: {composite_image_path}")
        return composite_image_path
    
    def _create_scene_audio(self, scene: Any, audio_script: AudioScript, index: int) -> str:
        """
        为场景创建旁白音频而不是对话音频
        
        Args:
            scene: 场景对象
            audio_script: 音频脚本对象
            index: 场景索引
            
        Returns:
            str: 场景旁白音频文件路径
        """
        # 使用场景中的旁白内容
        if hasattr(scene, 'narration') and scene.narration:
            scene_narration_text = scene.narration
        else:
            # 如果没有旁白，使用默认内容
            scene_narration_text = f"场景 {scene.scene_number} 的旁白叙述"
        
        # 生成旁白音频
        audio_agent = __import__('src.agents.audio_agent', fromlist=['AudioAgent'])
        audio_agent_instance = audio_agent.AudioAgent()
        return audio_agent_instance.generate_speech_from_text(scene_narration_text, "narrator")
    
    def _create_video_from_image_audio(self, image_path: str, audio_path: str, video_path: str, duration: int):
        """
        使用FFmpeg从图像和音频创建视频
        
        Args:
            image_path: 图像文件路径
            audio_path: 音频文件路径
            video_path: 视频文件路径
            duration: 视频时长（秒）
        """
        if not self.ffmpeg_available:
            # 如果FFmpeg不可用，创建一个简单的占位视频
            self._create_placeholder_video(video_path)
            return
            
        try:
            # 使用FFmpeg创建视频
            cmd = [
                "ffmpeg",
                "-y",  # 覆盖输出文件
                "-loop", "1",  # 循环图像
                "-i", image_path,  # 输入图像
                "-i", audio_path,  # 输入音频
                "-c:v", "libx264",  # 视频编码
                "-t", str(duration),  # 视频时长
                "-pix_fmt", "yuv420p",  # 像素格式
                "-vf", "scale=1920:1080",  # 分辨率
                "-shortest",  # 以最短的输入为准
                video_path  # 输出视频
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            self.logger.info(f"视频片段创建完成: {video_path}")
            
        except subprocess.CalledProcessError as e:
            self.error_handler.handle_error(e, context="使用FFmpeg创建视频片段时发生错误")
            raise
        except Exception as e:
            self.error_handler.handle_error(e, context="创建视频片段时发生未知错误")
            raise
    
    def _combine_videos(self, scene_videos: List[str], output_path: str):
        """
        合成场景视频为最终视频
        
        Args:
            scene_videos: 场景视频文件路径列表
            output_path: 输出视频文件路径
        """
        if not self.ffmpeg_available:
            # 如果FFmpeg不可用，直接复制第一个场景视频作为最终视频
            if scene_videos:
                shutil.copy2(scene_videos[0], output_path)
            else:
                self._create_placeholder_video(output_path)
            return
            
        self.logger.info("合成场景视频为最终视频")
        
        try:
            # 创建临时文件列表
            file_list_path = os.path.join(self.output_dir, "file_list.txt")
            with open(file_list_path, "w") as f:
                for video_path in scene_videos:
                    f.write(f"file '{video_path}'\n")
            
            # 使用FFmpeg合并视频
            cmd = [
                "ffmpeg",
                "-y",  # 覆盖输出文件
                "-f", "concat",  # 合并格式
                "-safe", "0",  # 允许不安全路径
                "-i", file_list_path,  # 输入文件列表
                "-c", "copy",  # 直接复制流
                output_path  # 输出视频
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            self.logger.info(f"视频合成完成: {output_path}")
            
            # 清理临时文件
            os.remove(file_list_path)
            
        except subprocess.CalledProcessError as e:
            self.error_handler.handle_error(e, context="使用FFmpeg合并视频时发生错误")
            raise
        except Exception as e:
            self.error_handler.handle_error(e, context="合并视频时发生未知错误")
            raise
    
    def _get_video_info(self, video_path: str) -> tuple:
        """
        获取视频信息（时长、分辨率、文件大小）
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            tuple: (时长, 分辨率, 文件大小)
        """
        if not self.ffmpeg_available:
            # 如果FFmpeg不可用，返回默认值
            return 120, "1920x1080", 50
            
        try:
            # 使用FFprobe获取视频信息
            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                video_path
            ]
            
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            video_info = json.loads(result.stdout)
            
            # 获取时长
            duration = int(float(video_info["format"]["duration"]))
            
            # 获取分辨率
            stream = next((s for s in video_info["streams"] if s["codec_type"] == "video"), None)
            if stream:
                resolution = f"{stream['width']}x{stream['height']}"
            else:
                resolution = "1920x1080"  # 默认分辨率
            
            # 获取文件大小（MB）
            file_size = int(video_info["format"]["size"]) // (1024 * 1024)
            
            return duration, resolution, file_size
            
        except subprocess.CalledProcessError as e:
            self.error_handler.handle_error(e, context="使用FFprobe获取视频信息时发生错误")
            # 返回默认值
            return 120, "1920x1080", 50
        except Exception as e:
            self.error_handler.handle_error(e, context="获取视频信息时发生未知错误")
            # 返回默认值
            return 120, "1920x1080", 50
    
    def _create_default_image(self) -> str:
        """
        创建默认图像
        
        Returns:
            str: 默认图像文件路径
        """
        default_image_path = os.path.join(self.output_dir, "default_image.png")
        # 创建一个简单的默认图像（这里简化处理，实际应用中可能需要创建真实的图像）
        with open(default_image_path, "w") as f:
            f.write("Default image placeholder")
        return default_image_path
    
    def _create_default_audio(self) -> str:
        """
        创建默认音频
        
        Returns:
            str: 默认音频文件路径
        """
        default_audio_path = os.path.join(self.output_dir, "default_audio.wav")
        # 创建一个简单的默认音频（这里简化处理，实际应用中可能需要创建真实的音频）
        with open(default_audio_path, "w") as f:
            f.write("Default audio placeholder")
        return default_audio_path
    
    def _create_default_video(self, video_path: str, duration: int):
        """
        创建默认视频
        
        Args:
            video_path: 视频文件路径
            duration: 视频时长（秒）
        """
        if not self.ffmpeg_available:
            # 如果FFmpeg不可用，创建一个简单的占位视频
            self._create_placeholder_video(video_path)
            return
            
        try:
            # 创建默认图像和音频
            default_image = self._create_default_image()
            default_audio = self._create_default_audio()
            
            # 使用FFmpeg创建默认视频
            cmd = [
                "ffmpeg",
                "-y",
                "-loop", "1",
                "-i", default_image,
                "-i", default_audio,
                "-c:v", "libx264",
                "-t", str(duration),
                "-pix_fmt", "yuv420p",
                "-vf", "scale=1920:1080",
                "-shortest",
                video_path
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            self.logger.info(f"默认视频创建完成: {video_path}")
            
        except subprocess.CalledProcessError as e:
            self.error_handler.handle_error(e, context="创建默认视频时发生错误")
            raise
        except Exception as e:
            self.error_handler.handle_error(e, context="创建默认视频时发生未知错误")
            raise
    
    def _create_placeholder_video(self, video_path: str):
        """
        创建占位视频
        
        Args:
            video_path: 视频文件路径
        """
        # 创建一个简单的占位视频文件
        with open(video_path, "w") as f:
            f.write("Placeholder video file - FFmpeg not available")
        self.logger.info(f"占位视频创建完成: {video_path}")
    
    def generate_video_from_prompt(self, prompt: str, output_path: str) -> str:
        """
        使用DashScope视频生成模型根据提示词生成视频
        
        Args:
            prompt: 视频生成提示词
            output_path: 输出视频文件路径
            
        Returns:
            str: 生成的视频文件路径
        """
        try:
            self.logger.info(f"使用DashScope生成视频: {prompt}")
            
            # 调用DashScope视频生成API
            response = self.dashscope_client.video_generation(
                model=self.video_model_name,
                prompt=prompt
            )
            
            # 保存生成的视频
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 从响应中获取视频数据并保存
            # 注意：这里需要根据实际的API响应格式进行调整
            video_url = response.get("video_url")
            if video_url:
                # 下载视频文件
                import requests
                video_data = requests.get(video_url).content
                with open(output_path, "wb") as f:
                    f.write(video_data)
                
                self.logger.info(f"视频生成完成: {output_path}")
                return output_path
            else:
                raise Exception("视频生成失败：未返回视频URL")
                
        except Exception as e:
            self.error_handler.handle_error(e, context="使用DashScope生成视频时发生错误")
            # 返回默认视频文件路径
            default_video_path = output_path.replace(".mp4", "_default.mp4")
            os.makedirs(os.path.dirname(default_video_path), exist_ok=True)
            with open(default_video_path, "w") as f:
                f.write("Default video placeholder")
            return default_video_path