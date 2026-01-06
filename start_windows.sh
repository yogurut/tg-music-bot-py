# Windows启动脚本 (Git Bash)

echo "🎵 启动Telegram音乐机器人..."

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在，请先创建："
    echo "   python -m venv venv"
    echo "   source venv/Scripts/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# 检查配置文件
if [ ! -f ".env" ]; then
    echo "❌ 配置文件不存在，请先复制并配置 .env 文件"
    echo "   cp .env.example .env"
    exit 1
fi

# 激活虚拟环境（Windows）
source venv/Scripts/activate

# 启动机器人
python bot.py
