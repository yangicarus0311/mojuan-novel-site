from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
import uuid

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.models import (
    PaymentPlan, UserSubscription, WorkPrice, Order, UserBalance, MonthlyTicket,
    SubscriptionStatus, OrderType, OrderStatus
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
    current_user: dict = Depends(get_current_user)
):
    """用户订阅VIP套餐"""
    user_id = current_user["id"]
    
    try:
        result = PaymentService.create_subscription(db, user_id, plan_id, payment_method)
        return {
            **result,
            "payment_url": f"/payment/process/{result['order_no']}"  # 实际项目中这里应该是第三方支付链接
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/subscription/status", response_model=SubscriptionStatusResponse)
def get_subscription_status(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取用户订阅状态"""
    user_id = current_user["id"]
    return PaymentService.get_user_subscription_status(db, user_id)


@router.post("/chapter/purchase")
def purchase_chapter(
    work_id: int,
    chapter_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """购买单章"""
    user_id = current_user["id"]
    
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
    current_user: dict = Depends(get_current_user)
):
    """用户充值余额"""
    user_id = current_user["id"]
    
    try:
        result = PaymentService.recharge_balance(db, user_id, amount, payment_method)
        return {
            **result,
            "payment_url": f"/payment/process/{result['order_no']}"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/balance", response_model=BalanceSchema)
def get_balance(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取用户余额"""
    user_id = current_user["id"]
    return PaymentService.get_user_balance(db, user_id)


@router.post("/ticket/vote")
def vote_monthly_ticket(
    work_id: int,
    ticket_count: int = 1,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """投月票"""
    user_id = current_user["id"]
    
    try:
        result = PaymentService.vote_monthly_ticket(db, user_id, work_id, ticket_count)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/webhook/payment")
def payment_webhook(
    order_no: str,
    status: str,
    db: Session = Depends(get_db)
):
    """支付回调（实际项目中用于接收第三方支付回调）"""
    try:
        result = PaymentService.process_payment_success(db, order_no)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))