from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from database import Base


class Channel(Base):
    __tablename__ = "channels"

    id = Column(String, primary_key=True)
    title = Column(String)
    statistics = relationship(
        "ChannelStatistics", back_populates="channel")
    videos = relationship("Video", back_populates="channel", cascade="all, delete",
                          passive_deletes=True,)


class ChannelStatistics(Base):
    __tablename__ = "channel_statistics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    channel_id = Column(String, ForeignKey("channels.id", ondelete="CASCADE"))
    view_count = Column(Integer)
    subscriber_count = Column(Integer)
    video_count = Column(Integer)
    fetch_date = Column(DateTime, default=datetime.now)
    channel = relationship("Channel", back_populates="statistics")


class Video(Base):
    __tablename__ = "videos"

    id = Column(String, primary_key=True)
    channel_id = Column(String, ForeignKey("channels.id", ondelete="CASCADE"))
    title = Column(String)
    pub_date = Column(DateTime)
    channel = relationship("Channel", back_populates="videos")
    statistics = relationship(
        "VideoStatistics", back_populates="video", cascade="all, delete",
        passive_deletes=True,)


class VideoStatistics(Base):
    __tablename__ = "video_statistics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(String, ForeignKey("videos.id", ondelete="CASCADE"))
    view_count = Column(Integer)
    like_count = Column(Integer)
    comment_count = Column(Integer)
    privacy_status = Column(String)
    yt_rating = Column(String)
    fetch_date = Column(DateTime, default=datetime.now)
    video = relationship("Video", back_populates="statistics")
