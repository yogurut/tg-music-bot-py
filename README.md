# Telegram 音乐机器人 🎵

一个功能强大的Telegram音乐机器人，支持从YouTube和Spotify搜索并下载音乐。使用Python开发，适合部署在VPS上24/7运行。

## ✨ 主要功能

- 🔍 **多平台搜索** - 同时支持YouTube和Spotify搜索
- ⏬ **高质量下载** - 自动下载MP3格式音频（192kbps）
- 🎯 **智能匹配** - Spotify歌曲自动在YouTube下载
- 💾 **历史记录** - 保存所有下载历史
- ⚙️ **个性化设置** - 用户偏好设置
- 🎨 **交互界面** - 美观的按钮式交互
- 📊 **数据库存储** - SQLite存储用户信息和历史

## 🚀 快速开始

### 方式一：直接部署（推荐）

1. **克隆仓库**
   ```bash
   git clone <your-repo-url>
   cd tg-music-bot-py
   ```

2. **运行部署脚本**
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

3. **配置环境变量**

   编辑 `.env` 文件：
   ```bash
   nano .env
   ```

   填入必要的配置：
   ```env
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   SPOTIFY_CLIENT_ID=your_spotify_id  # 可选
   SPOTIFY_CLIENT_SECRET=your_spotify_secret  # 可选
   ```

4. **启动机器人**
   ```bash
   source venv/bin/activate
   python bot.py
   ```

### 方式二：使用Docker

1. **构建并运行**
   ```bash
   # 编辑 .env 文件
   cp .env.example .env
   nano .env

   # 使用Docker Compose启动
   docker-compose up -d
   ```

2. **查看日志**
   ```bash
   docker-compose logs -f
   ```

### 方式三：Systemd服务（后台运行）

1. **完成基础部署**
   ```bash
   ./deploy.sh
   ```

2. **配置systemd服务**
   ```bash
   chmod +x deploy_systemd.sh
   ./deploy_systemd.sh
   ```

3. **管理服务**
   ```bash
   sudo systemctl start telegram-music-bot    # 启动
   sudo systemctl stop telegram-music-bot     # 停止
   sudo systemctl restart telegram-music-bot  # 重启
   sudo systemctl status telegram-music-bot   # 状态
   sudo systemctl enable telegram-music-bot   # 开机自启
   ```

## 📋 系统要求

### VPS配置建议
- **操作系统**: Ubuntu 20.04+ / Debian 10+
- **内存**: 最低512MB，推荐1GB+
- **存储**: 10GB+（用于临时下载）
- **Python**: 3.10+
- **带宽**: 不限流量，速度越快越好

### 必需软件
- Python 3.10+
- FFmpeg
- pip

## 🔧 配置说明

### 获取Telegram Bot Token

