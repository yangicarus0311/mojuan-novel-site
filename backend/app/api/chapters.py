from sqlalchemy.orm import Session, defer
from sqlalchemy import func
from app.models.models import Chapter, Work, ReadProgress, WorkPrice, UserSubscription, SubscriptionStatus
from app.schemas.schemas import ChapterResponse, ChapterSummary, ChapterCreate, ChapterListResponse, ReadProgressUpdate, ReadProgressResponse
from app.core.database import get_db
from app.core.auth import get_current_user, require_admin
from app.models.models import User
from app.services.payment_service import PaymentService
from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import datetime

router = APIRouter(prefix="/chapters", tags=["章节"])


@router.get("", response_model=ChapterListResponse)
def get_chapters(
    work_id: int = Query(..., ge=1),
    db: Session = Depends(get_db)
):
    chapters = db.query(Chapter).options(defer(Chapter.content)).filter(
        Chapter.work_id == work_id
    ).order_by(Chapter.chapter_number).all()
    
    # 标记VIP章节
    work_price = db.query(WorkPrice).filter(WorkPrice.work_id == work_id).first()
    chapters_with_vip = []
    for chapter in chapters:
        chapter_data = ChapterSummary.model_validate(chapter)
        chapter_data.is_vip = bool(work_price and work_price.is_premium)
        chapter_data.chapter_price = float(work_price.chapter_price) if work_price else 0
        chapters_with_vip.append(chapter_data)
    
    return ChapterListResponse(
        total=len(chapters_with_vip),
        chapters=chapters_with_vip
    )


@router.get("/{chapter_id}", response_model=ChapterResponse)
def get_chapter(
    chapter_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="章节不存在")
    
    PaymentService.require_chapter_access(db, current_user.id, chapter)

    return ChapterResponse.model_validate(chapter)


@router.get("/{chapter_id}/content")
def get_chapter_content(
    chapter_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="章节不存在")
    
    PaymentService.require_chapter_access(db, current_user.id, chapter)

    return {
        "id": chapter.id,
        "work_id": chapter.work_id,
        "chapter_number": chapter.chapter_number,
        "title": chapter.title,
        "content": chapter.content,
        "word_count": chapter.word_count
    }


@router.post("", response_model=ChapterResponse)
def create_chapter(
    chapter_data: ChapterCreate,
    work_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    # Verify work exists
    work = db.query(Work).filter(Work.id == work_id).first()
    if not work:
        raise HTTPException(status_code=404, detail="作品不存在")
    
    # Check if chapter number already exists
    existing = db.query(Chapter).filter(
        Chapter.work_id == work_id,
        Chapter.chapter_number == chapter_data.chapter_number
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="章节号已存在")
    
    # Calculate word count
    word_count = len(chapter_data.content) if chapter_data.content else 0
    
    new_chapter = Chapter(
        work_id=work_id,
        volume_id=chapter_data.volume_id,
        chapter_number=chapter_data.chapter_number,
        title=chapter_data.title,
        content=chapter_data.content,
        word_count=word_count
    )
    db.add(new_chapter)
    
    # Update work word count
    work.word_count += word_count
    work.updated_at = func.now()
    
    db.commit()
    db.refresh(new_chapter)
    return ChapterResponse.model_validate(new_chapter)
