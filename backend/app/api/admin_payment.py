from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.models import (
    PaymentPlan, UserSubscription, Order, UserBalance, MonthlyTicket,
    SubscriptionStatus, OrderStatus, OrderType, Work, WorkPrice, User
)
from app.schemas.schemas import (
    PaymentPlanSchema, SubscriptionSchema, OrderSchema, 
    BalanceSchema, MonthlyTicketSchema, WorkPriceSchema
)

router = APIRouter(prefix="/admin/payment", tags=["admin"])


@router.get("/plans", response_model=List[PaymentPlanSchema])
def admin_get_payment_plans(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """管理后台：获取所有支付套餐"""
    if current_user.is_admin != 1:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    return db.query(PaymentPlan).all()


@router.post("/plans", response_model=PaymentPlanSchema)
def admin_create_payment_plan(
    plan_data: PaymentPlanSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """管理后台：创建支付套餐"""
    if current_user.is_admin != 1:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    # 检查套餐名称是否已存在
    existing = db.query(PaymentPlan).filter(PaymentPlan.name == plan_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="套餐名称已存在")
    
    plan = PaymentPlan(
        name=plan_data.name,
        price=plan_data.price,
        duration_days=plan_data.duration_days,
        description=plan_data.description,
        is_active=plan_data.is_active
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@router.put("/plans/{plan_id}", response_model=PaymentPlanSchema)
def admin_update_payment_plan(
    plan_id: int,
    plan_data: PaymentPlanSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """管理后台：更新支付套餐"""
    if current_user.is_admin != 1:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    plan = db.query(PaymentPlan).filter(PaymentPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="套餐不存在")
    
    # 更新字段
    if plan_data.name is not None:
        plan.name = plan_data.name
    if plan_data.price is not None:
        plan.price = plan_data.price
    if plan_data.duration_days is not None:
        plan.duration_days = plan_data.duration_days
    if plan_data.description is not None:
        plan.description = plan_data.description
    if plan_data.is_active is not None:
        plan.is_active = plan_data.is_active
    
    db.commit()
    db.refresh(plan)
    return plan


@router.get("/orders", response_model=List[OrderSchema])
def admin_get_orders(
    status: Optional[str] = Query(None),
    order_type: Optional[str] = Query(None),
    user_id: Optional[int] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """管理后台：获取订单列表（支持筛选）"""
    if current_user.is_admin != 1:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    query = db.query(Order)
    
    # 筛选条件
    if status:
        query = query.filter(Order.status == status)
    if order_type:
        query = query.filter(Order.order_type == order_type)
    if user_id:
        query = query.filter(Order.user_id == user_id)
    if start_date:
        query = query.filter(Order.created_at >= start_date)
    if end_date:
        query = query.filter(Order.created_at <= end_date)
    
    return query.order_by(Order.created_at.desc()).all()


@router.get("/orders/{order_id}", response_model=OrderSchema)
def admin_get_order_detail(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """管理后台：获取订单详情"""
    if current_user.is_admin != 1:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    return order


@router.get("/stats/revenue")
def admin_get_revenue_stats(
    period: str = "day",  # day, week, month, year
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """管理后台：获取收入统计"""
    if current_user.is_admin != 1:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    from sqlalchemy import func
    
    # 根据时间周期筛选
    now = datetime.now()
    if period == "day":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "week":
        start_date = now - timedelta(days=7)
    elif period == "month":
        start_date = now - timedelta(days=30)
    elif period == "year":
        start_date = now - timedelta(days=365)
    else:
        start_date = now
    
    # 统计已支付订单
    paid_orders = db.query(Order).filter(
        Order.status == OrderStatus.paid,
        Order.created_at >= start_date
    ).all()
    
    total_revenue = sum(order.amount for order in paid_orders)
    order_count = len(paid_orders)
    
    # 按类型统计
    type_stats = {}
    for order in paid_orders:
        order_type = order.order_type.value
        if order_type not in type_stats:
            type_stats[order_type] = {"count": 0, "revenue": 0}
        type_stats[order_type]["count"] += 1
        type_stats[order_type]["revenue"] += order.amount
    
    return {
        "period": period,
        "start_date": start_date,
        "end_date": now,
        "total_revenue": total_revenue,
        "order_count": order_count,
        "type_stats": type_stats
    }


@router.get("/stats/users")
def admin_get_user_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """管理后台：获取用户付费统计"""
    if current_user.is_admin != 1:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    # 统计VIP用户数
    vip_users = db.query(UserSubscription).filter(
        UserSubscription.status == SubscriptionStatus.active,
        UserSubscription.end_date > datetime.now()
    ).count()
    
    # 统计有消费记录的用户
    paying_users = db.query(Order).filter(
        Order.status == OrderStatus.paid
    ).distinct(Order.user_id).count()
    
    # 按VIP等级统计
    from sqlalchemy import func
    vip_level_stats = db.query(
        UserSubscription.plan_id,
        func.count(UserSubscription.id).label("user_count")
    ).filter(
        UserSubscription.status == SubscriptionStatus.active,
        UserSubscription.end_date > datetime.now()
    ).group_by(UserSubscription.plan_id).all()
    
    return {
        "total_users": db.query(User).count(),
        "vip_users": vip_users,
        "paying_users": paying_users,
        "vip_level_stats": [
            {
                "plan_id": stat.plan_id,
                "plan_name": db.query(PaymentPlan).filter(PaymentPlan.id == stat.plan_id).first().name,
                "user_count": stat.user_count
            }
            for stat in vip_level_stats
        ]
    }


@router.get("/work-prices", response_model=List[WorkPriceSchema])
def admin_get_work_prices(
    work_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """管理后台：获取作品价格设置"""
    if current_user.is_admin != 1:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    query = db.query(WorkPrice)
    if work_id:
        query = query.filter(WorkPrice.work_id == work_id)
    
    return query.all()


@router.put("/work-prices/{work_id}", response_model=WorkPriceSchema)
def admin_update_work_price(
    work_id: int,
    chapter_price: float = Query(0.0),
    is_premium: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """管理后台：更新作品价格设置"""
    if current_user.is_admin != 1:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    # 检查作品是否存在
    work = db.query(Work).filter(Work.id == work_id).first()
    if not work:
        raise HTTPException(status_code=404, detail="作品不存在")
    
    # 获取或创建价格记录
    work_price = db.query(WorkPrice).filter(WorkPrice.work_id == work_id).first()
    if not work_price:
        work_price = WorkPrice(work_id=work_id)
        db.add(work_price)
    
    work_price.chapter_price = chapter_price
    work_price.is_premium = is_premium
    
    db.commit()
    db.refresh(work_price)
    return work_price


@router.get("/monthly-tickets", response_model=List[MonthlyTicketSchema])
def admin_get_monthly_tickets(
    work_id: Optional[int] = Query(None),
    user_id: Optional[int] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """管理后台：获取月票记录"""
    if current_user.is_admin != 1:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    query = db.query(MonthlyTicket)
    
    if work_id:
        query = query.filter(MonthlyTicket.work_id == work_id)
    if user_id:
        query = query.filter(MonthlyTicket.user_id == user_id)
    if start_date:
        query = query.filter(MonthlyTicket.created_at >= start_date)
    if end_date:
        query = query.filter(MonthlyTicket.created_at <= end_date)
    
    return query.order_by(MonthlyTicket.created_at.desc()).all()


@router.get("/monthly-tickets/rankings")
def admin_get_monthly_ticket_rankings(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """管理后台：获取月票排行榜"""
    if current_user.is_admin != 1:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    from sqlalchemy import func
    
    # 统计每部作品的月票总数
    rankings = db.query(
        MonthlyTicket.work_id,
        func.sum(MonthlyTicket.ticket_count).label("total_tickets")
    ).group_by(MonthlyTicket.work_id).order_by(
        func.sum(MonthlyTicket.ticket_count).desc()
    ).limit(limit).all()
    
    # 获取作品信息
    result = []
    for rank in rankings:
        work = db.query(Work).filter(Work.id == rank.work_id).first()
        if work:
            result.append({
                "work_id": work.id,
                "work_title": work.title,
                "total_tickets": rank.total_tickets,
                "author": work.author
            })
    
    return result


