#!/bin/bash

# VPS部署脚本 - 适用于Ubuntu/Debian系统

set -e

echo "🚀 开始部署Telegram音乐机器人..."

# 1. 更新系统
echo "📦 更新系统包..."
sudo apt-get update
sudo apt-get upgrade -y

# 2. 安装Python和必要工具
echo "🐍 安装Python 3.10+..."
sudo apt-get install -y python3 python3-pip python3-venv

# 3. 安装FFmpeg（用于音频处理）
echo "🎵 安装FFmpeg..."
sudo apt-get install -y ffmpeg

# 4. 创建虚拟环境
echo "📁 创建Python虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 5. 安装Python依赖
echo "📚 安装Python依赖包..."
pip install --upgrade pip
pip install -r requirements.txt

# 6. 配置环境变量
if [ ! -f .env ]; then
    echo "⚙️ 创建配置文件..."
    cp .env.example .env
    echo ""
    echo "❗ 请编辑 .env 文件并填入你的配置信息："
    echo "   - TELEGRAM_BOT_TOKEN（必填）"
    echo "   - SPOTIFY_CLIENT_ID（可选）"
    echo "   - SPOTIFY_CLIENT_SECRET（可选）"
    echo ""
    read -p "按Enter继续编辑配置文件..."
    nano .env
fi

# 7. 创建必要目录
echo "📂 创建必要目录..."
mkdir -p downloads logs

# 8. 测试运行
echo "✅ 部署完成！"
echo ""
echo "使用以下命令运行机器人："
echo "  source venv/bin/activate"
echo "  python bot.py"
echo ""
echo "或使用systemd服务（见deploy_systemd.sh）"
