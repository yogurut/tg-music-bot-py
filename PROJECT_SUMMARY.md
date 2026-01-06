# 🎵 Telegram音乐机器人 - 项目总结

## 📦 项目文件清单

### 核心代码文件
- `bot.py` - 主程序入口，包含所有Bot逻辑
- `config.py` - 配置管理模块
- `database.py` - 数据库模型和ORM
- `youtube_downloader.py` - YouTube音乐下载器
- `spotify_searcher.py` - Spotify音乐搜索器

### 配置文件
- `requirements.txt` - Python依赖包列表
- `.env.example` - 环境变量配置示例
- `.gitignore` - Git忽略文件配置

### 部署文件
- `deploy.sh` - VPS一键部署脚本
- `deploy_systemd.sh` - Systemd服务配置脚本
- `start.sh` - Linux快速启动脚本
- `start_windows.sh` - Windows快速启动脚本
- `Dockerfile` - Docker镜像配置
- `docker-compose.yml` - Docker Compose配置

### 文档文件
- `README.md` - 项目主文档
- `VPS_DEPLOY_GUIDE.md` - VPS部署详细指南

## 🎯 功能特性

### ✅ 已实现功能

1. **多平台搜索**
   - YouTube音乐搜索
   - Spotify音乐搜索
   - 混合搜索结果

2. **音乐下载**
   - 高质量MP3下载（192kbps）
   - 自动格式转换
   - 文件大小限制（50MB）
   - 时长限制（10分钟）

3. **用户交互**
   - 命令式操作（/search, /youtube, /spotify）
   - 直接文本搜索
   - 交互式按钮选择
   - 美观的搜索结果展示

4. **数据管理**
   - SQLite数据库存储
   - 用户信息记录
   - 下载历史追踪
   - 用户偏好设置

5. **部署支持**
   - 直接部署
   - Docker部署
   - Systemd服务
   - 后台运行

## 🏗️ 技术架构

### 系统架构
```
用户 <---> Telegram API <---> Bot程序
                                 |
                    +------------+------------+
                    |            |            |
                YouTube API   Spotify API   Database
                    |            |            |
                 yt-dlp      spotipy      SQLAlchemy
```

### 数据流程
```
1. 用户发送搜索请求
   ↓
2. Bot解析命令/文本
   ↓
3. 调用搜索API（YouTube/Spotify）
   ↓
4. 返回搜索结果 + 交互按钮
   ↓
5. 用户点击选择
   ↓
6. 下载音频文件
   ↓
7. 发送给用户 + 保存历史
   ↓
8. 清理临时文件
```

### 核心依赖

| 库名 | 版本 | 用途 |
|------|------|------|
| python-telegram-bot | 20.7 | Telegram Bot API |
| yt-dlp | latest | YouTube下载 |
| spotipy | 2.23.0 | Spotify API |
| sqlalchemy | 2.0.23 | 数据库ORM |
| loguru | 0.7.2 | 日志管理 |
| aiohttp | 3.9.1 | 异步HTTP |

## 📊 数据库设计

### 表结构

#### users（用户表）
- id (主键)
- user_id (Telegram用户ID)
- username
- first_name
- last_name
- language_code
- is_active
- created_at
- last_active

#### download_history（下载历史表）
- id (主键)
- user_id (外键)
- song_title
- artist
- source (youtube/spotify)
- source_url
- duration
- file_size
- downloaded_at

#### user_preferences（用户偏好表）
- id (主键)
- user_id (外键)
- preferred_source
- preferred_quality
- auto_download
- created_at
- updated_at

## 🚀 快速开始

### 本地测试（Windows）

```bash
# 1. 克隆项目
cd f:\code\tg-music-bot-py

# 2. 创建虚拟环境
python -m venv venv
source venv/Scripts/activate  # Git Bash

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入 TELEGRAM_BOT_TOKEN

# 5. 启动机器人
python bot.py
```

### VPS部署

