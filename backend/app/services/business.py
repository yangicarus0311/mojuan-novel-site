"""Services for business logic"""
from sqlalchemy.orm import Session
from app.models.models import Work, Chapter, User, Bookshelf, ReadProgress
from typing import List, Optional


def get_works(db: Session, category: Optional[str] = None, skip: int = 0, limit: int = 20):
    query = db.query(Work)
    if category:
        query = query.filter(Work.category == category)
    return query.order_by(Work.created_at.desc()).offset(skip).limit(limit).all()


def get_work_by_id(db: Session, work_id: int):
    return db.query(Work).filter(Work.id == work_id).first()


def get_work_chapters(db: Session, work_id: int):
    return db.query(Chapter).filter(Chapter.work_id == work_id).order_by(Chapter.chapter_number).all()


def get_chapter_by_id(db: Session, chapter_id: int):
    return db.query(Chapter).filter(Chapter.id == chapter_id).first()


def search_works(db: Session, keyword: str, skip: int = 0, limit: int = 20):
    return db.query(Work).filter(
        (Work.title.contains(keyword)) | (Work.author.contains(keyword))
    ).offset(skip).limit(limit).all()


def get_user_bookshelf(db: Session, user_id: int):
    return db.query(Bookshelf).filter(Bookshelf.user_id == user_id).all()


def add_to_bookshelf(db: Session, user_id: int, work_id: int):
    existing = db.query(Bookshelf).filter(
        Bookshelf.user_id == user_id,
        Bookshelf.work_id == work_id
    ).first()
    if existing:
        return existing
    shelf = Bookshelf(user_id=user_id, work_id=work_id)
    db.add(shelf)
    db.commit()
    return shelf


def remove_from_bookshelf(db: Session, user_id: int, work_id: int):
    db.query(Bookshelf).filter(
        Bookshelf.user_id == user_id,
        Bookshelf.work_id == work_id
    ).delete()
    db.commit()


def get_read_progress(db: Session, user_id: int, work_id: int):
    return db.query(ReadProgress).filter(
        ReadProgress.user_id == user_id,
        ReadProgress.work_id == work_id
    ).first()


def update_read_progress(db: Session, user_id: int, work_id: int, chapter_id: int):
    progress = db.query(ReadProgress).filter(
        ReadProgress.user_id == user_id,
        ReadProgress.work_id == work_id
    ).first()
    if progress:
        progress.chapter_id = chapter_id
    else:
        progress = ReadProgress(user_id=user_id, work_id=work_id, chapter_id=chapter_id)
        db.add(progress)
    db.commit()
    return progress


def get_rankings(db: Session, sort_by: str = "clicks", limit: int = 10):
    if sort_by == "favorites":
        return db.query(Work).order_by(Work.favorites.desc()).limit(limit).all()
    return db.query(Work).order_by(Work.clicks.desc()).limit(limit).all()


def get_recent_updates(db: Session, limit: int = 20):
    return db.query(Chapter).order_by(Chapter.created_at.desc()).limit(limit).all()
