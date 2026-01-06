"""
YouTube音乐下载器 - 使用yt-dlp下载音频
"""
import os
import asyncio
from pathlib import Path
from typing import List, Dict, Optional
import yt_dlp
from loguru import logger
import config


class YouTubeDownloader:
    """YouTube下载器类"""

    def __init__(self):
        self.download_path = config.DOWNLOAD_PATH
        self.max_duration = config.MAX_SONG_DURATION
        self.max_file_size = config.MAX_FILE_SIZE_MB * 1024 * 1024

    async def search(self, query: str, limit: int = 5) -> List[Dict]:
        """
        搜索YouTube视频

        Args:
            query: 搜索关键词
            limit: 返回结果数量

        Returns:
            搜索结果列表
        """
        logger.info(f"YouTube搜索: {query}")

        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'skip_download': True,
        }

        try:
            # 在线程池中运行同步代码
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None,
                self._search_sync,
                query,
                limit,
                ydl_opts
            )
            return results

        except Exception as e:
            logger.error(f"YouTube搜索失败: {e}")
            return []

    def _search_sync(self, query: str, limit: int, ydl_opts: dict) -> List[Dict]:
        """同步搜索方法"""
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_results = ydl.extract_info(f"ytsearch{limit}:{query}", download=False)

            if not search_results or 'entries' not in search_results:
                return []

            results = []
            for entry in search_results['entries']:
                if not entry:
                    continue

                # 获取时长
                duration = entry.get('duration', 0)
                if duration > self.max_duration:
                    continue

                results.append({
                    'title': entry.get('title', 'Unknown'),
                    'artist': entry.get('uploader', 'Unknown'),
                    'url': entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}",
                    'duration': duration,
                    'thumbnail': entry.get('thumbnail'),
                    'views': entry.get('view_count', 0),
                    'video_id': entry.get('id'),
                    'source': 'youtube'
                })

            return results

    async def download(self, video_url: str, user_id: int) -> Optional[Path]:
        """
        下载YouTube视频的音频

        Args:
            video_url: 视频URL
            user_id: 用户ID

        Returns:
            下载的文件路径，失败返回None
        """
        logger.info(f"开始下载YouTube音频: {video_url}")

        # 生成唯一文件名
        output_template = str(self.download_path / f"{user_id}_%(title)s.%(ext)s")

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_template,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True,
            'max_filesize': self.max_file_size,
        }

        try:
            loop = asyncio.get_event_loop()
            file_path = await loop.run_in_executor(
                None,
                self._download_sync,
                video_url,
                ydl_opts
            )

            if file_path and file_path.exists():
                logger.info(f"下载成功: {file_path}")
                return file_path
            else:
                logger.error("下载失败: 文件不存在")
                return None

        except Exception as e:
            logger.error(f"下载失败: {e}")
            return None

    def _download_sync(self, video_url: str, ydl_opts: dict) -> Optional[Path]:
        """同步下载方法"""
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)

            # 获取下载的文件路径
            if info:
                # 构建mp3文件路径
                base_path = ydl.prepare_filename(info)
                mp3_path = Path(base_path).with_suffix('.mp3')

                if mp3_path.exists():
                    return mp3_path

                # 尝试其他可能的路径
                for ext in ['.mp3', '.m4a', '.opus']:
                    test_path = Path(base_path).with_suffix(ext)
                    if test_path.exists():
                        return test_path

            return None

    async def get_video_info(self, video_url: str) -> Optional[Dict]:
        """
        获取视频信息

        Args:
            video_url: 视频URL

        Returns:
            视频信息字典
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
        }

        try:
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(
                None,
                self._get_info_sync,
                video_url,
                ydl_opts
            )
            return info

        except Exception as e:
            logger.error(f"获取视频信息失败: {e}")
            return None

    def _get_info_sync(self, video_url: str, ydl_opts: dict) -> Optional[Dict]:
        """同步获取信息方法"""
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)

            if info:
                return {
                    'title': info.get('title'),
                    'artist': info.get('uploader'),
                    'duration': info.get('duration'),
                    'thumbnail': info.get('thumbnail'),
                    'description': info.get('description'),
                }
            return None


# 全局实例
youtube_downloader = YouTubeDownloader()
