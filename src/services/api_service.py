#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API服务
提供基于FastAPI的Web接口，用于访问AI短剧生成系统的各项功能
"""

import os
import sys
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import uvicorn

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.core.director_agent import DirectorAgent
from src.models.story_models import UserInput


class StoryRequest(BaseModel):
    """故事创作请求数据模型"""
    story_idea: str  # 初始故事创意
    genre: str  # 短剧类型
    duration: int  # 目标时长（秒）
    visual_style: str  # 视觉风格偏好
    character_info: Optional[Dict[str, str]] = None  # 角色预设信息
    special_requirements: Optional[str] = None  # 特殊要求说明


class StoryResponse(BaseModel):
    """故事创作响应数据模型"""
    status: str
    message: str
    result: Optional[Dict[str, Any]] = None


# 创建FastAPI应用实例
app = FastAPI(
    title="AI短剧生成系统API",
    description="基于多AI智能体协作的自动化短剧生成系统API接口",
    version="1.0.0"
)

# 全局导演智能体实例
director_agent: Optional[DirectorAgent] = None


@app.on_event("startup")
async def startup_event():
    """应用启动时初始化导演智能体"""
    global director_agent
    try:
        director_agent = DirectorAgent()
    except Exception as e:
        print(f"初始化导演智能体失败: {e}")


@app.get("/")
async def root():
    """根路径，返回API信息"""
    return {
        "message": "欢迎使用AI短剧生成系统API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "message": "API服务运行正常"}


@app.post("/generate-story", response_model=StoryResponse)
async def generate_story(request: StoryRequest, background_tasks: BackgroundTasks):
    """
    生成短剧内容
    """
    if director_agent is None:
        raise HTTPException(status_code=500, detail="导演智能体未初始化")
    
    try:
        # 创建用户输入对象
        user_input = UserInput(
            story_idea=request.story_idea,
            genre=request.genre,
            duration=request.duration,
            visual_style=request.visual_style,
            character_info=request.character_info,
            special_requirements=request.special_requirements
        )
        
        # 启动导演智能体执行任务
        result = director_agent.start()
        
        return StoryResponse(
            status="success",
            message="短剧生成任务已启动",
            result=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成短剧时发生错误: {str(e)}")


@app.get("/status")
async def get_status():
    """
    获取系统状态
    """
    if director_agent is None:
        raise HTTPException(status_code=500, detail="导演智能体未初始化")
    
    try:
        status = director_agent.get_workflow_status()
        return StoryResponse(
            status="success",
            message="获取状态成功",
            result=status
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取状态时发生错误: {str(e)}")


if __name__ == "__main__":
    # 启动API服务
    uvicorn.run(
        "api_service:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["/Users/mac/Documents/Qorder/video/src"]
    )