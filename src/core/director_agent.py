#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
导演智能体
负责总体协调和流程控制，调度其他智能体
"""

import json
from typing import Dict, Any, Optional, List
from src.utils.logger import Logger
from src.utils.error_handler import ErrorHandler
from src.utils.config_manager import ConfigManager
from src.utils.dashscope_client import DashScopeClient
from src.models.story_models import UserInput, StoryConcept, Script

# LangChain/LangGraph相关导入
from langgraph.graph import StateGraph
from langgraph.constants import START, END
from typing import TypedDict


class WorkflowState(TypedDict):
    """工作流状态"""
    current_stage: str
    completed_steps: List[str]
    generated_assets: Dict[str, Any]
    errors: List[str]
    user_input: Optional[UserInput]
    story_concept: Optional[StoryConcept]
    script: Optional[Script]


class DirectorAgent:
    """导演智能体类"""
    
    def __init__(self):
        """初始化导演智能体"""
        self.logger = Logger("DirectorAgent")
        self.error_handler = ErrorHandler(self.logger)
        self.config = ConfigManager()
        self.workflow_state = {
            "current_stage": "initialization",
            "completed_steps": [],
            "generated_assets": {},
            "errors": []
        }
        self.agents = {}
        
        # 初始化各个专业智能体
        from src.agents.screenwriter_agent import ScreenwriterAgent
        from src.agents.character_agent import CharacterAgent
        from src.agents.visual_agent import VisualAgent
        from src.agents.audio_agent import AudioAgent
        from src.agents.video_agent import VideoAgent
        
        self.screenwriter_agent = ScreenwriterAgent()
        self.character_agent = CharacterAgent()
        self.visual_agent = VisualAgent()
        self.audio_agent = AudioAgent()
        self.video_agent = VideoAgent()
        
        # 使用LangChain StateGraph构建工作流
        self.workflow = self._build_workflow()
        
        self.logger.info("导演智能体初始化完成")
    
    def _build_workflow(self):
        """构建基于LangChain的工作流"""
        # 定义工作流图
        workflow = StateGraph(WorkflowState)
        
        # 添加节点
        workflow.add_node("user_input_processing", self._execute_user_input_processing_langchain)
        workflow.add_node("creative_planning", self._execute_creative_planning_langchain)
        workflow.add_node("script_writing", self._execute_script_writing_langchain)
        workflow.add_node("character_development", self._execute_character_development_langchain)
        workflow.add_node("visual_generation", self._execute_visual_generation_langchain)
        workflow.add_node("audio_generation", self._execute_audio_generation_langchain)
        workflow.add_node("video_synthesis", self._execute_video_synthesis_langchain)
        
        # 设置边连接
        workflow.add_edge(START, "user_input_processing")
        workflow.add_edge("user_input_processing", "creative_planning")
        workflow.add_edge("creative_planning", "script_writing")
        workflow.add_edge("script_writing", "character_development")
        workflow.add_edge("character_development", "visual_generation")
        workflow.add_edge("character_development", "audio_generation")
        workflow.add_edge("visual_generation", "video_synthesis")
        workflow.add_edge("audio_generation", "video_synthesis")
        workflow.add_edge("video_synthesis", END)
        
        return workflow.compile()
    
    def start(self):
        """启动导演智能体"""
        self.logger.info("导演智能体启动...")
        try:
            # 运行工作流
            initial_state = WorkflowState(
                current_stage="initialization",
                completed_steps=[],
                generated_assets={},
                errors=[],
                user_input=None,
                story_concept=None,
                script=None
            )
            
            result = self.workflow.invoke(initial_state)
            self.logger.info("导演智能体运行完成")
            return result
            
        except Exception as e:
            self.error_handler.handle_error(e, context="导演智能体运行过程中发生错误")
    
    # LangChain兼容的方法
    def _execute_user_input_processing_langchain(self, state: WorkflowState) -> WorkflowState:
        """LangChain兼容的用户输入处理方法"""
        self._execute_user_input_processing()
        return state
    
    def _execute_creative_planning_langchain(self, state: WorkflowState) -> WorkflowState:
        """LangChain兼容的创意策划方法"""
        self._execute_creative_planning()
        return state
    
    def _execute_script_writing_langchain(self, state: WorkflowState) -> WorkflowState:
        """LangChain兼容的剧本写作方法"""
        self._execute_script_writing()
        return state
    
    def _execute_character_development_langchain(self, state: WorkflowState) -> WorkflowState:
        """LangChain兼容的角色开发方法"""
        self._execute_character_development()
        return state
    
    def _execute_visual_generation_langchain(self, state: WorkflowState) -> WorkflowState:
        """LangChain兼容的视觉生成方法"""
        self._execute_visual_generation()
        return state
    
    def _execute_audio_generation_langchain(self, state: WorkflowState) -> WorkflowState:
        """LangChain兼容的音频生成方法"""
        self._execute_audio_generation()
        return state
    
    def _execute_video_synthesis_langchain(self, state: WorkflowState) -> WorkflowState:
        """LangChain兼容的视频合成方法"""
        self._execute_video_synthesis()
        return state
    
    def _execute_script_writing(self):
        """执行剧本写作阶段"""
        self.logger.info("执行剧本写作阶段...")
        
        # 获取用户输入（在实际应用中，这应该来自用户界面或命令行参数）
        # 这里我们模拟用户输入处理
        user_input = self._get_user_input()
        
        if not user_input:
            self.logger.warning("未获取到用户输入，使用默认示例")
            user_input = UserInput(
                story_idea="一个关于人工智能与人类友谊的温馨故事",
                genre="科幻",
                duration=120,
                visual_style="写实",
                special_requirements="希望展现未来城市的美景"
            )
        
        # 基于用户输入生成故事概念
        concept = self._generate_story_concept(user_input)
        
        if not concept:
            self.logger.warning("未能生成故事概念，使用默认示例")
            concept = StoryConcept(
                title="AI伙伴",
                core_conflict="人工智能是否能真正理解人类情感",
                main_characters=["小明", "AI助手小智"],
                emotional_tone="温馨感人",
                audience_analysis="适合全年龄段观众",
                feasibility_score=0.9
            )
        
        # 调用编剧智能体创建剧本
        screenwriter = self.agents.get("screenwriter")
        if screenwriter:
            script = screenwriter.create_script_from_concept(concept, user_input)
            self.workflow_state["generated_assets"]["script"] = script
            # 保存剧本到文件
            with open("./output/script.json", "w", encoding="utf-8") as f:
                f.write(script.json(indent=2, ensure_ascii=False))
            self.logger.info("剧本创作完成")
        else:
            self.logger.error("编剧智能体未初始化")
    
    def _get_user_input(self) -> Optional[UserInput]:
        """
        获取用户输入
        在实际应用中，这应该从用户界面或命令行参数获取
        """
        # TODO: 实现真实的用户输入获取逻辑
        # 这里暂时返回None，表示需要实现用户输入处理
        return None
    
    def _generate_story_concept(self, user_input: UserInput) -> Optional[StoryConcept]:
        """
        基于用户输入生成故事概念
        
        Args:
            user_input: 用户输入
            
        Returns:
            StoryConcept: 生成的故事概念
        """
        self.logger.info("基于用户输入生成故事概念...")
        
        try:
            # 构建提示词
            prompt = f"""
            请基于以下用户输入创建一个详细的故事概念：
            
            用户创意：{user_input.story_idea}
            视频类型：{user_input.genre}
            目标时长：{user_input.duration}秒
            视觉风格：{user_input.visual_style}
            特殊要求：{user_input.special_requirements or "无"}
            
            请严格按照以下JSON格式返回结果：
            {{
                "title": "故事标题",
                "core_conflict": "核心冲突",
                "main_characters": ["角色1", "角色2"],
                "emotional_tone": "情感基调",
                "audience_analysis": "目标受众分析",
                "feasibility_score": 0.8
            }}
            """.strip()
            
            # 获取创意策划智能体（如果存在）或直接使用DashScope
            if "creative_planner" in self.agents:
                creative_planner = self.agents.get("creative_planner")
                # TODO: 实现创意策划智能体调用
                pass
            else:
                # 直接使用DashScope生成故事概念
                dashscope_client = DashScopeClient()
                response = dashscope_client.chat_completion(
                    model="qwen-plus",
                    messages=[{"role": "user", "content": prompt}],
                    format="json"
                )
                
                # 解析响应
                if response and 'message' in response and 'content' in response['message']:
                    content = response['message']['content']
                    if isinstance(content, str):
                        concept_data = json.loads(content)
                    else:
                        concept_data = content
                    
                    concept = StoryConcept(
                        title=concept_data["title"],
                        core_conflict=concept_data["core_conflict"],
                        main_characters=concept_data["main_characters"],
                        emotional_tone=concept_data["emotional_tone"],
                        audience_analysis=concept_data["audience_analysis"],
                        feasibility_score=concept_data["feasibility_score"]
                    )
                    
                    self.logger.info("故事概念生成完成")
                    return concept
            
        except Exception as e:
            self.error_handler.handle_error(e, context="生成故事概念时发生错误")
        
        return None
    
    def _execute_character_development(self):
        """执行角色开发阶段"""
        self.logger.info("执行角色开发阶段...")
        
        # 获取已生成的剧本
        script = self.workflow_state["generated_assets"].get("script")
        if not script:
            self.logger.warning("未找到剧本，跳过角色开发阶段")
            return
        
        # 如果剧本中没有角色，跳过角色开发阶段
        if not script.characters:
            self.logger.info("剧本中没有角色，跳过角色开发阶段")
            self.workflow_state["generated_assets"]["enhanced_characters"] = []
            return
        
        # 调用角色智能体增强角色档案
        character_agent = self.agents.get("character")
        if character_agent:
            enhanced_characters = character_agent.enhance_characters_from_script(script)
            self.workflow_state["generated_assets"]["enhanced_characters"] = enhanced_characters
            self.logger.info("角色开发完成")
        else:
            self.logger.error("角色智能体未初始化")
    
    def _execute_visual_generation(self):
        """执行视觉生成阶段"""
        self.logger.info("执行视觉生成阶段...")
        
        # 获取已生成的剧本
        script = self.workflow_state["generated_assets"].get("script")
        if not script:
            self.logger.warning("未找到剧本，跳过视觉生成阶段")
            return
        
        # 调用视觉智能体生成视觉脚本
        visual_agent = self.agents.get("visual")
        if visual_agent:
            visual_script = visual_agent.generate_visual_script(script)
            self.workflow_state["generated_assets"]["visual_script"] = visual_script
            # 保存视觉脚本到文件
            with open("./output/visual_script.json", "w", encoding="utf-8") as f:
                f.write(visual_script.json(indent=2, ensure_ascii=False))
            self.logger.info("视觉脚本生成完成")
        else:
            self.logger.error("视觉智能体未初始化")
    
    def _execute_audio_generation(self):
        """执行音频生成阶段"""
        self.logger.info("执行音频生成阶段...")
        
        # 获取已生成的剧本
        script = self.workflow_state["generated_assets"].get("script")
        if not script:
            self.logger.warning("未找到剧本，跳过音频生成阶段")
            return
        
        # 调用音频智能体生成音频脚本
        audio_agent = self.agents.get("audio")
        if audio_agent:
            audio_script = audio_agent.generate_audio_script(script)
            self.workflow_state["generated_assets"]["audio_script"] = audio_script
            self.logger.info("音频脚本生成完成")
        else:
            self.logger.error("音频智能体未初始化")
    
    def _execute_video_synthesis(self):
        """执行视频合成阶段"""
        self.logger.info("执行视频合成阶段...")
        
        # 获取已生成的剧本、视觉脚本和音频脚本
        script = self.workflow_state["generated_assets"].get("script")
        visual_script = self.workflow_state["generated_assets"].get("visual_script")
        audio_script = self.workflow_state["generated_assets"].get("audio_script")
        
        if not script or not visual_script or not audio_script:
            self.logger.warning("未找到必要的素材，跳过视频合成阶段")
            return
        
        # 调用视频智能体合成视频
        video_agent = self.agents.get("video")
        if video_agent:
            video_output = video_agent.synthesize_video(script, visual_script, audio_script)
            self.workflow_state["generated_assets"]["video_output"] = video_output
            self.logger.info("视频合成完成")
        else:
            self.logger.error("视频智能体未初始化")
    
    def _execute_user_input_processing(self):
        """执行用户输入处理阶段"""
        self.logger.info("执行用户输入处理阶段...")
        # TODO: 实现用户输入处理逻辑
        pass
    
    def _execute_creative_planning(self):
        """执行创意策划阶段"""
        self.logger.info("执行创意策划阶段...")
        # TODO: 实现创意策划逻辑
        pass
    
    def should_continue_after_error(self, stage: str, error: Exception) -> bool:
        """根据错误处理策略决定是否继续执行"""
        # TODO: 实现分级错误处理策略
        self.logger.warning(f"阶段 {stage} 发生错误，暂定继续执行")
        return True
    
    def monitor_progress(self):
        """监控进度"""
        # TODO: 实现进度监控逻辑
        progress_info = {
            "current_stage": self.workflow_state["current_stage"],
            "completed_steps": len(self.workflow_state["completed_steps"]),
            "total_errors": len(self.workflow_state["errors"])
        }
        self.logger.info(f"进度信息: {progress_info}")
        return progress_info
    
    def handle_error(self, error: Exception):
        """处理错误"""
        # TODO: 实现错误处理逻辑
        self.error_handler.handle_error(error, context="导演智能体错误处理")
        self.workflow_state["errors"].append(str(error))
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """获取工作流状态"""
        return self.workflow_state.copy()
    
    def save_checkpoint(self):
        """保存检查点"""
        # TODO: 实现进度保存和断点续传
        self.logger.info("保存检查点...")
        self.workflow_state["checkpoint_time"] = self.config.get("system.time", "unknown")