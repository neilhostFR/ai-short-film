#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
故事相关的数据模型定义
"""

from typing import List, Dict, Optional
from pydantic import BaseModel


class UserInput(BaseModel):
    """用户输入数据模型"""
    story_idea: str  # 初始故事创意
    genre: str  # 短剧类型
    duration: int  # 目标时长（秒）
    visual_style: str  # 视觉风格偏好
    character_info: Optional[Dict[str, str]] = None  # 角色预设信息
    special_requirements: Optional[str] = None  # 特殊要求说明


class StoryConcept(BaseModel):
    """故事概念数据模型"""
    title: str  # 概念标题
    core_conflict: str  # 核心冲突
    main_characters: List[str]  # 主要角色
    emotional_tone: str  # 情感基调
    audience_analysis: str  # 目标受众分析
    feasibility_score: float  # 制作可行性评分


class CharacterProfile(BaseModel):
    """角色档案数据模型"""
    name: str  # 角色姓名
    age: int  # 年龄
    personality_traits: List[str]  # 性格特征
    background_story: str  # 背景故事
    voice_characteristics: Dict[str, str]  # 声音特征
    # 扩展字段
    motivations: Optional[List[str]] = None  # 动机
    fears: Optional[List[str]] = None  # 恐惧
    relationships: Optional[List[Dict[str, str]]] = None  # 关系
    character_arc: Optional[str] = None  # 角色成长弧线
    visual_description: Optional[str] = None  # 视觉描述
    image_path: Optional[str] = None  # 图像路径


class Scene(BaseModel):
    """场景数据模型"""
    scene_number: int  # 场景编号
    location: str  # 地点
    time: str  # 时间
    characters: List[str]  # 出现场角
    dialogue: List[Dict[str, str]]  # 对话内容 {角色名: 台词}
    actions: List[str]  # 动作描述
    duration: int  # 场景时长（秒）
    narration: Optional[str] = None  # 旁白叙述


class Script(BaseModel):
    """剧本数据模型"""
    title: str  # 剧本标题
    genre: str  # 类型
    total_duration: int  # 总时长（秒）
    scenes: List[Scene]  # 场景列表
    characters: List[CharacterProfile]  # 角色列表
    emotional_tone: Optional[str] = None  # 情感基调
    visual_style: Optional[str] = None  # 视觉风格


class VisualScript(BaseModel):
    """视觉脚本数据模型"""
    scene_descriptions: List[Dict[str, str]]  # 场景描述
    camera_angles: List[str]  # 镜头角度
    visual_effects: List[str]  # 视觉效果
    style_references: List[str]  # 风格参考
    scene_images: Optional[List[str]] = None  # 场景图片路径列表


class AudioScript(BaseModel):
    """音频脚本数据模型"""
    background_music: List[str]  # 背景音乐描述
    sound_effects: List[str]  # 音效描述
    voice_lines: List[Dict[str, str]]  # 语音台词 {角色名: 台词}


class VideoOutput(BaseModel):
    """最终视频输出数据模型"""
    file_path: str  # 文件路径
    duration: int  # 时长（秒）
    resolution: str  # 分辨率
    file_size: int  # 文件大小（MB）
    quality_score: float  # 质量评分