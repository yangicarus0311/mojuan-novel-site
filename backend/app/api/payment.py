from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
import uuid

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.models import (
    PaymentPlan, UserSubscription, WorkPrice, Order, UserBalance, MonthlyTicket,
    SubscriptionStatus, OrderType, OrderStatus, User
)
from app.schemas.schemas import (
    PaymentPlanSchema, SubscriptionSchema, OrderSchema, 
    BalanceSchema, MonthlyTicketSchema, SubscriptionStatusResponse
)
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/payment", tags=["payment"])


@router.get("/plans", response_model=List[PaymentPlanSchema])
def get_payment_plans(db: Session = Depends(get_db)):
    """获取所有付费套餐"""
    return PaymentService.get_payment_plans(db)


@router.post("/subscribe")
def subscribe(
    plan_id: int,
    payment_method: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """用户订阅VIP套餐"""
    raise HTTPException(status_code=503, detail="会员开通暂不可用，支付服务尚未开放")


@router.get("/subscription/status", response_model=SubscriptionStatusResponse)
def get_subscription_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户订阅状态"""
    user_id = current_user.id
    return PaymentService.get_user_subscription_status(db, user_id)


@router.post("/chapter/purchase")
def purchase_chapter(
    work_id: int,
    chapter_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """购买单章"""
    user_id = current_user.id
    
    try:
        result = PaymentService.purchase_chapter(db, user_id, work_id, chapter_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/recharge")
def recharge_balance(
    amount: float,
    payment_method: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """用户充值余额"""
    raise HTTPException(status_code=503, detail="充值暂不可用，支付服务尚未开放")


@router.get("/balance", response_model=BalanceSchema)
def get_balance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户余额"""
    user_id = current_user.id
    return PaymentService.get_user_balance(db, user_id)


@router.post("/ticket/vote")
def vote_monthly_ticket(
    work_id: int,
    ticket_count: int = 1,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """投月票"""
    user_id = current_user.id
    
    try:
        result = PaymentService.vote_monthly_ticket(db, user_id, work_id, ticket_count)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/capabilities")
def payment_capabilities():
    return {"external_payments_enabled": False, "message": "充值和会员开通暂未开放，已有会员与余额可继续使用。"}
