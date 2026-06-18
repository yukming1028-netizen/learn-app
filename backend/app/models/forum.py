"""Parent community forum models: Post, Reply, PostLike."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class ForumPost(Base):
    """A parent's post in the community forum."""
    __tablename__ = "forum_posts"

    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("parents.id"), nullable=False, index=True)
    parent_name = Column(String(50), default="匿名家長")
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(30), default="分享")  # 分享, 提問, 資源
    reply_count = Column(Integer, default=0)
    is_pinned = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    replies = relationship("ForumReply", backref="post", cascade="all, delete-orphan")


class ForumReply(Base):
    """A reply to a forum post."""
    __tablename__ = "forum_replies"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("forum_posts.id"), nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey("parents.id"), nullable=False)
    parent_name = Column(String(50), default="匿名家長")
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
