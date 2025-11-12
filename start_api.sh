#!/bin/bash

# 启动AI短剧生成系统API服务

echo "启动AI短剧生成系统API服务..."

# 激活conda环境
source $(conda info --base)/etc/profile.d/conda.sh
conda activate ai-short-film

# 启动API服务
cd /Users/mac/Documents/Qorder/video/src/services
python api_service.py

echo "API服务已启动，访问地址: http://localhost:8000"