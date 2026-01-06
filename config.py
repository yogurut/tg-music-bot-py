"""
配置文件 - 加载环境变量和系统配置
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 基础路径
BASE_DIR = Path(__file__).parent
DOWNLOAD_PATH = Path(os.getenv('DOWNLOAD_PATH', './downloads'))
LOG_PATH = Path('./logs')

# 创建必要的目录
DOWNLOAD_PATH.mkdir(exist_ok=True)
LOG_PATH.mkdir(exist_ok=True)

# Telegram配置
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("请在.env文件中设置TELEGRAM_BOT_TOKEN")

# Spotify配置
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_ENABLED = bool(SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET)

# 下载限制
MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', '50'))
MAX_SONG_DURATION = int(os.getenv('MAX_SONG_DURATION', '600'))

# 数据库配置
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///./music_bot.db')

# 管理员配置
ADMIN_USER_IDS = [
    int(uid.strip())
    for uid in os.getenv('ADMIN_USER_IDS', '').split(',')
    if uid.strip()
]

# 日志配置
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', str(LOG_PATH / 'bot.log'))

# 搜索配置
SEARCH_RESULTS_LIMIT = 5
CACHE_EXPIRE_MINUTES = 30

# 按钮配置
BUTTON_COLUMNS = 1  # 每行显示几个按钮
