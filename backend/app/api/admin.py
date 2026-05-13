from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.models import User, Work, Chapter
from app.schemas.schemas import WorkResponse, UserResponse, ChapterResponse
from app.core.database import get_db
from app.api.auth import get_current_user
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime, timedelta

router = APIRouter(prefix="/admin", tags=["管理后台"])


def require_admin(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="权限不足")
    return current_user


@router.get("/users", response_model=List[UserResponse])
def get_users(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    offset = (page - 1) * page_size
    users = db.query(User).offset(offset).limit(page_size).all()
    return users


@router.get("/users/count")
def get_user_count(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    total = db.query(User).count()
    return {"total": total}


@router.get("/works", response_model=List[WorkResponse])
def get_all_works(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    offset = (page - 1) * page_size
    works = db.query(Work).order_by(Work.id.desc()).offset(offset).limit(page_size).all()
    return works


@router.get("/works/count")
def get_work_count(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    total = db.query(Work).count()
    return {"total": total}


@router.delete("/works/{work_id}")
def delete_work(
    work_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    work = db.query(Work).filter(Work.id == work_id).first()
    if not work:
        raise HTTPException(status_code=404, detail="作品不存在")
    
    # Delete all chapters first
    db.query(Chapter).filter(Chapter.work_id == work_id).delete()
    db.delete(work)
    db.commit()
    return {"message": "删除成功"}


@router.post("/works", response_model=WorkResponse)
def create_work(
    title: str,
    author: str,
    description: str = "",
    category: str = "其他",
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    work = Work(
        title=title,
        author=author,
        description=description,
        category=category,
        cover_url="/uploads/covers/default.png"
    )
    db.add(work)
    db.commit()
    db.refresh(work)
    return work


@router.post("/works/{work_id}/chapters", response_model=ChapterResponse)
def create_chapter(
    work_id: int,
    title: str,
    content: str,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    work = db.query(Work).filter(Work.id == work_id).first()
    if not work:
        raise HTTPException(status_code=404, detail="作品不存在")
    
    # Get next chapter number
    last_chapter = db.query(Chapter).filter(Chapter.work_id == work_id).order_by(Chapter.chapter_number.desc()).first()
    next_num = (last_chapter.chapter_number + 1) if last_chapter else 1
    
    chapter = Chapter(
        work_id=work_id,
        chapter_number=next_num,
        title=title,
        content=content,
        word_count=len(content)
    )
    db.add(chapter)
    
    # Update work word count
    work.word_count += len(content)
    work.updated_at = datetime.now()
    
    db.commit()
    db.refresh(chapter)
    return chapter


@router.put("/works/{work_id}", response_model=WorkResponse)
def update_work(
    work_id: int,
    title: str = None,
    author: str = None,
    description: str = None,
    category: str = None,
    status: str = None,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    work = db.query(Work).filter(Work.id == work_id).first()
    if not work:
        raise HTTPException(status_code=404, detail="作品不存在")
    
    if title:
        work.title = title
    if author:
        work.author = author
    if description is not None:
        work.description = description
    if category:
        work.category = category
    if status:
        work.status = status
    
    work.updated_at = datetime.now()
    db.commit()
    db.refresh(work)
    return work


@router.get("/stats")
def get_stats(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    user_count = db.query(User).count()
    work_count = db.query(Work).count()
    chapter_count = db.query(Chapter).count()
    
    # Recent stats
    today = datetime.now().date()
    new_works_today = db.query(Work).filter(func.date(Work.created_at) == today).count()
    new_users_today = db.query(User).filter(func.date(User.created_at) == today).count()
    
    return {
        "total_users": user_count,
        "total_works": work_count,
        "total_chapters": chapter_count,
        "new_works_today": new_works_today,
        "new_users_today": new_users_today
    }