```bash
# 1. 连接VPS
ssh user@your_vps_ip

# 2. 克隆项目
git clone <repo-url>
cd tg-music-bot-py

# 3. 一键部署
chmod +x deploy.sh
./deploy.sh

# 4. 配置systemd服务
chmod +x deploy_systemd.sh
./deploy_systemd.sh
```

### Docker部署

```bash
# 1. 配置环境变量
cp .env.example .env
nano .env

# 2. 启动容器
docker-compose up -d

# 3. 查看日志
docker-compose logs -f
```

## 🎮 使用示例

### 基础搜索
```
用户: 周杰伦 晴天
Bot: 🔍 正在YouTube和Spotify搜索...
     [显示5个搜索结果，每个带按钮]
用户: [点击第一个按钮]
Bot: ⏬ 正在下载...
     [发送MP3文件]
Bot: ✅ 下载完成！
```

### 指定平台
```
用户: /youtube Taylor Swift
Bot: 🔍 正在YouTube搜索...
     [仅显示YouTube结果]
```

### 查看历史
```
用户: /history
Bot: 📜 最近下载的歌曲：
     1. 周杰伦 - 晴天
        📅 2024-01-15 10:30
     2. ...
```

## ⚙️ 配置说明

### 必需配置
```env
TELEGRAM_BOT_TOKEN=your_token_here  # 从 @BotFather 获取
```

### 可选配置
```env
# Spotify（提升搜索质量）
SPOTIFY_CLIENT_ID=your_id
SPOTIFY_CLIENT_SECRET=your_secret

# 下载限制
MAX_FILE_SIZE_MB=50
MAX_SONG_DURATION=600

# 日志
LOG_LEVEL=INFO
```

## 🔒 安全考虑

1. **环境变量**: 敏感信息存储在.env文件
2. **权限控制**: 文件权限设置为600
3. **专用用户**: 使用非root用户运行
4. **防火墙**: 仅允许必要端口
5. **日志审计**: 记录所有操作

## 📈 性能优化

### 已实现
- 异步IO操作
- 搜索结果缓存
- 临时文件自动清理
- 数据库连接池

### 可优化
- 使用Redis缓存
- 多进程下载
- CDN加速
- PostgreSQL替代SQLite

## 🐛 已知问题

1. **YouTube地区限制**: 某些地区可能无法访问YouTube
   - 解决：使用VPN或代理

2. **文件大小限制**: Telegram限制50MB
   - 解决：已在下载前检查

3. **并发限制**: 大量用户同时下载可能导致性能下降
   - 解决：添加队列系统（待实现）

## 🚧 未来计划

### 短期（1-2周）
- [ ] 添加播放列表支持
- [ ] 音质选择功能
- [ ] 用户收藏夹

### 中期（1个月）
- [ ] 支持更多平台（SoundCloud、Apple Music）
- [ ] 歌词显示
- [ ] 管理员后台

### 长期（3个月+）
- [ ] 使用统计和分析
- [ ] 多语言支持
- [ ] Web控制面板
- [ ] 付费功能（去广告、更高质量）

## 📝 开发笔记

### 遇到的挑战

1. **异步编程**: python-telegram-bot v20使用异步
   - 解决：学习async/await模式

2. **yt-dlp集成**: 需要在异步环境中使用同步库
   - 解决：使用run_in_executor

3. **Spotify下载**: Spotify只提供元数据
   - 解决：在YouTube搜索Spotify歌曲

4. **文件管理**: 临时文件需要及时清理
   - 解决：下载完成后立即删除

### 最佳实践

1. **日志记录**: 使用loguru详细记录
2. **错误处理**: 所有API调用都包含异常处理
3. **用户体验**: 及时反馈操作状态
4. **代码组织**: 模块化设计，职责分离

## 📄 许可证

MIT License - 可自由使用、修改和分发

## 🙏 致谢

感谢以下开源项目：
- python-telegram-bot
- yt-dlp
- spotipy
- SQLAlchemy

## 📮 联系方式

- GitHub Issues: 报告问题和建议
- Email: your-email@example.com

---

**项目状态**: ✅ 已完成基础功能，可部署使用

**最后更新**: 2024-01-15

**作者**: Claude Code

**版本**: v1.0.0
