#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI短剧生成系统主入口
"""

import os
import sys

# 将src目录添加到Python路径中
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.director_agent import DirectorAgent
from src.utils.logger import Logger


def main():
    """系统主函数"""
    logger = Logger("Main")
    logger.info("AI短剧生成系统启动...")
    
    try:
        # 初始化导演智能体
        director = DirectorAgent()
        
        # 启动系统
        director.start()
        
        # 输出最终状态
        status = director.get_workflow_status()
        logger.info(f"系统运行完成，最终状态: {status}")
        
    except Exception as e:
        logger.error(f"系统运行过程中发生未处理的异常: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()