from sqlalchemy.orm import Session
from app.models.models import Bookshelf, Work, ReadProgress, Chapter
from app.schemas.schemas import BookshelfResponse, ReadProgressResponse, ReadProgressUpdate
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.models import User
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/bookshelf", tags=["书架"])


@router.get("", response_model=list[BookshelfResponse])
def get_bookshelf(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    items = db.query(Bookshelf).filter(
        Bookshelf.user_id == current_user.id
    ).order_by(Bookshelf.created_at.desc()).all()
    return [BookshelfResponse.model_validate(item) for item in items]


@router.post("", response_model=BookshelfResponse)
def add_to_bookshelf(
    work_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if work exists
    work = db.query(Work).filter(Work.id == work_id).first()
    if not work:
        raise HTTPException(status_code=404, detail="作品不存在")
    
    # Check if already in bookshelf
    existing = db.query(Bookshelf).filter(
        Bookshelf.user_id == current_user.id,
        Bookshelf.work_id == work_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="作品已在书架中")
    
    # Add to bookshelf
    new_item = Bookshelf(user_id=current_user.id, work_id=work_id)
    db.add(new_item)
    
    # Increment favorites
    work.favorites += 1
    
    db.commit()
    db.refresh(new_item)
    return BookshelfResponse.model_validate(new_item)


@router.delete("/{work_id}")
def remove_from_bookshelf(
    work_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    item = db.query(Bookshelf).filter(
        Bookshelf.user_id == current_user.id,
        Bookshelf.work_id == work_id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="作品不在书架中")
    
    # Decrement favorites
    work = db.query(Work).filter(Work.id == work_id).first()
    if work and work.favorites > 0:
        work.favorites -= 1
    
    db.delete(item)
    db.commit()
    return {"message": "已从书架移除"}


@router.get("/progress/{work_id}", response_model=ReadProgressResponse)
def get_read_progress(
    work_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    progress = db.query(ReadProgress).filter(
        ReadProgress.user_id == current_user.id,
        ReadProgress.work_id == work_id
    ).first()
    if not progress:
        raise HTTPException(status_code=404, detail="暂无阅读进度")
    return ReadProgressResponse.model_validate(progress)


@router.put("/progress/{work_id}", response_model=ReadProgressResponse)
def update_read_progress(
    work_id: int,
    progress_data: ReadProgressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    chapter = db.query(Chapter).filter(Chapter.id == progress_data.chapter_id, Chapter.work_id == work_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="章节不存在或不属于该作品")
    from app.services.payment_service import PaymentService
    PaymentService.require_chapter_access(db, current_user.id, chapter)
    progress = db.query(ReadProgress).filter(
        ReadProgress.user_id == current_user.id,
        ReadProgress.work_id == work_id
    ).first()

    if progress:
        progress.chapter_id = progress_data.chapter_id
        progress.progress = progress_data.progress
    else:
        progress = ReadProgress(
            user_id=current_user.id,
            work_id=work_id,
            chapter_id=progress_data.chapter_id,
            progress=progress_data.progress
        )
        db.add(progress)
    
    db.commit()
    db.refresh(progress)
    return ReadProgressResponse.model_validate(progress)
