"""
Telegram音乐机器人主程序
支持YouTube和Spotify音乐搜索下载
"""
import os
import asyncio
from pathlib import Path
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from telegram.constants import ParseMode
from loguru import logger
from sqlalchemy import select

import config
from database import init_db, close_db, AsyncSessionLocal, User, DownloadHistory, UserPreference
from youtube_downloader import youtube_downloader
from spotify_searcher import spotify_searcher


# 配置日志
logger.add(
    config.LOG_FILE,
    rotation="10 MB",
    retention="7 days",
    level=config.LOG_LEVEL,
    encoding="utf-8"
)


class MusicBot:
    """音乐机器人类"""

    def __init__(self):
        self.app = None
        self.search_cache = {}  # 用户搜索结果缓存 {chat_id: results}

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理/start命令"""
        user = update.effective_user
        chat_id = update.effective_chat.id

        # 保存用户信息到数据库
        await self.save_user(user)

        welcome_text = f"""
👋 欢迎使用音乐机器人，{user.first_name}！

🎵 我可以帮你从YouTube和Spotify搜索并下载音乐

📝 使用方法：
/search <歌曲名> - 搜索音乐
/youtube <歌曲名> - 仅在YouTube搜索
/spotify <歌曲名> - 仅在Spotify搜索
/settings - 查看和修改设置
/history - 查看下载历史
/help - 查看帮助

