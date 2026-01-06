#!/bin/bash

# Systemd服务配置脚本 - 让机器人在后台持续运行

set -e

# 获取当前目录和用户
CURRENT_DIR=$(pwd)
CURRENT_USER=$(whoami)

echo "🔧 配置Systemd服务..."

# 创建systemd服务文件
sudo tee /etc/systemd/system/telegram-music-bot.service > /dev/null <<EOF
[Unit]
Description=Telegram Music Bot
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$CURRENT_DIR
Environment="PATH=$CURRENT_DIR/venv/bin"
ExecStart=$CURRENT_DIR/venv/bin/python $CURRENT_DIR/bot.py
Restart=always
RestartSec=10

# 日志配置
StandardOutput=append:/var/log/telegram-music-bot/output.log
StandardError=append:/var/log/telegram-music-bot/error.log

[Install]
WantedBy=multi-user.target
EOF

# 创建日志目录
sudo mkdir -p /var/log/telegram-music-bot
sudo chown $CURRENT_USER:$CURRENT_USER /var/log/telegram-music-bot

# 重新加载systemd
sudo systemctl daemon-reload

echo "✅ Systemd服务配置完成！"
echo ""
echo "使用以下命令管理服务："
echo "  启动服务: sudo systemctl start telegram-music-bot"
echo "  停止服务: sudo systemctl stop telegram-music-bot"
echo "  重启服务: sudo systemctl restart telegram-music-bot"
echo "  查看状态: sudo systemctl status telegram-music-bot"
echo "  开机自启: sudo systemctl enable telegram-music-bot"
echo "  查看日志: sudo journalctl -u telegram-music-bot -f"
echo ""

# 询问是否立即启动
read -p "是否现在启动服务？(y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo systemctl start telegram-music-bot
    sudo systemctl enable telegram-music-bot
    echo "✅ 服务已启动并设置为开机自启"
    echo ""
    sudo systemctl status telegram-music-bot
fi
