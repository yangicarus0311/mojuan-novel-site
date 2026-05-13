"""划线/想法 API"""
from sqlalchemy.orm import Session
from app.models.models import Highlight, User, Work, Chapter
from app.schemas.schemas import HighlightCreate, HighlightUpdate, HighlightResponse
from app.core.database import get_db
from app.api.auth import get_current_user
from fastapi import APIRouter, Depends, HTTPException, status, Query

router = APIRouter(prefix="/highlights", tags=["划线与想法"])


@router.get("", response_model=list[HighlightResponse])
def get_highlights(
    work_id: int = Query(None),
    chapter_id: int = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户的划线列表"""
    query = db.query(Highlight).filter(Highlight.user_id == current_user.id)
    if work_id:
        query = query.filter(Highlight.work_id == work_id)
    if chapter_id:
        query = query.filter(Highlight.chapter_id == chapter_id)
    return query.order_by(Highlight.created_at.desc()).all()


@router.post("", response_model=HighlightResponse, status_code=status.HTTP_201_CREATED)
def create_highlight(
    work_id: int,
    data: HighlightCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建划线/想法"""
    chapter = db.query(Chapter).filter(Chapter.id == data.chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="章节不存在")
    
    highlight = Highlight(
        user_id=current_user.id,
        work_id=work_id,
        chapter_id=data.chapter_id,
        content=data.content,
        note=data.note,
        color=data.color,
        location_start=data.location_start,
        location_end=data.location_end,
        page_url=f"/works/{work_id}/chapters/{data.chapter_id}"
    )
    db.add(highlight)
    db.commit()
    db.refresh(highlight)
    return highlight


@router.put("/{highlight_id}", response_model=HighlightResponse)
def update_highlight(
    highlight_id: int,
    data: HighlightUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新划线内容或颜色"""
    highlight = db.query(Highlight).filter(
        Highlight.id == highlight_id,
        Highlight.user_id == current_user.id
    ).first()
    if not highlight:
        raise HTTPException(status_code=404, detail="划线不存在")
    
    if data.note is not None:
        highlight.note = data.note
    if data.color is not None:
        highlight.color = data.color
    
    db.commit()
    db.refresh(highlight)
    return highlight


@router.delete("/{highlight_id}")
def delete_highlight(
    highlight_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除划线"""
    highlight = db.query(Highlight).filter(
        Highlight.id == highlight_id,
        Highlight.user_id == current_user.id
    ).first()
    if not highlight:
        raise HTTPException(status_code=404, detail="划线不存在")
    
    db.delete(highlight)
    db.commit()
    return {"message": "删除成功"}


@router.get("/notebook", response_model=list[HighlightResponse])
def get_notebook(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取划线本 - 所有带笔记的划线"""
    return db.query(Highlight).filter(
        Highlight.user_id == current_user.id,
        Highlight.note != "",
        Highlight.note.isnot(None)
    ).order_by(Highlight.created_at.desc()).all()