💡 快速开始：
直接发送歌曲名即可搜索！
例如: 周杰伦 晴天
        """

        await update.message.reply_text(welcome_text)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理/help命令"""
        help_text = """
🎵 音乐机器人完整指南

📌 基础命令：
/start - 开始使用机器人
/help - 查看此帮助信息

🔍 搜索命令：
/search <歌曲名> - 智能搜索（YouTube + Spotify）
/youtube <歌曲名> - 仅在YouTube搜索
/spotify <歌曲名> - 仅在Spotify搜索

⚙️ 设置命令：
/settings - 查看和修改个人设置
/history - 查看下载历史

🎯 使用技巧：
1. 直接发送歌曲名称即可搜索
2. 可以同时搜索歌手和歌名，如: "周杰伦 晴天"
3. Spotify搜索会自动在YouTube下载音频
4. 下载的音频为MP3格式，音质192kbps

⚠️ 限制说明：
• 单个文件最大 50MB
• 歌曲时长最长 10分钟
• 每次搜索最多显示 5个结果

💡 提示：
- 使用 /settings 可以设置默认搜索源
- 所有下载记录都会保存在历史中
        """

        await update.message.reply_text(help_text)

    async def search_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理/search命令 - 同时搜索YouTube和Spotify"""
        await self._handle_search(update, context, source='both')

    async def youtube_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理/youtube命令 - 仅搜索YouTube"""
        await self._handle_search(update, context, source='youtube')

    async def spotify_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理/spotify命令 - 仅搜索Spotify"""
        await self._handle_search(update, context, source='spotify')

    async def _handle_search(self, update: Update, context: ContextTypes.DEFAULT_TYPE, source: str = 'both'):
        """
        统一的搜索处理方法

        Args:
            source: 'youtube', 'spotify', 或 'both'
        """
        # 获取搜索关键词
        if context.args:
            query = ' '.join(context.args)
        else:
            await update.message.reply_text(
                "❌ 请输入要搜索的歌曲名称\n"
                f"例如: /{update.message.text.split()[0].replace('/', '')} 周杰伦 晴天"
            )
            return

        chat_id = update.effective_chat.id
        user = update.effective_user

        # 显示搜索提示
        source_text = {
            'youtube': 'YouTube',
            'spotify': 'Spotify',
            'both': 'YouTube和Spotify'
        }.get(source, '多个平台')

        msg = await update.message.reply_text(f"🔍 正在{source_text}搜索: {query}...")

        try:
            results = []

            # YouTube搜索
            if source in ['youtube', 'both']:
                yt_results = await youtube_downloader.search(query, limit=5)
                results.extend(yt_results)

            # Spotify搜索
            if source in ['spotify', 'both'] and spotify_searcher.enabled:
                sp_results = await spotify_searcher.search(query, limit=5)
                results.extend(sp_results)

            if not results:
                await msg.edit_text("❌ 没有找到相关歌曲，请换个关键词试试")
                return

            # 保存搜索结果到缓存
            self.search_cache[chat_id] = results

            # 构建结果消息和按钮
            await self.send_search_results(update, results, msg)

        except Exception as e:
            logger.error(f"搜索失败: {e}")
            await msg.edit_text("❌ 搜索时出错，请稍后再试")

    async def send_search_results(self, update: Update, results: list, msg):
        """发送搜索结果"""
        result_text = "🎵 搜索结果：\n\n"

        keyboard = []
        for idx, track in enumerate(results[:10]):  # 最多显示10个结果
            # 格式化时长
            duration = track.get('duration', 0)
            duration_str = f"{duration // 60}:{duration % 60:02d}"

            # 来源标识
            source_emoji = "🎬" if track['source'] == 'youtube' else "🎧"

            # 构建结果文本
            result_text += f"{idx + 1}. {source_emoji} {track['title']}\n"
            result_text += f"   👤 {track['artist']} | ⏱️ {duration_str}\n"

            if track['source'] == 'youtube' and 'views' in track:
                views = track.get('views', 0)
                result_text += f"   👁️ {views:,} 次观看\n"
            elif track['source'] == 'spotify' and 'popularity' in track:
                popularity = track.get('popularity', 0)
                result_text += f"   🔥 热度: {popularity}/100\n"

            result_text += "\n"

            # 创建按钮
            button_text = f"{idx + 1}. {track['title'][:25]}..."
            keyboard.append([InlineKeyboardButton(
                button_text,
                callback_data=f"download_{idx}"
            )])

        # 添加翻页按钮（如果结果很多）
        if len(results) > 10:
            keyboard.append([
                InlineKeyboardButton("◀️ 上一页", callback_data="page_prev"),
                InlineKeyboardButton("下一页 ▶️", callback_data="page_next")
            ])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await msg.edit_text(result_text, reply_markup=reply_markup)

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理按钮回调"""
        query = update.callback_query
        await query.answer()

        chat_id = query.message.chat.id
        user = query.from_user
        data = query.data

        # 处理下载按钮
        if data.startswith('download_'):
            idx = int(data.split('_')[1])
            results = self.search_cache.get(chat_id, [])

            if not results or idx >= len(results):
                await query.answer("❌ 搜索结果已过期，请重新搜索", show_alert=True)
                return

            track = results[idx]

            # 显示下载提示
            await query.edit_message_text(
                f"⏬ 正在下载: {track['title']}\n"
                f"👤 {track['artist']}\n\n"
                f"⏳ 请稍候..."
            )

            try:
                # 下载音乐
                file_path = await self.download_music(track, user.id)

                if file_path:
                    # 发送音频文件
                    await self.send_audio_file(query, track, file_path, user.id)

                    # 保存下载历史
                    await self.save_download_history(user.id, track, file_path)

                    await query.message.reply_text("✅ 下载完成！")
                else:
                    await query.message.reply_text("❌ 下载失败，请稍后重试")

            except Exception as e:
                logger.error(f"下载失败: {e}")
                await query.message.reply_text(f"❌ 下载失败: {str(e)}")

    async def download_music(self, track: dict, user_id: int) -> Path:
        """
        下载音乐

        Args:
            track: 歌曲信息
            user_id: 用户ID

        Returns:
            下载的文件路径
        """
        if track['source'] == 'youtube':
            # YouTube直接下载
            return await youtube_downloader.download(track['url'], user_id)
        elif track['source'] == 'spotify':
            # Spotify需要先在YouTube搜索
            youtube_query = track.get('youtube_query', f"{track['artist']} {track['title']}")
            yt_results = await youtube_downloader.search(youtube_query, limit=1)

            if yt_results:
                return await youtube_downloader.download(yt_results[0]['url'], user_id)

        return None

    async def send_audio_file(self, query, track: dict, file_path: Path, user_id: int):
        """发送音频文件"""
        try:
            with open(file_path, 'rb') as audio_file:
                await query.message.reply_audio(
                    audio=audio_file,
                    title=track['title'],
                    performer=track['artist'],
                    duration=track.get('duration'),
                    thumbnail=None  # 可以添加缩略图
                )

            # 删除临时文件
            file_path.unlink(missing_ok=True)

        except Exception as e:
            logger.error(f"发送音频文件失败: {e}")
            raise

    async def text_message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理普通文本消息 - 直接作为搜索"""
        query_text = update.message.text

        # 模拟search命令
        context.args = query_text.split()
        await self._handle_search(update, context, source='both')

    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理/settings命令"""
        user = update.effective_user

        settings_text = """
⚙️ 个人设置

当前设置：
• 默认搜索源: YouTube + Spotify
• 音频质量: 高质量 (192kbps)
• 自动下载: 关闭

🔧 可用设置（开发中）：
- 修改默认搜索源
- 调整音频质量
- 启用自动下载第一个结果
        """

        await update.message.reply_text(settings_text)

    async def history_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理/history命令 - 显示下载历史"""
        user_id = update.effective_user.id

        try:
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    select(DownloadHistory)
                    .where(DownloadHistory.user_id == user_id)
                    .order_by(DownloadHistory.downloaded_at.desc())
                    .limit(10)
                )
                history = result.scalars().all()

                if not history:
                    await update.message.reply_text("📭 你还没有下载过任何歌曲")
                    return

                history_text = "📜 最近下载的歌曲：\n\n"
                for idx, record in enumerate(history, 1):
                    history_text += f"{idx}. {record.song_title}\n"
                    history_text += f"   👤 {record.artist}\n"
                    history_text += f"   📅 {record.downloaded_at.strftime('%Y-%m-%d %H:%M')}\n\n"

                await update.message.reply_text(history_text)

        except Exception as e:
            logger.error(f"获取历史记录失败: {e}")
            await update.message.reply_text("❌ 获取历史记录失败")

    async def save_user(self, user):
        """保存用户信息到数据库"""
        try:
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    select(User).where(User.user_id == user.id)
                )
                db_user = result.scalar_one_or_none()

                if db_user:
                    # 更新最后活跃时间
                    db_user.last_active = datetime.utcnow()
                else:
                    # 创建新用户
                    db_user = User(
                        user_id=user.id,
                        username=user.username,
                        first_name=user.first_name,
                        last_name=user.last_name,
                        language_code=user.language_code
                    )
                    session.add(db_user)

                await session.commit()

        except Exception as e:
            logger.error(f"保存用户失败: {e}")

    async def save_download_history(self, user_id: int, track: dict, file_path: Path):
        """保存下载历史"""
        try:
            async with AsyncSessionLocal() as session:
                history = DownloadHistory(
                    user_id=user_id,
                    song_title=track['title'],
                    artist=track['artist'],
                    source=track['source'],
                    source_url=track.get('url') or track.get('spotify_url'),
                    duration=track.get('duration'),
                    file_size=file_path.stat().st_size if file_path.exists() else None
                )
                session.add(history)
                await session.commit()

        except Exception as e:
            logger.error(f"保存下载历史失败: {e}")

    async def post_init(self, application: Application):
        """应用初始化后的钩子"""
        logger.info("初始化数据库...")
        await init_db(config.DATABASE_URL)
        logger.info("数据库初始化完成")

    async def post_shutdown(self, application: Application):
        """应用关闭前的钩子"""
        logger.info("关闭数据库连接...")
        await close_db()
        logger.info("数据库连接已关闭")

    def run(self):
        """启动机器人"""
        logger.info("🎵 音乐机器人启动中...")

        # 创建应用
        self.app = (
            Application.builder()
            .token(config.TELEGRAM_BOT_TOKEN)
            .post_init(self.post_init)
            .post_shutdown(self.post_shutdown)
            .build()
        )

        # 添加命令处理器
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("search", self.search_command))
        self.app.add_handler(CommandHandler("youtube", self.youtube_command))
        self.app.add_handler(CommandHandler("spotify", self.spotify_command))
        self.app.add_handler(CommandHandler("settings", self.settings_command))
        self.app.add_handler(CommandHandler("history", self.history_command))

        # 添加回调查询处理器
        self.app.add_handler(CallbackQueryHandler(self.button_callback))

        # 添加文本消息处理器（普通消息直接搜索）
        self.app.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self.text_message_handler
        ))

        # 启动机器人
        logger.info("✅ 机器人已启动，正在监听消息...")
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    bot = MusicBot()
    bot.run()
