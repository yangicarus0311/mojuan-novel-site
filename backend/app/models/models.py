from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum, DECIMAL, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class WorkStatus(str, enum.Enum):
    ongoing = "ongoing"
    completed = "completed"
    paused = "paused"


class SubscriptionStatus(str, enum.Enum):
    active = "active"
    expired = "expired"
    cancelled = "cancelled"


class OrderType(str, enum.Enum):
    subscription = "subscription"
    chapter = "chapter"
    donation = "donation"


class OrderStatus(str, enum.Enum):
    pending = "pending"
    paid = "paid"
    failed = "failed"
    refunded = "refunded"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    avatar = Column(String(255), default="/uploads/avatars/default.png")
    is_admin = Column(Integer, default=0)  # 1 = admin, 0 = normal user
    created_at = Column(DateTime, server_default=func.now())

    bookshelf = relationship("Bookshelf", back_populates="user")
    read_progress = relationship("ReadProgress", back_populates="user")


class Work(Base):
    __tablename__ = "works"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    author = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    cover_url = Column(String(255), default="/uploads/covers/default.png")
    category = Column(String(50), nullable=False, index=True)
    status = Column(SQLEnum(WorkStatus), default=WorkStatus.ongoing)
    word_count = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    favorites = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    chapters = relationship("Chapter", back_populates="work", order_by="Chapter.chapter_number")
    bookshelf = relationship("Bookshelf", back_populates="work")
    read_progress = relationship("ReadProgress", back_populates="work")


class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True, index=True)
    work_id = Column(Integer, ForeignKey("works.id"), nullable=False, index=True)
    volume_id = Column(Integer, default=1)
    chapter_number = Column(Integer, nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text)
    word_count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())

    work = relationship("Work", back_populates="chapters")
    read_progress = relationship("ReadProgress", back_populates="chapter")


class Bookshelf(Base):
    __tablename__ = "bookshelf"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    work_id = Column(Integer, ForeignKey("works.id"), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="bookshelf")
    work = relationship("Work", back_populates="bookshelf")


class ReadProgress(Base):
    __tablename__ = "read_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    work_id = Column(Integer, ForeignKey("works.id"), nullable=False, index=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False)
    progress = Column(Integer, default=0)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="read_progress")
    work = relationship("Work", back_populates="read_progress")
    chapter = relationship("Chapter", back_populates="read_progress")


# ==================== 付费功能相关模型 ====================


class PaymentPlan(Base):
    __tablename__ = "payment_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)  # 套餐名称：月度VIP、季度VIP、年度VIP
    price = Column(DECIMAL(10, 2), nullable=False)  # 价格
    duration_days = Column(Integer, nullable=False)  # 有效期天数
    description = Column(Text)  # 套餐描述
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())


class UserSubscription(Base):
    __tablename__ = "user_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    plan_id = Column(Integer, ForeignKey("payment_plans.id"), nullable=False)
    status = Column(SQLEnum(SubscriptionStatus), default=SubscriptionStatus.active)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    auto_renew = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())


class WorkPrice(Base):
    __tablename__ = "work_prices"

    id = Column(Integer, primary_key=True, index=True)
    work_id = Column(Integer, ForeignKey("works.id"), nullable=False, unique=True)
    chapter_price = Column(DECIMAL(10, 2), default=0.00)  # 单章价格
    is_premium = Column(Boolean, default=False)  # 是否VIP专属


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_no = Column(String(50), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    order_type = Column(SQLEnum(OrderType), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.pending)
    payment_method = Column(String(20))
    payment_time = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())


class UserBalance(Base):
    __tablename__ = "user_balances"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    balance = Column(DECIMAL(10, 2), default=0.00)
    total_recharge = Column(DECIMAL(10, 2), default=0.00)
    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())


class MonthlyTicket(Base):
    __tablename__ = "monthly_tickets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    work_id = Column(Integer, ForeignKey("works.id"), nullable=False, index=True)
    ticket_count = Column(Integer, default=1)
    created_at = Column(DateTime, server_default=func.now())


# ==================== 阅读体验相关模型 ====================


class HighlightColor(str, enum.Enum):
    yellow = "yellow"
    green = "green"
    blue = "blue"
    pink = "pink"
    orange = "orange"


class Highlight(Base):
    """划线/想法模型"""
    __tablename__ = "highlights"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    work_id = Column(Integer, ForeignKey("works.id"), nullable=False, index=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)  # 被划线的文本内容
    note = Column(Text, default="")  # 想法/笔记
    color = Column(SQLEnum(HighlightColor), default=HighlightColor.yellow)
    location_start = Column(Integer, default=0)  # 起始位置(字符偏移)
    location_end = Column(Integer, default=0)  # 结束位置
    page_url = Column(String(500), default="")  # 跳转链接
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", backref="highlights")
    work = relationship("Work", backref="highlights")
    chapter = relationship("Chapter", backref="highlights")


class ReadingSession(Base):
    """阅读会话/统计模型"""
    __tablename__ = "reading_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    work_id = Column(Integer, ForeignKey("works.id"), nullable=False, index=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False)
    duration_seconds = Column(Integer, default=0)  # 本次阅读时长
    chars_read = Column(Integer, default=0)  # 本次阅读字数
    session_date = Column(DateTime, server_default=func.now())

    user = relationship("User", backref="reading_sessions")
    work = relationship("Work", backref="reading_sessions")
    chapter = relationship("Chapter", backref="reading_sessions")


class Follow(Base):
    """关注关系模型"""
    __tablename__ = "follows"

    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)  # 关注者
    following_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)  # 被关注者
    created_at = Column(DateTime, server_default=func.now())


class Review(Base):
    """书评模型"""
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    work_id = Column(Integer, ForeignKey("works.id"), nullable=False, index=True)
    rating = Column(Integer, default=5)  # 1-5 星
    title = Column(String(200), default="")
    content = Column(Text, nullable=False)
    is_long = Column(Integer, default=0)  # 1=长评, 0=短评
    likes = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", backref="reviews")
    work = relationship("Work", backref="reviews")


class ReviewLike(Base):
    """书评点赞"""
    __tablename__ = "review_likes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    review_id = Column(Integer, ForeignKey("reviews.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (UniqueConstraint("user_id", "review_id", name="uq_review_like"),)
