"""Parent community forum routes: posts, replies.

Non-commercial: no ads, no likes, no monetization. Pure sharing.
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.parent import Parent
from app.models.forum import ForumPost, ForumReply
from app.routers.deps import get_current_parent

router = APIRouter(prefix="/api/forum", tags=["forum"])


# ─── Schemas ───

class PostCreate(BaseModel):
    title: str
    content: str
    category: str = "分享"  # 分享, 提問, 資源


class PostOut(BaseModel):
    id: int
    parent_id: int
    parent_name: str
    title: str
    content: str
    category: str
    reply_count: int
    is_pinned: bool
    created_at: str

    class Config:
        from_attributes = True


class ReplyCreate(BaseModel):
    content: str


class ReplyOut(BaseModel):
    id: int
    post_id: int
    parent_id: int
    parent_name: str
    content: str
    created_at: str

    class Config:
        from_attributes = True


# ─── Posts ───

@router.get("/posts")
def list_posts(
    category: str | None = Query(None),
    limit: int = Query(20, le=50),
    offset: int = Query(0),
    parent: Parent = Depends(get_current_parent),
    db: Session = Depends(get_db),
):
    """List forum posts, newest first. Pinned posts always on top."""
    q = db.query(ForumPost)
    if category:
        q = q.filter(ForumPost.category == category)
    q = q.order_by(ForumPost.is_pinned.desc(), ForumPost.created_at.desc())
    posts = q.offset(offset).limit(limit).all()
    return [
        {
            "id": p.id,
            "parent_id": p.parent_id,
            "parent_name": p.parent_name,
            "title": p.title,
            "content": p.content[:200] + "..." if len(p.content) > 200 else p.content,
            "category": p.category,
            "reply_count": p.reply_count,
            "is_pinned": p.is_pinned,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        }
        for p in posts
    ]


@router.post("/posts")
def create_post(
    req: PostCreate,
    parent: Parent = Depends(get_current_parent),
    db: Session = Depends(get_db),
):
    """Create a new forum post."""
    if len(req.title.strip()) < 2:
        raise HTTPException(400, "標題至少 2 個字")
    if len(req.content.strip()) < 5:
        raise HTTPException(400, "內容至少 5 個字")

    # Use parent email prefix as display name for privacy
    display_name = parent.email.split("@")[0] if parent.email else "匿名家長"

    post = ForumPost(
        parent_id=parent.id,
        parent_name=display_name,
        title=req.title.strip(),
        content=req.content.strip(),
        category=req.category,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return {
        "id": post.id,
        "parent_id": post.parent_id,
        "parent_name": post.parent_name,
        "title": post.title,
        "content": post.content,
        "category": post.category,
        "reply_count": 0,
        "is_pinned": False,
        "created_at": post.created_at.isoformat(),
    }


@router.get("/posts/{post_id}")
def get_post(
    post_id: int,
    parent: Parent = Depends(get_current_parent),
    db: Session = Depends(get_db),
):
    """Get a single post with full content."""
    post = db.query(ForumPost).filter(ForumPost.id == post_id).first()
    if not post:
        raise HTTPException(404, "找不到此帖子")
    return {
        "id": post.id,
        "parent_id": post.parent_id,
        "parent_name": post.parent_name,
        "title": post.title,
        "content": post.content,
        "category": post.category,
        "reply_count": post.reply_count,
        "is_pinned": post.is_pinned,
        "created_at": post.created_at.isoformat() if post.created_at else None,
    }


@router.delete("/posts/{post_id}")
def delete_post(
    post_id: int,
    parent: Parent = Depends(get_current_parent),
    db: Session = Depends(get_db),
):
    """Delete own post (only the author can delete)."""
    post = db.query(ForumPost).filter(ForumPost.id == post_id).first()
    if not post:
        raise HTTPException(404, "找不到此帖子")
    if post.parent_id != parent.id:
        raise HTTPException(403, "只能刪除自己的帖子")
    db.delete(post)
    db.commit()
    return {"message": "帖子已刪除"}


# ─── Replies ───

@router.get("/posts/{post_id}/replies")
def list_replies(
    post_id: int,
    parent: Parent = Depends(get_current_parent),
    db: Session = Depends(get_db),
):
    """List all replies for a post."""
    replies = db.query(ForumReply).filter(
        ForumReply.post_id == post_id,
    ).order_by(ForumReply.created_at.asc()).all()
    return [
        {
            "id": r.id,
            "post_id": r.post_id,
            "parent_id": r.parent_id,
            "parent_name": r.parent_name,
            "content": r.content,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in replies
    ]


@router.post("/posts/{post_id}/replies")
def create_reply(
    post_id: int,
    req: ReplyCreate,
    parent: Parent = Depends(get_current_parent),
    db: Session = Depends(get_db),
):
    """Reply to a post."""
    post = db.query(ForumPost).filter(ForumPost.id == post_id).first()
    if not post:
        raise HTTPException(404, "找不到此帖子")
    if len(req.content.strip()) < 2:
        raise HTTPException(400, "回覆至少 2 個字")

    display_name = parent.email.split("@")[0] if parent.email else "匿名家長"

    reply = ForumReply(
        post_id=post_id,
        parent_id=parent.id,
        parent_name=display_name,
        content=req.content.strip(),
    )
    db.add(reply)
    post.reply_count += 1
    db.commit()
    db.refresh(reply)
    return {
        "id": reply.id,
        "post_id": reply.post_id,
        "parent_id": reply.parent_id,
        "parent_name": reply.parent_name,
        "content": reply.content,
        "created_at": reply.created_at.isoformat(),
    }


@router.delete("/replies/{reply_id}")
def delete_reply(
    reply_id: int,
    parent: Parent = Depends(get_current_parent),
    db: Session = Depends(get_db),
):
    """Delete own reply."""
    reply = db.query(ForumReply).filter(ForumReply.id == reply_id).first()
    if not reply:
        raise HTTPException(404, "找不到此回覆")
    if reply.parent_id != parent.id:
        raise HTTPException(403, "只能刪除自己的回覆")
    post = db.query(ForumPost).filter(ForumPost.id == reply.post_id).first()
    if post:
        post.reply_count = max(0, post.reply_count - 1)
    db.delete(reply)
    db.commit()
    return {"message": "回覆已刪除"}
