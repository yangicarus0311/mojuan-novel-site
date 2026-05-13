from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from app.models.models import WorkStatus


# User schemas
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    avatar: str
    is_admin: int
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


# Work schemas
class WorkBase(BaseModel):
    title: str
    author: str
    description: Optional[str] = None
    cover_url: Optional[str] = None
    category: str
    status: WorkStatus = WorkStatus.ongoing


class WorkCreate(WorkBase):
    pass


class WorkResponse(WorkBase):
    id: int
    word_count: int
    clicks: int
    favorites: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WorkListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    works: List[WorkResponse]


# Chapter schemas
class ChapterBase(BaseModel):
    volume_id: int = 1
    chapter_number: int
    title: str
    content: Optional[str] = None


class ChapterCreate(ChapterBase):
    pass


class ChapterResponse(ChapterBase):
    id: int
    work_id: int
    word_count: int
    created_at: datetime
    is_vip: bool = False

    class Config:
        from_attributes = True


class ChapterListResponse(BaseModel):
    total: int
    chapters: List[ChapterResponse]


# Bookshelf schemas
class BookshelfCreate(BaseModel):
    work_id: int


class BookshelfResponse(BaseModel):
    id: int
    work: WorkResponse
    created_at: datetime

    class Config:
        from_attributes = True


# Read Progress schemas
class ReadProgressUpdate(BaseModel):
    chapter_id: int
    progress: int = 0


class ReadProgressResponse(BaseModel):
    id: int
    work_id: int
    chapter_id: int
    progress: int
    updated_at: datetime

    class Config:
        from_attributes = True


# Search
class SearchResponse(BaseModel):
    total: int
    works: List[WorkResponse]


# ==================== 支付相关 Schema ====================


class PaymentPlanBase(BaseModel):
    name: str
    price: float
    duration_days: int
    description: Optional[str] = None


class PaymentPlanCreate(PaymentPlanBase):
    pass


class PaymentPlanSchema(PaymentPlanBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class SubscriptionBase(BaseModel):
    user_id: int
    plan_id: int
    status: str
    start_date: datetime
    end_date: datetime
    auto_renew: bool


class SubscriptionCreate(SubscriptionBase):
    pass


class SubscriptionSchema(SubscriptionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    order_no: str
    user_id: int
    order_type: str
    amount: float
    status: str
    payment_method: Optional[str] = None


class OrderCreate(OrderBase):
    pass


class OrderSchema(OrderBase):
    id: int
    payment_time: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class BalanceSchema(BaseModel):
    balance: float
    total_recharge: float


class MonthlyTicketBase(BaseModel):
    user_id: int
    work_id: int
    ticket_count: int


class MonthlyTicketCreate(MonthlyTicketBase):
    pass


class MonthlyTicketSchema(MonthlyTicketBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class SubscriptionStatusResponse(BaseModel):
    is_vip: bool
    expire_date: Optional[datetime] = None
    plan_name: Optional[str] = None


class WorkPriceSchema(BaseModel):
    id: int
    work_id: int
    chapter_price: float
    is_premium: bool

    class Config:
        from_attributes = True


# ==================== 阅读体验 Schema ====================


class HighlightCreate(BaseModel):
    chapter_id: int
    content: str
    note: str = ""
    color: str = "yellow"
    location_start: int = 0
    location_end: int = 0


class HighlightUpdate(BaseModel):
    note: Optional[str] = None
    color: Optional[str] = None


class HighlightResponse(BaseModel):
    id: int
    user_id: int
    work_id: int
    chapter_id: int
    content: str
    note: str
    color: str
    location_start: int
    location_end: int
    page_url: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReadingSessionHeartbeat(BaseModel):
    work_id: int
    chapter_id: int
    duration_seconds: int
    chars_read: int


class DailyStatsResponse(BaseModel):
    date: str
    duration_minutes: int
    chars_read: int
    works_read: int


class ReadingStatsResponse(BaseModel):
    total_duration_minutes: int
    total_chars: int
    total_works: int
    daily_stats: List[DailyStatsResponse]
    streak_days: int
    today_minutes: int


# ==================== 社交 Schema ====================


class FollowResponse(BaseModel):
    id: int
    follower_id: int
    following_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserProfileResponse(BaseModel):
    id: int
    username: str
    avatar: str
    bio: str = ""
    follower_count: int = 0
    following_count: int = 0
    review_count: int = 0
    is_following: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class ReviewCreate(BaseModel):
    work_id: int
    rating: int = 5
    title: str = ""
    content: str
    is_long: int = 0


class ReviewResponse(BaseModel):
    id: int
    user_id: int
    work_id: int
    rating: int
    title: str
    content: str
    is_long: int
    likes: int
    is_liked: bool = False
    username: str = ""
    user_avatar: str = ""
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
