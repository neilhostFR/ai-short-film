# AI短剧生成系统

## 项目概述

随着人工智能技术的快速发展，多模态内容生成能力已达到商业化应用水平。本项目旨在构建一个基于多AI智能体协作的自动化短剧生成系统，能够将用户输入的简单故事创意自动转化为完整的短视频内容。该系统将大幅降低视频创作的技术门槛和时间成本，使普通用户也能轻松创作专业质量的短剧内容。

## 系统架构

系统采用多智能体协作的流水线架构，模拟真实影视制作团队的专业分工模式。每个智能体都是特定领域的专家，通过中央协调器实现高效协作和数据流转。

### 核心组件

系统由七大核心智能体组成：
- **导演智能体**：总体协调和流程控制
- **创意策划智能体**：故事概念生成和创意发散
- **编剧智能体**：剧本创作和情节设计
- **角色扮演智能体**：角色塑造和对话生成
- **视觉生成智能体**：图像和视频内容生成
- **音频生成智能体**：语音、音乐和音效制作
- **视频合成智能体**：最终视频的剪辑和合成

### 技术架构

- **智能体编排**：LangChain
- **大语言模型**：阿里云DashScope的Qwen系列模型
  - 文本生成：qwen-plus
  - 语音合成：Qwen3-TTS
- **视觉生成**：wan2.2-t2i-plus文生图模型
- **视频生成**：wanx2.1-vace-plus视频模型
- **视频处理**：FFmpeg
- **开发语言**：Python

## 环境配置

### DashScope API密钥配置

本项目使用阿里云DashScope提供的AI服务，需要配置API密钥才能正常使用。

1. 获取API密钥：
   - 访问阿里云官网并登录账号
   - 进入DashScope控制台
   - 创建或获取现有的API密钥

2. 设置环境变量：
   - 在项目根目录下找到`set_env.sh`文件
   - 将文件中的`YOUR_API_KEY`替换为您的实际API密钥
   - 运行命令：`source set_env.sh`

### 依赖安装

确保已安装所有项目依赖：
```bash
pip install -r requirements.txt
```

### 其他服务

- **FFmpeg**：用于视频处理，需安装到系统中

## 使用说明

### 运行项目

1. 设置环境变量：
```bash
source set_env.sh
```

2. 激活conda环境：
```bash
conda activate ai-short-film
```

3. 运行主程序：
```bash
python src/main.py
```

### 运行API服务

1. 设置环境变量：
```bash
source set_env.sh
```

2. 激活conda环境：
```bash
conda activate ai-short-film
```

3. 启动API服务：
```bash
# 方式一：直接运行
cd src/services
python api_service.py

# 方式二：使用启动脚本
./start_api.sh
```

4. 访问API：
   - API文档：http://localhost:8000/docs
   - 健康检查：http://localhost:8000/health
   - 故事生成：POST http://localhost:8000/generate-story

### API接口说明

- `GET /` - 根路径，返回API信息
- `GET /health` - 健康检查接口
- `POST /generate-story` - 生成短剧内容接口
- `GET /status` - 获取系统状态接口
- `GET /docs` - 自动生成的Swagger API文档

### 配置说明

项目配置文件位于`src/config/app_config.yaml`，主要配置项包括：
- 模型配置：指定使用的各种AI模型
- 路径配置：输出目录、临时目录等
- API配置：服务主机和端口

## 项目特点

- **创作民主化**：让不具备专业视频制作技能的用户也能创作高质量短剧内容
- **效率革命**：将传统需要数天甚至数周的创作过程压缩到分钟级别完成
- **成本优化**：显著降低视频制作的人力成本、时间成本和设备投入
- **创意无限**：基于AI的强大生成能力，突破传统创作的技术限制和想象力边界
