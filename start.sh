#!/bin/bash

# 快速启动脚本

echo "🎵 启动Telegram音乐机器人..."

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在，请先运行 ./deploy.sh"
    exit 1
fi

# 检查配置文件
if [ ! -f ".env" ]; then
    echo "❌ 配置文件不存在，请先复制并配置 .env 文件"
    echo "   cp .env.example .env"
    echo "   nano .env"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

# 启动机器人
python bot.py
