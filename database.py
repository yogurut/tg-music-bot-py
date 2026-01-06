"""
数据库模型 - 存储用户信息和下载历史
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

Base = declarative_base()


class User(Base):
    """用户表"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    language_code = Column(String, default='en')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<User(user_id={self.user_id}, username={self.username})>"


class DownloadHistory(Base):
    """下载历史表"""
    __tablename__ = 'download_history'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    song_title = Column(String, nullable=False)
    artist = Column(String, nullable=True)
    source = Column(String, nullable=False)  # 'youtube' 或 'spotify'
    source_url = Column(String, nullable=True)
    duration = Column(Integer, nullable=True)  # 秒
    file_size = Column(Integer, nullable=True)  # 字节
    downloaded_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<DownloadHistory(user_id={self.user_id}, song={self.song_title})>"


class UserPreference(Base):
    """用户偏好设置表"""
    __tablename__ = 'user_preferences'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False, index=True)
    preferred_source = Column(String, default='youtube')  # 'youtube' 或 'spotify'
    preferred_quality = Column(String, default='high')  # 'low', 'medium', 'high'
    auto_download = Column(Boolean, default=False)  # 是否自动下载第一个结果
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<UserPreference(user_id={self.user_id}, source={self.preferred_source})>"


# 异步数据库引擎
async_engine = None
AsyncSessionLocal = None


async def init_db(database_url: str):
    """初始化数据库"""
    global async_engine, AsyncSessionLocal

    async_engine = create_async_engine(
        database_url,
        echo=False,
        future=True
    )

    AsyncSessionLocal = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    # 创建所有表
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db_session():
    """获取数据库会话"""
    async with AsyncSessionLocal() as session:
        yield session


async def close_db():
    """关闭数据库连接"""
    if async_engine:
        await async_engine.dispose()
