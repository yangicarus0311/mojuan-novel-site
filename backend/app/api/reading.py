"""阅读会话/统计 API"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, date
from app.models.models import ReadingSession, User, Work, Chapter, ReadProgress
from app.schemas.schemas import (
    ReadingSessionHeartbeat, DailyStatsResponse, ReadingStatsResponse
)
from app.core.database import get_db
from app.api.auth import get_current_user
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List

router = APIRouter(prefix="/reading", tags=["阅读统计"])


@router.post("/heartbeat")
def reading_heartbeat(
    data: ReadingSessionHeartbeat,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record bounded active-time deltas and chapter-relative progress."""
    chapter = db.query(Chapter).filter(Chapter.id == data.chapter_id, Chapter.work_id == data.work_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="章节不存在或不属于该作品")
    from app.services.payment_service import PaymentService
    PaymentService.require_chapter_access(db, current_user.id, chapter)
    now = datetime.now()
    previous = db.query(ReadingSession).filter(ReadingSession.user_id == current_user.id).order_by(
        ReadingSession.session_date.desc(), ReadingSession.id.desc()
    ).first()
    elapsed_limit = max(0, int((now - previous.session_date).total_seconds())) if previous else 60
    duration = min(data.duration_seconds, elapsed_limit, 60)
    already_read = db.query(func.coalesce(func.sum(ReadingSession.chars_read), 0)).filter(
        ReadingSession.user_id == current_user.id, ReadingSession.chapter_id == data.chapter_id
    ).scalar()
    position = len(chapter.content or "") * data.progress // 100
    chars = min(data.chars_read, max(0, position - already_read), duration * 100)
    if duration > 0 or chars > 0:
        db.add(ReadingSession(user_id=current_user.id, work_id=data.work_id, chapter_id=data.chapter_id,
            duration_seconds=duration, chars_read=chars, session_date=now))
    progress = db.query(ReadProgress).filter(
        ReadProgress.user_id == current_user.id, ReadProgress.work_id == data.work_id
    ).first()
    if not progress:
        progress = ReadProgress(user_id=current_user.id, work_id=data.work_id)
        db.add(progress)
    progress.chapter_id = data.chapter_id
    progress.progress = data.progress
    progress.updated_at = now
    db.commit()
    return {"status": "ok", "duration_seconds": duration, "chars_read": chars}


@router.get("/stats", response_model=ReadingStatsResponse)
def get_reading_stats(
    days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取阅读统计"""
    since = datetime.now() - timedelta(days=days)
    
    # 总阅读时长
    total_duration = db.query(func.coalesce(func.sum(ReadingSession.duration_seconds), 0)).filter(
        ReadingSession.user_id == current_user.id,
        ReadingSession.session_date >= since
    ).scalar()
    
    # 总阅读字数
    total_chars = db.query(func.coalesce(func.sum(ReadingSession.chars_read), 0)).filter(
        ReadingSession.user_id == current_user.id,
        ReadingSession.session_date >= since
    ).scalar()
    
    # 阅读作品数
    total_works = db.query(func.count(func.distinct(ReadingSession.work_id))).filter(
        ReadingSession.user_id == current_user.id,
        ReadingSession.session_date >= since
    ).scalar()
    
    # 今日阅读时长
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_duration = db.query(func.coalesce(func.sum(ReadingSession.duration_seconds), 0)).filter(
        ReadingSession.user_id == current_user.id,
        ReadingSession.session_date >= today_start
    ).scalar()
    
    # 每日统计
    daily = db.query(
        func.date(ReadingSession.session_date).label("day"),
        func.coalesce(func.sum(ReadingSession.duration_seconds), 0).label("duration"),
        func.coalesce(func.sum(ReadingSession.chars_read), 0).label("chars"),
        func.count(func.distinct(ReadingSession.work_id)).label("works")
    ).filter(
        ReadingSession.user_id == current_user.id,
        ReadingSession.session_date >= since
    ).group_by(
        func.date(ReadingSession.session_date)
    ).order_by(
        func.date(ReadingSession.session_date).desc()
    ).all()
    
    # 连续阅读天数
    streak = _calc_streak(db, current_user.id)
    
    daily_stats = [
        DailyStatsResponse(
            date=str(d.day),
            duration_minutes=d.duration // 60,
            chars_read=d.chars,
            works_read=d.works
        )
        for d in daily
    ]
    
    return ReadingStatsResponse(
        total_duration_minutes=total_duration // 60,
        total_chars=total_chars,
        total_works=total_works,
        daily_stats=daily_stats,
        streak_days=streak,
        today_minutes=today_duration // 60
    )


def _calc_streak(db: Session, user_id: int) -> int:
    """计算连续阅读天数"""
    today = date.today()
    for i in range(365):
        check_date = today - timedelta(days=i)
        count = db.query(ReadingSession).filter(
            ReadingSession.user_id == user_id,
            func.date(ReadingSession.session_date) == check_date.isoformat()
        ).count()
        if count == 0:
            return i
    return 365
