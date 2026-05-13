"""社交 API - 关注/书评/动态"""
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from app.models.models import (
    User, Work, Follow, Review, ReviewLike, 
    Highlight, ReadingSession, Bookshelf
)
from app.schemas.schemas import (
    FollowResponse, UserProfileResponse,
    ReviewCreate, ReviewResponse
)
from app.core.database import get_db
from app.api.auth import get_current_user
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional

router = APIRouter(prefix="/social", tags=["社交"])


# ==================== 关注系统 ====================


@router.post("/follow/{user_id}")
def follow_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """关注用户"""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能关注自己")
    
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    existing = db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.following_id == user_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="已关注该用户")
    
    follow = Follow(follower_id=current_user.id, following_id=user_id)
    db.add(follow)
    db.commit()
    return {"message": "关注成功"}


@router.delete("/unfollow/{user_id}")
def unfollow_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """取消关注"""
    db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.following_id == user_id
    ).delete()
    db.commit()
    return {"message": "已取消关注"}


@router.get("/followers", response_model=List[UserProfileResponse])
def get_followers(
    user_id: int = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取粉丝列表"""
    uid = user_id or current_user.id
    follows = db.query(Follow).filter(Follow.following_id == uid).all()
    follower_ids = [f.follower_id for f in follows]
    
    users = db.query(User).filter(User.id.in_(follower_ids)).all()
    results = []
    for u in users:
        is_following = db.query(Follow).filter(
            Follow.follower_id == current_user.id,
            Follow.following_id == u.id
        ).count() > 0
        results.append(_user_to_profile(db, u, current_user.id, is_following))
    return results


@router.get("/following", response_model=List[UserProfileResponse])
def get_following(
    user_id: int = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取关注列表"""
    uid = user_id or current_user.id
    follows = db.query(Follow).filter(Follow.follower_id == uid).all()
    following_ids = [f.following_id for f in follows]
    
    users = db.query(User).filter(User.id.in_(following_ids)).all()
    return [_user_to_profile(db, u, current_user.id, True) for u in users]


# ==================== 书评系统 ====================


@router.get("/reviews", response_model=List[ReviewResponse])
def get_reviews(
    work_id: int = Query(None),
    user_id: int = Query(None),
    sort: str = Query("created_at", regex="^(created_at|likes|rating)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取书评列表"""
    query = db.query(Review)
    if work_id:
        query = query.filter(Review.work_id == work_id)
    if user_id:
        query = query.filter(Review.user_id == user_id)
    
    if sort == "likes":
        query = query.order_by(desc(Review.likes))
    elif sort == "rating":
        query = query.order_by(desc(Review.rating))
    else:
        query = query.order_by(desc(Review.created_at))
    
    offset = (page - 1) * page_size
    reviews = query.offset(offset).limit(page_size).all()
    
    results = []
    for r in reviews:
        user = db.query(User).filter(User.id == r.user_id).first()
        is_liked = db.query(ReviewLike).filter(
            ReviewLike.user_id == current_user.id,
            ReviewLike.review_id == r.id
        ).count() > 0
        results.append(ReviewResponse(
            id=r.id, user_id=r.user_id, work_id=r.work_id,
            rating=r.rating, title=r.title, content=r.content,
            is_long=r.is_long, likes=r.likes, is_liked=is_liked,
            username=user.username if user else "",
            user_avatar=user.avatar if user else "",
            created_at=r.created_at, updated_at=r.updated_at
        ))
    return results


@router.post("/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建书评"""
    work = db.query(Work).filter(Work.id == data.work_id).first()
    if not work:
        raise HTTPException(status_code=404, detail="作品不存在")
    
    if data.rating < 1 or data.rating > 5:
        raise HTTPException(status_code=400, detail="评分范围1-5")
    
    review = Review(
        user_id=current_user.id,
        work_id=data.work_id,
        rating=data.rating,
        title=data.title,
        content=data.content,
        is_long=1 if len(data.content) > 200 else 0
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    
    return ReviewResponse(
        id=review.id, user_id=current_user.id, work_id=data.work_id,
        rating=data.rating, title=data.title, content=data.content,
        is_long=review.is_long, likes=0, is_liked=False,
        username=current_user.username, user_avatar=current_user.avatar,
        created_at=review.created_at, updated_at=review.updated_at
    )


@router.post("/reviews/{review_id}/like")
def like_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """点赞书评"""
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="书评不存在")
    
    existing = db.query(ReviewLike).filter(
        ReviewLike.user_id == current_user.id,
        ReviewLike.review_id == review_id
    ).first()
    
    if existing:
        # 取消点赞
        db.delete(existing)
        review.likes = max(0, review.likes - 1)
        db.commit()
        return {"liked": False, "likes": review.likes}
    else:
        # 点赞
        like = ReviewLike(user_id=current_user.id, review_id=review_id)
        db.add(like)
        review.likes += 1
        db.commit()
        return {"liked": True, "likes": review.likes}


@router.delete("/reviews/{review_id}")
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除自己的书评"""
    review = db.query(Review).filter(
        Review.id == review_id,
        Review.user_id == current_user.id
    ).first()
    if not review:
        raise HTTPException(status_code=404, detail="书评不存在")
    
    db.query(ReviewLike).filter(ReviewLike.review_id == review_id).delete()
    db.delete(review)
    db.commit()
    return {"message": "删除成功"}


# ==================== 用户动态 ====================


@router.get("/feed")
def get_feed(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取好友动态流"""
    # 获取关注列表
    follows = db.query(Follow).filter(Follow.follower_id == current_user.id).all()
    following_ids = [f.following_id for f in follows] + [current_user.id]
    
    events = []
    
    # 添加阅读动态
    sessions = db.query(ReadingSession, User, Chapter, Work).join(
        User, ReadingSession.user_id == User.id
    ).join(
        Chapter, ReadingSession.chapter_id == Chapter.id
    ).join(
        Work, ReadingSession.work_id == Work.id
    ).filter(
        ReadingSession.user_id.in_(following_ids)
    ).order_by(desc(ReadingSession.session_date)).limit(page_size).all()
    
    for s, u, c, w in sessions:
        events.append({
            "type": "reading",
            "user": {"id": u.id, "username": u.username, "avatar": u.avatar},
            "work": {"id": w.id, "title": w.title},
            "chapter": {"id": c.id, "title": c.title},
            "content": f"在阅读《{w.title}》- {c.title}",
            "created_at": s.session_date.isoformat()
        })
    
    # 添加书评动态
    reviews = db.query(Review, User, Work).join(
        User, Review.user_id == User.id
    ).join(
        Work, Review.work_id == Work.id
    ).filter(
        Review.user_id.in_(following_ids)
    ).order_by(desc(Review.created_at)).limit(page_size).all()
    
    for r, u, w in reviews:
        events.append({
            "type": "review",
            "user": {"id": u.id, "username": u.username, "avatar": u.avatar},
            "work": {"id": w.id, "title": w.title},
            "content": f"对《{w.title}》发表了{'长评' if r.is_long else '短评'}：{r.content[:100]}",
            "rating": r.rating,
            "created_at": r.created_at.isoformat()
        })
    
    # 书架动态
    shelves = db.query(Bookshelf, User, Work).join(
        User, Bookshelf.user_id == User.id
    ).join(
        Work, Bookshelf.work_id == Work.id
    ).filter(
        Bookshelf.user_id.in_(following_ids)
    ).order_by(desc(Bookshelf.created_at)).limit(page_size).all()
    
    for s, u, w in shelves:
        events.append({
            "type": "bookshelf",
            "user": {"id": u.id, "username": u.username, "avatar": u.avatar},
            "work": {"id": w.id, "title": w.title},
            "content": f"将《{w.title}》加入了书架",
            "created_at": s.created_at.isoformat()
        })
    
    # 按时间排序
    events.sort(key=lambda e: e["created_at"], reverse=True)
    
    return events[:page_size]


@router.get("/profile/{user_id}", response_model=UserProfileResponse)
def get_user_profile(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户主页信息"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    is_following = db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.following_id == user_id
    ).count() > 0
    
    return _user_to_profile(db, user, current_user.id, is_following)


def _user_to_profile(db: Session, user: User, current_id: int, is_following: bool = False) -> UserProfileResponse:
    """构建用户主页响应"""
    follower_count = db.query(Follow).filter(Follow.following_id == user.id).count()
    following_count = db.query(Follow).filter(Follow.follower_id == user.id).count()
    review_count = db.query(Review).filter(Review.user_id == user.id).count()
    
    return UserProfileResponse(
        id=user.id,
        username=user.username,
        avatar=user.avatar,
        follower_count=follower_count,
        following_count=following_count,
        review_count=review_count,
        is_following=is_following,
        created_at=user.created_at
    )
