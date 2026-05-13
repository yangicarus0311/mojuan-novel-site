from fastapi import APIRouter, Depends, HTTPException, Header, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import hmac
import hashlib
import json

from app.core.database import get_db
from app.models.models import (
    PaymentPlan, UserSubscription, Order, UserBalance,
    SubscriptionStatus, OrderType, OrderStatus
)
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/payment/webhook", tags=["payment"])


def verify_payment_signature(data: str, signature: str, secret_key: str) -> bool:
    """验证支付签名"""
    expected_signature = hmac.new(
        secret_key.encode(),
        data.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected_signature)


@router.post("/alipay")
async def alipay_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """支付宝支付回调"""
    form_data = await request.form()
    
    # 验证签名
    signature = form_data.get("sign", "")
    # 实际项目中应该从配置获取
    secret_key = "your_alipay_secret_key"
    
    # 构建待签名字符串
    sorted_params = sorted([(k, v) for k, v in form_data.items() if k != "sign" and v])
    data_str = "&".join([f"{k}={v}" for k, v in sorted_params])
    
    if not verify_payment_signature(data_str, signature, secret_key):
        raise HTTPException(status_code=400, detail="签名验证失败")
    
    # 处理支付结果
    trade_status = form_data.get("trade_status")
    out_trade_no = form_data.get("out_trade_no")
    
    if trade_status == "TRADE_SUCCESS":
        try:
            result = PaymentService.process_payment_success(db, out_trade_no)
            return {"success": True}
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    raise HTTPException(status_code=400, detail="支付未成功")


@router.post("/wechat")
async def wechat_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """微信支付回调"""
    xml_data = await request.body()
    # 解析XML数据（简化处理）
    
    # 实际项目中应该：
    # 1. 验证签名
    # 2. 解析订单信息
    # 3. 处理支付结果
    
    return {"return_code": "SUCCESS", "return_msg": "OK"}


@router.post("/balance")
def balance_webhook(
    order_no: str,
    db: Session = Depends(get_db)
):
    """余额支付回调（内部调用）"""
    try:
        result = PaymentService.process_payment_success(db, order_no)
        return {"success": True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/test/success")
def test_payment_success(
    order_no: str,
    db: Session = Depends(get_db)
):
    """测试支付成功回调（仅用于测试环境）"""
    try:
        result = PaymentService.process_payment_success(db, order_no)
        return {"success": True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))