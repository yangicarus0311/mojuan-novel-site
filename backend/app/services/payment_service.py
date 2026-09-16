"""Payment services for handling payment logic"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from datetime import datetime, timedelta
from app.models.models import (
    PaymentPlan, UserSubscription, WorkPrice, Order, UserBalance, MonthlyTicket,
    SubscriptionStatus, OrderType, OrderStatus, User, Chapter, ChapterPurchase
)
from app.schemas.schemas import (
    PaymentPlanSchema, SubscriptionSchema, OrderSchema, 
    BalanceSchema, MonthlyTicketSchema, SubscriptionStatusResponse
)
from typing import Optional, List
import uuid


class PaymentService:
    """支付服务类"""
    
    @staticmethod
    def get_payment_plans(db: Session) -> List[PaymentPlan]:
        """获取所有有效的支付套餐"""
        return db.query(PaymentPlan).filter(PaymentPlan.is_active == True).all()
    
    @staticmethod
    def get_payment_plan(db: Session, plan_id: int) -> Optional[PaymentPlan]:
        """获取单个支付套餐"""
        return db.query(PaymentPlan).filter(
            PaymentPlan.id == plan_id, 
            PaymentPlan.is_active == True
        ).first()
    
    @staticmethod
    def create_subscription(db: Session, user_id: int, plan_id: int, payment_method: str) -> dict:
        raise ValueError("会员开通暂不可用，支付服务尚未开放")

    @staticmethod
    def get_user_subscription_status(db: Session, user_id: int) -> SubscriptionStatusResponse:
        """获取用户订阅状态"""
        subscription = db.query(UserSubscription).filter(
            UserSubscription.user_id == user_id,
            UserSubscription.status == SubscriptionStatus.active
        ).order_by(UserSubscription.end_date.desc()).first()
        
        if not subscription:
            return SubscriptionStatusResponse(is_vip=False)
        
        is_expired = subscription.end_date < datetime.now()
        if is_expired:
            subscription.status = SubscriptionStatus.expired
            db.commit()
            return SubscriptionStatusResponse(is_vip=False)
        
        return SubscriptionStatusResponse(
            is_vip=True,
            expire_date=subscription.end_date,
            plan_name=db.query(PaymentPlan).filter(PaymentPlan.id == subscription.plan_id).one().name
        )
    
    @staticmethod
    def purchase_chapter(db: Session, user_id: int, work_id: int, chapter_id: int) -> dict:
        chapter = db.query(Chapter).filter(Chapter.id == chapter_id, Chapter.work_id == work_id).first()
        if not chapter:
            raise ValueError("章节不存在或不属于该作品")
        existing = db.query(ChapterPurchase).filter_by(user_id=user_id, chapter_id=chapter_id).first()
        if existing:
            order = db.query(Order).filter_by(id=existing.order_id, status=OrderStatus.paid).first()
            if order:
                return {"success": True, "order_no": order.order_no, "already_purchased": True}
            raise ValueError("该购买记录状态异常，请联系管理员")
        if PaymentService.check_user_vip_status(db, user_id):
            return {"success": True, "already_accessible": True}
        price = db.query(WorkPrice).filter_by(work_id=work_id).first()
        if price and price.is_premium:
            raise ValueError("该章节仅限有效会员阅读")
        if not price or price.chapter_price <= 0:
            raise ValueError("该章节可免费阅读，无需购买")
        # Conditional UPDATE prevents concurrent requests from overspending.
        try:
            changed = db.query(UserBalance).filter(
                UserBalance.user_id == user_id, UserBalance.balance >= price.chapter_price
            ).update({UserBalance.balance: UserBalance.balance - price.chapter_price}, synchronize_session=False)
            if changed != 1:
                db.rollback()
                # A concurrent retry may have already paid for this same chapter.
                receipt = db.query(ChapterPurchase).filter_by(user_id=user_id, chapter_id=chapter_id).first()
                if receipt:
                    paid_order = db.query(Order).filter_by(id=receipt.order_id, user_id=user_id, status=OrderStatus.paid).first()
                    if paid_order:
                        return {"success": True, "order_no": paid_order.order_no, "already_purchased": True}
                raise ValueError("余额不足")
            order = Order(order_no=str(uuid.uuid4()), user_id=user_id, order_type=OrderType.chapter,
                amount=price.chapter_price, status=OrderStatus.paid, payment_method="balance", payment_time=datetime.now())
            db.add(order)
            db.flush()
            db.add(ChapterPurchase(user_id=user_id, chapter_id=chapter_id, order_id=order.id))
            order_no = order.order_no
            db.commit()
            return {"success": True, "order_no": order_no}
        except IntegrityError:
            # The unique user/chapter receipt also makes concurrent retries idempotent.
            db.rollback()
            receipt = db.query(ChapterPurchase).filter_by(user_id=user_id, chapter_id=chapter_id).first()
            if receipt:
                order = db.query(Order).filter_by(id=receipt.order_id, status=OrderStatus.paid).first()
                if order:
                    return {"success": True, "order_no": order.order_no, "already_purchased": True}
            raise ValueError("购买未完成，请重试")

    @staticmethod
    def recharge_balance(db: Session, user_id: int, amount: float, payment_method: str) -> dict:
        raise ValueError("充值暂不可用，支付服务尚未开放")

    @staticmethod
    def get_or_create_user_balance(db: Session, user_id: int) -> UserBalance:
        """获取或创建用户余额记录"""
        user_balance = db.query(UserBalance).filter(UserBalance.user_id == user_id).first()
        if not user_balance:
            user_balance = UserBalance(user_id=user_id)
            db.add(user_balance)
            db.commit()
            db.refresh(user_balance)
        return user_balance
    
    @staticmethod
    def get_user_balance(db: Session, user_id: int) -> BalanceSchema:
        """获取用户余额信息"""
        user_balance = PaymentService.get_or_create_user_balance(db, user_id)
        return BalanceSchema(
            balance=float(user_balance.balance),
            total_recharge=float(user_balance.total_recharge)
        )
    
    @staticmethod
    def vote_monthly_ticket(
        db: Session, 
        user_id: int, 
        work_id: int, 
        ticket_count: int = 1
    ) -> dict:
        """投月票"""
        if ticket_count <= 0 or ticket_count > 100:
            raise ValueError("投票数量不合法")
        
        # 检查用户是否有足够的月票（简化处理）
        # 实际项目中应该有月票获取和消耗的逻辑
        
        ticket = MonthlyTicket(
            user_id=user_id,
            work_id=work_id,
            ticket_count=ticket_count
        )
        db.add(ticket)
        db.commit()
        
        return {"success": True, "ticket_count": ticket_count}
    
    @staticmethod
    def process_payment_success(db: Session, order_no: str):
        raise ValueError("未配置可信支付渠道，禁止修改订单支付状态")

    @staticmethod
    def check_user_vip_status(db: Session, user_id: int) -> bool:
        """检查用户是否为VIP"""
        subscription = db.query(UserSubscription).filter(
            UserSubscription.user_id == user_id,
            UserSubscription.status == SubscriptionStatus.active,
            UserSubscription.end_date > datetime.now()
        ).first()
        
        return subscription is not None
    
    @staticmethod
    def check_chapter_access(db: Session, user_id: int, work_id: int, chapter_id: int) -> bool:
        if not db.query(Chapter.id).filter_by(id=chapter_id, work_id=work_id).first():
            return False
        if PaymentService.check_user_vip_status(db, user_id):
            return True
        price = db.query(WorkPrice).filter_by(work_id=work_id).first()
        if not price:
            return True
        if price.is_premium:
            return False
        if price.chapter_price <= 0:
            return True
        return db.query(ChapterPurchase).join(Order, Order.id == ChapterPurchase.order_id).filter(
            ChapterPurchase.user_id == user_id, ChapterPurchase.chapter_id == chapter_id,
            Order.user_id == user_id, Order.status == OrderStatus.paid,
            Order.order_type == OrderType.chapter
        ).first() is not None

    @staticmethod
    def require_chapter_access(db: Session, user_id: int, chapter: Chapter):
        if PaymentService.check_chapter_access(db, user_id, chapter.work_id, chapter.id):
            return
        price = db.query(WorkPrice).filter_by(work_id=chapter.work_id).first()
        if price and price.is_premium:
            raise HTTPException(status_code=403, detail="该章节需要有效的 VIP 会员")
        raise HTTPException(status_code=402, detail="请先购买该章节")
