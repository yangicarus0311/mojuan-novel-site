from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, or_, func
from app.models.models import Work, WorkStatus, User
from app.schemas.schemas import WorkResponse, WorkListResponse, WorkCreate
from app.core.database import get_db
from app.api.auth import get_current_user
from fastapi import APIRouter, Depends, HTTPException, status, Query

router = APIRouter(prefix="/works", tags=["作品"])


@router.get("", response_model=WorkListResponse)
def get_works(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: str = Query(None),
    sort: str = Query("updated_at", regex="^(updated_at|clicks|favorites|created_at)$"),
    order: str = Query("desc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db)
):
    query = db.query(Work)
    
    if category:
        query = query.filter(Work.category == category)
    
    # Get total count
    total = query.count()
    
    # Apply sorting
    sort_column = getattr(Work, sort)
    if order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))
    
    # Apply pagination
    offset = (page - 1) * page_size
    works = query.offset(offset).limit(page_size).all()
    
    return WorkListResponse(
        total=total,
        page=page,
        page_size=page_size,
        works=[WorkResponse.model_validate(w) for w in works]
    )


@router.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Work.category, func.count(Work.id).label("count")).group_by(Work.category).all()
    return [{"category": c[0], "count": c[1]} for c in categories]


@router.get("/rankings")
def get_rankings(
    sort: str = Query("clicks", regex="^(clicks|favorites)$"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    sort_column = getattr(Work, sort)
    works = db.query(Work).order_by(desc(sort_column)).limit(limit).all()
    return [{"rank": i+1, "work": WorkResponse.model_validate(w)} for i, w in enumerate(works)]


@router.get("/{work_id}", response_model=WorkResponse)
def get_work(work_id: int, db: Session = Depends(get_db)):
    work = db.query(Work).filter(Work.id == work_id).first()
    if not work:
        raise HTTPException(status_code=404, detail="作品不存在")
    
    # Increment clicks
    work.clicks += 1
    db.commit()
    
    return WorkResponse.model_validate(work)


@router.post("", response_model=WorkResponse)
def create_work(
    work_data: WorkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_work = Work(
        title=work_data.title,
        author=work_data.author,
        description=work_data.description,
        cover_url=work_data.cover_url or "/uploads/covers/default.png",
        category=work_data.category,
        status=work_data.status
    )
    db.add(new_work)
    db.commit()
    db.refresh(new_work)
    return WorkResponse.model_validate(new_work)


@router.get("/search")
def search_works(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Work).filter(
        or_(
            Work.title.contains(q),
            Work.author.contains(q),
            Work.description.contains(q)
        )
    )
    total = query.count()
    offset = (page - 1) * page_size
    works = query.offset(offset).limit(page_size).all()
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "works": [WorkResponse.model_validate(w) for w in works]
    }

