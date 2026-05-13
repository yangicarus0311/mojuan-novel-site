"""Payment services for handling payment logic"""
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models.models import (
    PaymentPlan, UserSubscription, WorkPrice, Order, UserBalance, MonthlyTicket,
    SubscriptionStatus, OrderType, OrderStatus, User
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
    def create_subscription(
        db: Session, 
        user_id: int, 
        plan_id: int, 
        payment_method: str
    ) -> dict:
        """创建订阅订单"""
        plan = PaymentService.get_payment_plan(db, plan_id)
        if not plan:
            raise ValueError("套餐不存在")
        
        # 检查用户是否已有有效订阅
        existing_sub = db.query(UserSubscription).filter(
            UserSubscription.user_id == user_id,
            UserSubscription.status == SubscriptionStatus.active,
            UserSubscription.end_date > datetime.now()
        ).first()
        if existing_sub:
            raise ValueError("您已有有效的订阅")
        
        # 创建订单
        order_no = str(uuid.uuid4())
        order = Order(
            order_no=order_no,
            user_id=user_id,
            order_type=OrderType.subscription,
            amount=plan.price,
            payment_method=payment_method,
            status=OrderStatus.pending
        )
        db.add(order)
        db.commit()
        db.refresh(order)
        
        return {
            "order_no": order_no,
            "amount": plan.price,
            "payment_method": payment_method
        }
    
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
            plan_name=subscription.plan.name
        )
    
    @staticmethod
    def purchase_chapter(
        db: Session, 
        user_id: int, 
        work_id: int, 
        chapter_id: int
    ) -> dict:
        """购买单章"""
        # 检查作品价格
        work_price = db.query(WorkPrice).filter(WorkPrice.work_id == work_id).first()
        if not work_price or work_price.chapter_price <= 0:
            raise ValueError("该作品不支持单章购买")
        
        # 检查用户余额
        user_balance = PaymentService.get_or_create_user_balance(db, user_id)
        if user_balance.balance < work_price.chapter_price:
            raise ValueError("余额不足，请先充值")
        
        # 创建订单
        order_no = str(uuid.uuid4())
        order = Order(
            order_no=order_no,
            user_id=user_id,
            order_type=OrderType.chapter,
            amount=work_price.chapter_price,
            status=OrderStatus.paid,
            payment_method="balance"
        )
        db.add(order)
        
        # 扣除余额
        user_balance.balance -= work_price.chapter_price
        db.commit()
        
        return {"success": True, "order_no": order_no}
    
    @staticmethod
    def recharge_balance(
        db: Session, 
        user_id: int, 
        amount: float, 
        payment_method: str
    ) -> dict:
        """充值余额"""
        if amount <= 0 or amount > 10000:
            raise ValueError("充值金额不合法")
        
        # 创建订单
        order_no = str(uuid.uuid4())
        order = Order(
            order_no=order_no,
            user_id=user_id,
            order_type=OrderType.subscription,
            amount=amount,
            payment_method=payment_method,
            status=OrderStatus.pending
        )
        db.add(order)
        db.commit()
        
        return {
            "order_no": order_no,
            "amount": amount,
            "payment_method": payment_method
        }
    
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
        """处理支付成功回调"""
        order = db.query(Order).filter(Order.order_no == order_no).first()
        if not order:
            raise ValueError("订单不存在")
        
        if order.status == OrderStatus.paid:
            return {"success": True}  # 已经处理过
        
        order.status = OrderStatus.paid
        order.payment_time = datetime.now()
        
        # 处理订单业务逻辑
        if order.order_type == OrderType.subscription:
            # 处理订阅
            # 这里需要找到对应的套餐信息（简化处理）
            pass
        
        db.commit()
        return {"success": True}
    
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
    def check_chapter_access(
        db: Session, 
        user_id: int, 
        work_id: int, 
        chapter_id: int
    ) -> bool:
        """检查用户是否有权限访问章节"""
        # 检查是否为VIP专属章节
        work_price = db.query(WorkPrice).filter(WorkPrice.work_id == work_id).first()
        if work_price and work_price.is_premium:
            # 需要VIP权限
            is_vip = PaymentService.check_user_vip_status(db, user_id)
            if not is_vip:
                return False
        
        # 检查是否为付费章节
        if work_price and work_price.chapter_price > 0:
            # 检查用户是否已购买
            order = db.query(Order).filter(
                Order.user_id == user_id,
                Order.order_type == OrderType.chapter,
                Order.status == OrderStatus.paid
            ).first()
            if not order:
                # 检查用户余额是否足够
                user_balance = PaymentService.get_user_balance(db, user_id)
                if user_balance.balance < work_price.chapter_price:
                    return False
        
        return True