"""初始化支付套餐数据"""
from app.core.database import SessionLocal
from app.models.models import PaymentPlan


def seed_payment_plans():
    """创建默认支付套餐"""
    db = SessionLocal()
    
    try:
        # 检查是否已有套餐
        existing = db.query(PaymentPlan).first()
        if existing:
            print("支付套餐已存在，跳过初始化")
            return
        
        # 创建默认套餐
        plans = [
            PaymentPlan(
                name="月度VIP",
                price=30.00,
                duration_days=30,
                description="有效期30天，享受VIP专属章节和功能",
                is_active=True
            ),
            PaymentPlan(
                name="季度VIP",
                price=80.00,
                duration_days=90,
                description="有效期90天，享受VIP专属章节和功能，赠送月票",
                is_active=True
            ),
            PaymentPlan(
                name="年度VIP",
                price=288.00,
                duration_days=365,
                description="有效期365天，享受VIP专属章节和功能，赠送更多月票",
                is_active=True
            ),
        ]
        
        for plan in plans:
            db.add(plan)
        
        db.commit()
        print(f"成功创建 {len(plans)} 个支付套餐")
        
    except Exception as e:
        print(f"初始化支付套餐失败: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_payment_plans()