1. 在Telegram搜索 [@BotFather](https://t.me/BotFather)
2. 发送 `/newbot` 命令
3. 按提示设置机器人名称和用户名
4. 复制获得的token到 `.env` 文件

### 获取Spotify API密钥（可选）

1. 访问 [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. 登录并创建新应用
3. 获取 Client ID 和 Client Secret
4. 填入 `.env` 文件

**注意**: Spotify是可选的，不配置也能正常使用YouTube搜索。

### 环境变量说明

| 变量名 | 说明 | 默认值 | 必填 |
|--------|------|--------|------|
| `TELEGRAM_BOT_TOKEN` | Telegram机器人Token | - | ✅ |
| `SPOTIFY_CLIENT_ID` | Spotify客户端ID | - | ❌ |
| `SPOTIFY_CLIENT_SECRET` | Spotify客户端密钥 | - | ❌ |
| `DOWNLOAD_PATH` | 临时下载目录 | `./downloads` | ❌ |
| `MAX_FILE_SIZE_MB` | 最大文件大小(MB) | `50` | ❌ |
| `MAX_SONG_DURATION` | 最大歌曲时长(秒) | `600` | ❌ |
| `DATABASE_URL` | 数据库连接URL | `sqlite+aiosqlite:///./music_bot.db` | ❌ |
| `LOG_LEVEL` | 日志级别 | `INFO` | ❌ |

## 📱 使用指南

### 基础命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `/start` | 开始使用机器人 | `/start` |
| `/help` | 查看帮助信息 | `/help` |
| `/search` | 搜索音乐（YouTube+Spotify） | `/search 周杰伦 晴天` |
| `/youtube` | 仅在YouTube搜索 | `/youtube Taylor Swift` |
| `/spotify` | 仅在Spotify搜索 | `/spotify The Weeknd` |
| `/history` | 查看下载历史 | `/history` |
| `/settings` | 个人设置 | `/settings` |

### 快捷搜索

直接发送歌曲名即可搜索，无需输入命令：
```
周杰伦 晴天
Taylor Swift - Anti Hero
```

### 使用流程

1. 📝 **发送搜索** - 输入歌曲名或使用 `/search` 命令
2. 📋 **选择歌曲** - 从搜索结果中点击想要的歌曲按钮
3. ⏬ **等待下载** - 机器人自动下载并转换为MP3
4. 🎵 **接收音乐** - 收到音频文件，可直接播放

## 📁 项目结构

```
tg-music-bot-py/
├── bot.py                    # 主程序入口
├── config.py                 # 配置管理
├── database.py               # 数据库模型
├── youtube_downloader.py     # YouTube下载器
├── spotify_searcher.py       # Spotify搜索器
├── requirements.txt          # Python依赖
├── .env.example              # 环境变量示例
├── .gitignore               # Git忽略文件
├── deploy.sh                # 部署脚本
├── deploy_systemd.sh        # Systemd服务配置
├── docker-compose.yml       # Docker配置
├── Dockerfile               # Docker镜像
├── README.md                # 说明文档
├── downloads/               # 临时下载目录
├── logs/                    # 日志目录
└── music_bot.db            # SQLite数据库
```

## 🛠️ 技术栈

### 核心库
- **python-telegram-bot** - Telegram Bot API
- **yt-dlp** - YouTube视频/音频下载
- **spotipy** - Spotify API客户端
- **SQLAlchemy** - 异步ORM
- **aiosqlite** - 异步SQLite驱动

### 工具库
- **loguru** - 日志管理
- **python-dotenv** - 环境变量管理
- **aiohttp** - 异步HTTP客户端
- **pydub** - 音频处理

## 🔒 安全说明

### 权限管理
- 建议为机器人创建专用的Linux用户
- 使用环境变量存储敏感信息
- 不要将 `.env` 文件提交到Git

### 防火墙配置
机器人只需要出站连接，无需开放入站端口。

### 资源限制
建议在systemd服务中添加资源限制：
```ini
[Service]
MemoryMax=1G
CPUQuota=50%
```

## 📊 监控和维护

### 查看日志
```bash
# Systemd服务日志
sudo journalctl -u telegram-music-bot -f

# 应用日志
tail -f logs/bot.log

# Docker日志
docker-compose logs -f
```

### 清理临时文件
```bash
# 清理下载目录
rm -rf downloads/*

# 清理旧日志
find logs/ -name "*.log.*" -mtime +7 -delete
```

### 数据库备份
```bash
# 备份数据库
cp music_bot.db music_bot.db.backup

# 定时备份（添加到crontab）
0 2 * * * cp /path/to/music_bot.db /path/to/backups/music_bot.db.$(date +\%Y\%m\%d)
```

## ⚠️ 常见问题

### 1. 安装依赖失败

**问题**: pip安装某些包失败

**解决**:
```bash
# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或更新pip
pip install --upgrade pip
```

### 2. FFmpeg未安装

**问题**: 下载音频时报错

**解决**:
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# CentOS/RHEL
sudo yum install ffmpeg
```

### 3. YouTube下载失败

**问题**: YouTube下载频繁失败

**解决**:
- 更新yt-dlp: `pip install --upgrade yt-dlp`
- 检查网络连接
- 某些地区可能需要VPN

### 4. Spotify搜索无结果

**问题**: Spotify API返回空结果

**解决**:
- 检查API密钥是否正确
- 确认Spotify应用已激活
- 查看日志了解具体错误

### 5. 机器人无响应

**问题**: 发送消息无反应

**解决**:
```bash
# 检查服务状态
sudo systemctl status telegram-music-bot

# 查看日志
tail -f logs/bot.log

# 检查网络连接
ping api.telegram.org
```

### 6. 数据库锁定

**问题**: SQLite数据库锁定错误

**解决**:
- 确保只有一个实例在运行
- 重启服务
- 如果问题持续，考虑使用PostgreSQL

## 🚧 开发计划

- [ ] 支持播放列表批量下载
- [ ] 添加音质选择功能
- [ ] 支持更多音乐平台（SoundCloud、Apple Music）
- [ ] 歌词显示功能
- [ ] 用户收藏夹
- [ ] 管理员后台
- [ ] 使用统计和分析
- [ ] 多语言支持

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m '添加某个功能'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📄 许可证

本项目使用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## ⚖️ 免责声明

- 本项目仅供学习和个人使用
- 请遵守当地法律法规和版权规定
- 不要用于商业用途或侵犯版权
- 下载的音乐仅供个人欣赏，请支持正版
- 开发者不对任何滥用行为负责

## 📮 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 [Issue](https://github.com/your-repo/issues)
- 发送邮件到: your-email@example.com

## 🙏 致谢

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - 优秀的Telegram Bot框架
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - 强大的视频下载工具
- [spotipy](https://github.com/plamere/spotipy) - Spotify API封装库

---

⭐ 如果觉得这个项目有用，请给个Star支持一下！
