"""
Spotify音乐搜索 - 获取Spotify歌曲信息，然后在YouTube下载
"""
from typing import List, Dict, Optional
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from loguru import logger
import config


class SpotifySearcher:
    """Spotify搜索器类"""

    def __init__(self):
        self.enabled = config.SPOTIFY_ENABLED
        self.client = None

        if self.enabled:
            try:
                auth_manager = SpotifyClientCredentials(
                    client_id=config.SPOTIFY_CLIENT_ID,
                    client_secret=config.SPOTIFY_CLIENT_SECRET
                )
                self.client = spotipy.Spotify(auth_manager=auth_manager)
                logger.info("Spotify客户端初始化成功")
            except Exception as e:
                logger.error(f"Spotify初始化失败: {e}")
                self.enabled = False
        else:
            logger.warning("Spotify未配置，仅使用YouTube搜索")

    async def search(self, query: str, limit: int = 5) -> List[Dict]:
        """
        搜索Spotify音乐

        Args:
            query: 搜索关键词
            limit: 返回结果数量

        Returns:
            搜索结果列表
        """
        if not self.enabled or not self.client:
            logger.warning("Spotify未启用")
            return []

        logger.info(f"Spotify搜索: {query}")

        try:
            results = self.client.search(q=query, limit=limit, type='track')

            if not results or 'tracks' not in results:
                return []

            tracks = []
            for item in results['tracks']['items']:
                # 提取艺术家信息
                artists = [artist['name'] for artist in item['artists']]
                artist_name = ', '.join(artists)

                # 提取专辑信息
                album = item['album']
                album_name = album['name']
                album_image = album['images'][0]['url'] if album['images'] else None

                # 构建YouTube搜索查询
                youtube_query = f"{artist_name} - {item['name']}"

                tracks.append({
                    'title': item['name'],
                    'artist': artist_name,
                    'album': album_name,
                    'duration': item['duration_ms'] // 1000,  # 转换为秒
                    'thumbnail': album_image,
                    'spotify_url': item['external_urls']['spotify'],
                    'youtube_query': youtube_query,
                    'popularity': item['popularity'],
                    'source': 'spotify'
                })

            logger.info(f"Spotify搜索到 {len(tracks)} 首歌曲")
            return tracks

        except Exception as e:
            logger.error(f"Spotify搜索失败: {e}")
            return []

    async def get_track_info(self, track_id: str) -> Optional[Dict]:
        """
        获取单首歌曲的详细信息

        Args:
            track_id: Spotify曲目ID

        Returns:
            歌曲信息字典
        """
        if not self.enabled or not self.client:
            return None

        try:
            track = self.client.track(track_id)

            artists = [artist['name'] for artist in track['artists']]
            artist_name = ', '.join(artists)

            return {
                'title': track['name'],
                'artist': artist_name,
                'album': track['album']['name'],
                'duration': track['duration_ms'] // 1000,
                'thumbnail': track['album']['images'][0]['url'] if track['album']['images'] else None,
                'spotify_url': track['external_urls']['spotify'],
                'youtube_query': f"{artist_name} - {track['name']}",
                'source': 'spotify'
            }

        except Exception as e:
            logger.error(f"获取Spotify歌曲信息失败: {e}")
            return None

    async def get_playlist_tracks(self, playlist_id: str, limit: int = 20) -> List[Dict]:
        """
        获取播放列表中的歌曲

        Args:
            playlist_id: 播放列表ID
            limit: 返回结果数量

        Returns:
            歌曲列表
        """
        if not self.enabled or not self.client:
            return []

        try:
            results = self.client.playlist_tracks(playlist_id, limit=limit)

            tracks = []
            for item in results['items']:
                track = item['track']
                if not track:
                    continue

                artists = [artist['name'] for artist in track['artists']]
                artist_name = ', '.join(artists)

                tracks.append({
                    'title': track['name'],
                    'artist': artist_name,
                    'album': track['album']['name'],
                    'duration': track['duration_ms'] // 1000,
                    'thumbnail': track['album']['images'][0]['url'] if track['album']['images'] else None,
                    'spotify_url': track['external_urls']['spotify'],
                    'youtube_query': f"{artist_name} - {track['name']}",
                    'source': 'spotify'
                })

            return tracks

        except Exception as e:
            logger.error(f"获取播放列表失败: {e}")
            return []


# 全局实例
spotify_searcher = SpotifySearcher()
