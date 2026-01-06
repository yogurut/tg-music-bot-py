# VPS部署完整指南 📝

本指南详细说明如何在VPS上从零开始部署Telegram音乐机器人。

## 📋 准备工作

### 1. VPS要求

推荐配置：
- **CPU**: 1核心+
- **内存**: 1GB+
- **存储**: 10GB+
- **系统**: Ubuntu 20.04 / 22.04 LTS
- **网络**: 不限流量

### 2. 必需账号

- Telegram账号（用于创建机器人）
- （可选）Spotify开发者账号
- VPS SSH访问权限

## 🚀 部署步骤

### 第一步：连接到VPS

使用SSH连接到你的VPS：

```bash
ssh root@your_vps_ip
# 或
ssh your_username@your_vps_ip
```

### 第二步：创建专用用户（推荐）

为安全起见，创建专用用户运行机器人：

```bash
# 创建用户
sudo adduser musicbot

# 添加sudo权限
sudo usermod -aG sudo musicbot

# 切换到新用户
su - musicbot
```

### 第三步：安装基础软件

```bash
# 更新系统
sudo apt update
sudo apt upgrade -y

# 安装必需软件
sudo apt install -y git python3 python3-pip python3-venv ffmpeg

# 验证安装
python3 --version  # 应该是 3.10+
ffmpeg -version
```

### 第四步：下载项目

```bash
# 创建工作目录
mkdir -p ~/projects
cd ~/projects

# 克隆仓库（替换为你的仓库地址）
git clone https://github.com/your-username/tg-music-bot-py.git
cd tg-music-bot-py

# 或者使用wget下载压缩包
# wget https://github.com/your-username/tg-music-bot-py/archive/main.zip
# unzip main.zip
# cd tg-music-bot-py-main
```

### 第五步：配置环境

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 升级pip
pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt
```

### 第六步：配置机器人

#### 6.1 获取Telegram Bot Token

1. 在Telegram中搜索 `@BotFather`
2. 发送 `/newbot` 命令
3. 设置机器人名称（例如: My Music Bot）
4. 设置用户名（必须以bot结尾，例如: my_music_bot）
5. 复制获得的Token

#### 6.2 （可选）获取Spotify API密钥

1. 访问 https://developer.spotify.com/dashboard
2. 登录Spotify账号
3. 点击 "Create an App"
4. 填写应用信息
5. 获取 Client ID 和 Client Secret

#### 6.3 配置环境变量

```bash
# 复制配置文件
cp .env.example .env

# 编辑配置
nano .env
```

填入以下内容：

```env
# 必填 - Telegram Bot Token
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz

# 可选 - Spotify配置（不填也能用YouTube搜索）
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret

# 可选 - 其他配置
DOWNLOAD_PATH=./downloads
MAX_FILE_SIZE_MB=50
MAX_SONG_DURATION=600
LOG_LEVEL=INFO
```

保存并退出（Ctrl+X，然后按Y，回车）

### 第七步：测试运行

```bash
# 确保虚拟环境已激活
source venv/bin/activate

# 运行机器人
python bot.py
```

如果看到 `✅ 机器人已启动，正在监听消息...` 说明启动成功！

在Telegram中找到你的机器人，发送 `/start` 测试。

按 Ctrl+C 停止机器人。

### 第八步：配置后台运行

#### 方法A：使用systemd（推荐）

```bash
# 运行systemd配置脚本
chmod +x deploy_systemd.sh
./deploy_systemd.sh

# 启动服务
sudo systemctl start telegram-music-bot

# 设置开机自启
sudo systemctl enable telegram-music-bot

# 查看状态
sudo systemctl status telegram-music-bot
```

#### 方法B：使用screen

```bash
# 安装screen
sudo apt install screen

# 创建新会话
screen -S musicbot

# 激活虚拟环境并运行
source venv/bin/activate
python bot.py

# 分离会话：按 Ctrl+A，然后按 D
# 重新连接：screen -r musicbot
```

#### 方法C：使用tmux

```bash
# 安装tmux
sudo apt install tmux

# 创建新会话
tmux new -s musicbot

# 激活虚拟环境并运行
source venv/bin/activate
python bot.py

# 分离会话：按 Ctrl+B，然后按 D
# 重新连接：tmux attach -t musicbot
```

## 🔧 日常维护

### 查看日志

```bash
# 查看应用日志
tail -f ~/projects/tg-music-bot-py/logs/bot.log

# 查看systemd日志
sudo journalctl -u telegram-music-bot -f

# 查看最近100行日志
sudo journalctl -u telegram-music-bot -n 100
```

### 重启服务

```bash
sudo systemctl restart telegram-music-bot
```

### 更新代码

```bash
cd ~/projects/tg-music-bot-py

# 停止服务
sudo systemctl stop telegram-music-bot

# 拉取最新代码
git pull

# 更新依赖
source venv/bin/activate
pip install -r requirements.txt --upgrade

