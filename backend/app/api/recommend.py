from sqlalchemy.orm import Session
from app.models.models import Highlight, Work, Chapter, User
from app.schemas.schemas import HighlightResponse
from app.core.database import get_db
from app.api.auth import get_current_user
from fastapi import APIRouter, Depends, Query

router = APIRouter(prefix="/recommend", tags=["推荐"])


@router.get("/personalized")
def get_personalized_recommendations(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """基于用户阅读历史的个性化推荐"""
    # 获取用户最近阅读的作品分类
    recent_sessions = db.query(ReadingSession, Work).join(
        Work, ReadingSession.work_id == Work.id
    ).filter(
        ReadingSession.user_id == current_user.id
    ).order_by(ReadingSession.session_date.desc()).limit(20).all()
    
    categories = set()
    read_work_ids = set()
    for _, w in recent_sessions:
        categories.add(w.category)
        read_work_ids.add(w.id)
    
    # 没有阅读历史时返回热门作品
    if not categories:
        return _get_hot_works(db, limit)
    
    # 按分类推荐同类作品（排除已读的）
    from sqlalchemy import or_
    works = db.query(Work).filter(
        Work.category.in_(categories),
        ~Work.id.in_(read_work_ids) if read_work_ids else True
    ).order_by(Work.clicks.desc()).limit(limit).all()
    
    return _format_works(works)


@router.get("/similar/{work_id}")
def get_similar_works(
    work_id: int,
    limit: int = Query(8, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """获取相似作品推荐 - 基于分类和标签"""
    work = db.query(Work).filter(Work.id == work_id).first()
    if not work:
        return {"error": "作品不存在"}
    
    similar = db.query(Work).filter(
        Work.category == work.category,
        Work.id != work_id
    ).order_by(Work.favorites.desc()).limit(limit).all()
    
    return _format_works(similar)


@router.get("/hot")
def get_hot_works(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """获取热门作品"""
    return _get_hot_works(db, limit)


@router.get("/new")
def get_new_works(
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """获取新作品"""
    from datetime import datetime, timedelta
    since = datetime.now() - timedelta(days=days)
    
    works = db.query(Work).filter(
        Work.created_at >= since
    ).order_by(Work.created_at.desc()).limit(limit).all()
    
    return _format_works(works)


@router.get("/trending")
def get_trending_works(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """获取上升趋势作品（7天内点击增长最快）"""
    from datetime import datetime, timedelta
    from sqlalchemy import func
    
    # 简单实现：按收藏+点击综合排序
    works = db.query(Work).order_by(
        (Work.clicks + Work.favorites * 10).desc()
    ).limit(limit).all()
    
    return _format_works(works)


def _get_hot_works(db: Session, limit: int):
    works = db.query(Work).order_by(Work.clicks.desc()).limit(limit).all()
    return _format_works(works)


def _format_works(works):
    return [
        {
            "id": w.id, "title": w.title, "author": w.author,
            "description": w.description[:100] if w.description else "",
            "category": w.category, "status": w.status.value if hasattr(w.status, 'value') else str(w.status),
            "word_count": w.word_count, "clicks": w.clicks,
            "favorites": w.favorites, "cover_url": w.cover_url
        }
        for w in works
    ]