# 重启服务
sudo systemctl start telegram-music-bot
```

### 清理临时文件

```bash
# 清理下载目录
cd ~/projects/tg-music-bot-py
rm -rf downloads/*

# 添加定时清理（每天凌晨2点）
crontab -e
# 添加这行：
0 2 * * * rm -rf /home/musicbot/projects/tg-music-bot-py/downloads/*
```

### 备份数据库

```bash
# 手动备份
cp music_bot.db music_bot.db.backup

# 自动备份脚本
mkdir -p ~/backups

# 创建备份脚本
cat > ~/backup_db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR=~/backups
DB_PATH=~/projects/tg-music-bot-py/music_bot.db
DATE=$(date +%Y%m%d_%H%M%S)

cp $DB_PATH $BACKUP_DIR/music_bot_$DATE.db

# 只保留最近7天的备份
find $BACKUP_DIR -name "music_bot_*.db" -mtime +7 -delete
EOF

chmod +x ~/backup_db.sh

# 添加到crontab（每天凌晨3点备份）
crontab -e
# 添加这行：
0 3 * * * /home/musicbot/backup_db.sh
```

## 🛡️ 安全加固

### 1. 配置防火墙

```bash
# 安装UFW
sudo apt install ufw

# 允许SSH
sudo ufw allow 22/tcp

# 启用防火墙
sudo ufw enable

# 查看状态
sudo ufw status
```

### 2. 保护敏感文件

```bash
cd ~/projects/tg-music-bot-py

# 设置.env文件权限
chmod 600 .env

# 设置数据库文件权限
chmod 600 music_bot.db
```

### 3. 定期更新系统

```bash
# 创建更新脚本
cat > ~/update_system.sh << 'EOF'
#!/bin/bash
sudo apt update
sudo apt upgrade -y
sudo apt autoremove -y
EOF

chmod +x ~/update_system.sh

# 每周日凌晨4点更新
crontab -e
# 添加：
0 4 * * 0 /home/musicbot/update_system.sh
```

## 📊 监控

### 1. 资源使用监控

```bash
# 查看CPU和内存使用
htop

# 查看磁盘使用
df -h

# 查看进程
ps aux | grep python
```

### 2. 服务监控

```bash
# 创建监控脚本
cat > ~/monitor_bot.sh << 'EOF'
#!/bin/bash

# 检查服务是否运行
if ! systemctl is-active --quiet telegram-music-bot; then
    echo "Bot is down! Restarting..."
    systemctl start telegram-music-bot

    # 发送通知（需要配置）
    # curl -X POST "https://api.telegram.org/bot<YOUR_TOKEN>/sendMessage" \
    #      -d "chat_id=<YOUR_CHAT_ID>&text=Bot was down and has been restarted"
fi
EOF

chmod +x ~/monitor_bot.sh

# 每5分钟检查一次
crontab -e
# 添加：
*/5 * * * * /home/musicbot/monitor_bot.sh
```

## ❓ 故障排查

### 问题1：机器人无法启动

```bash
# 检查日志
sudo journalctl -u telegram-music-bot -n 50

# 检查配置
cat .env

# 手动运行查看详细错误
cd ~/projects/tg-music-bot-py
source venv/bin/activate
python bot.py
```

### 问题2：下载失败

```bash
# 测试FFmpeg
ffmpeg -version

# 测试网络
curl -I https://www.youtube.com

# 更新yt-dlp
source venv/bin/activate
pip install --upgrade yt-dlp
```

### 问题3：磁盘空间不足

```bash
# 查看磁盘使用
df -h

# 清理下载目录
rm -rf ~/projects/tg-music-bot-py/downloads/*

# 清理日志
cd ~/projects/tg-music-bot-py/logs
rm *.log.*
```

## 🔄 升级和迁移

### 升级Python版本

```bash
# 安装新版本Python
sudo apt install python3.11

# 重新创建虚拟环境
cd ~/projects/tg-music-bot-py
rm -rf venv
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 迁移到新VPS

```bash
# 在旧VPS上备份
cd ~/projects/tg-music-bot-py
tar -czf musicbot-backup.tar.gz .env music_bot.db

# 复制到新VPS
scp musicbot-backup.tar.gz user@new_vps_ip:~/

# 在新VPS上：
# 1. 完成基础部署（第一步到第五步）
# 2. 解压备份
tar -xzf ~/musicbot-backup.tar.gz -C ~/projects/tg-music-bot-py/
# 3. 重启服务
```

## 💡 性能优化

### 1. 使用更快的pip镜像

```bash
# 创建pip配置
mkdir -p ~/.pip
cat > ~/.pip/pip.conf << EOF
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
EOF
```

### 2. 限制并发下载

在 `config.py` 中添加：
```python
MAX_CONCURRENT_DOWNLOADS = 3
```

### 3. 定期清理

```bash
# 添加到crontab
0 */6 * * * rm -rf /home/musicbot/projects/tg-music-bot-py/downloads/*
```

## 📞 获取帮助

如果遇到问题：

1. 查看日志文件
2. 检查GitHub Issues
3. 阅读完整README
4. 提交新Issue并附上：
   - 错误日志
   - 系统信息
   - 复现步骤

---

部署成功后，你的音乐机器人将7x24小时运行在VPS上！🎉
