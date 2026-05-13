"""定时任务服务 - 处理订阅过期、到期提醒等自动化任务"""
from datetime import datetime, timedelta
from typing import List
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.database import SessionLocal
from app.models.models import (
    UserSubscription, User, Order, PaymentPlan,
    SubscriptionStatus, OrderStatus
)
from app.services.payment_service import PaymentService
from app.services.notification_service import notification_service

logger = logging.getLogger(__name__)


class CronService:
    """定时任务服务类"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.db = SessionLocal()
        
        # 添加定时任务
        self.add_subscription_expiration_check()
        self.add_subscription_expiring_reminder()
        self.add_monthly_ticket_distribution()
        self.add_monthly_statistics()
    
    def add_subscription_expiration_check(self):
        """订阅过期检查 - 每小时执行一次"""
        self.scheduler.add_job(
            self.check_subscription_expiration,
            trigger=CronTrigger(hour="*/1"),  # 每小时
            id="subscription_expiration_check",
            replace_existing=True
        )
    
    def add_subscription_expiring_reminder(self):
        """订阅到期提醒 - 每天执行一次"""
        self.scheduler.add_job(
            self.check_subscription_expiring,
            trigger=CronTrigger(day="*", hour="9"),  # 每天早上9点
            id="subscription_expiring_reminder",
            replace_existing=True
        )
    
    def add_monthly_ticket_distribution(self):
        """月票分配 - 每月1号执行"""
        self.scheduler.add_job(
            self.distribute_monthly_tickets,
            trigger=CronTrigger(day="1", hour="2"),  # 每月1号凌晨2点
            id="monthly_ticket_distribution",
            replace_existing=True
        )
    
    def add_monthly_statistics(self):
        """月度统计 - 每月1号执行"""
        self.scheduler.add_job(
            self.generate_monthly_statistics,
            trigger=CronTrigger(day="1", hour="3"),  # 每月1号凌晨3点
            id="monthly_statistics",
            replace_existing=True
        )
    
    def check_subscription_expiration(self):
        """检查订阅过期"""
        try:
            logger.info("开始检查订阅过期...")
            
            # 查找即将过期的订阅（24小时内）
            now = datetime.now()
            expire_soon = now + timedelta(hours=24)
            
            subscriptions = self.db.query(UserSubscription).filter(
                UserSubscription.status == SubscriptionStatus.active,
                UserSubscription.end_date <= expire_soon,
                UserSubscription.end_date > now
            ).all()
            
            for subscription in subscriptions:
                # 自动续费（如果开启自动续费）
                if subscription.auto_renew:
                    try:
                        self.auto_renew_subscription(subscription)
                    except Exception as e:
                        logger.error(f"自动续费失败: {e}")
            
            logger.info(f"订阅过期检查完成，处理了 {len(subscriptions)} 条记录")
            
        except Exception as e:
            logger.error(f"订阅过期检查失败: {e}")
    
    def check_subscription_expiring(self):
        """检查即将到期的订阅并发送提醒"""
        try:
            logger.info("开始检查即将到期的订阅...")
            
            # 查找3天后到期的订阅
            now = datetime.now()
            three_days_later = now + timedelta(days=3)
            
            subscriptions = self.db.query(UserSubscription).filter(
                UserSubscription.status == SubscriptionStatus.active,
                UserSubscription.end_date <= three_days_later,
                UserSubscription.end_date > now
            ).all()
            
            for subscription in subscriptions:
                user = self.db.query(User).filter(User.id == subscription.user_id).first()
                if user:
                    try:
                        notification_service.send_subscription_expiring(user, subscription, 3)
                    except Exception as e:
                        logger.error(f"发送到期提醒失败: {e}")
            
            logger.info(f"到期提醒检查完成，发送了 {len(subscriptions)} 条提醒")
            
        except Exception as e:
            logger.error(f"到期提醒检查失败: {e}")
    
    def auto_renew_subscription(self, subscription: UserSubscription):
        """自动续费订阅"""
        try:
            logger.info(f"自动续费: 用户 {subscription.user_id}, 套餐 {subscription.plan_id}")
            
            # 检查用户余额
            user_balance = self.db.query(UserBalance).filter(
                UserBalance.user_id == subscription.user_id
            ).first()
            
            if not user_balance or user_balance.balance < subscription.plan.price:
                logger.warning(f"用户 {subscription.user_id} 余额不足，无法自动续费")
                return
            
            # 扣除余额
            user_balance.balance -= subscription.plan.price
            
            # 创建续费订单
            order = Order(
                order_no=f"AUTO_{datetime.now().strftime('%Y%m%d%H%M%S')}_{subscription.user_id}",
                user_id=subscription.user_id,
                order_type=OrderType.subscription,
                amount=subscription.plan.price,
                status=OrderStatus.paid,
                payment_method="balance",
                payment_time=datetime.now()
            )
            self.db.add(order)
            
            # 更新订阅
            subscription.start_date = datetime.now()
            subscription.end_date = datetime.now() + timedelta(days=subscription.plan.duration_days)
            
            self.db.commit()
            
            # 发送续费通知
            user = self.db.query(User).filter(User.id == subscription.user_id).first()
            if user:
                notification_service.send_subscription_success(user, subscription, order)
            
            logger.info(f"自动续费成功: 用户 {subscription.user_id}")
            
        except Exception as e:
            logger.error(f"自动续费失败: {e}")
            self.db.rollback()
    
    def distribute_monthly_tickets(self):
        """分配月票给VIP用户"""
        try:
            logger.info("开始分配月度月票...")
            
            # 查找所有活跃的VIP订阅
            now = datetime.now()
            subscriptions = self.db.query(UserSubscription).filter(
                UserSubscription.status == SubscriptionStatus.active,
                UserSubscription.end_date > now
            ).all()
            
            ticket_count = 0
            for subscription in subscriptions:
                # 根据套餐类型分配月票
                plan = subscription.plan
                if plan.duration_days >= 365:  # 年度VIP
                    monthly_tickets = 50
                elif plan.duration_days >= 90:  # 季度VIP
                    monthly_tickets = 20
                else:  # 月度VIP
                    monthly_tickets = 10
                
                # 创建月票记录
                from app.models.models import MonthlyTicket
                ticket = MonthlyTicket(
                    user_id=subscription.user_id,
                    work_id=1,  # 默认投给第一个作品
                    ticket_count=monthly_tickets
                )
                self.db.add(ticket)
                ticket_count += monthly_tickets
            
            self.db.commit()
            logger.info(f"月度月票分配完成，共分配 {ticket_count} 张月票")
            
        except Exception as e:
            logger.error(f"月度月票分配失败: {e}")
            self.db.rollback()
    
    def generate_monthly_statistics(self):
        """生成月度统计报告"""
        try:
            logger.info("开始生成月度统计报告...")
            
            # 获取上个月的数据
            now = datetime.now()
            last_month = now.replace(day=1) - timedelta(days=1)
            start_date = last_month.replace(day=1)
            
            # 统计收入
            paid_orders = self.db.query(Order).filter(
                Order.status == OrderStatus.paid,
                Order.created_at >= start_date,
                Order.created_at <= last_month
            ).all()
            
            total_revenue = sum(order.amount for order in paid_orders)
            
            # 统计VIP用户
            vip_users = self.db.query(UserSubscription).filter(
                UserSubscription.status == SubscriptionStatus.active,
                UserSubscription.start_date >= start_date,
                UserSubscription.start_date <= last_month
            ).count()
            
            # 统计月票
            total_tickets = self.db.query(MonthlyTicket).filter(
                MonthlyTicket.created_at >= start_date,
                MonthlyTicket.created_at <= last_month
            ).count()
            
            # 生成统计报告
            report = f"""
            月度统计报告 ({start_date.strftime('%Y-%m')}):
            
            💰 总收入: ¥{total_revenue:.2f}
            📊 订单数: {len(paid_orders)}
            👥 新增VIP用户: {vip_users}
            🎫 月票总数: {total_tickets}
            
            收入构成:
            - VIP订阅: ¥{sum(o.amount for o in paid_orders if o.order_type == OrderType.subscription):.2f}
            - 单章购买: ¥{sum(o.amount for o in paid_orders if o.order_type == OrderType.chapter):.2f}
            - 其他: ¥{sum(o.amount for o in paid_orders if o.order_type not in [OrderType.subscription, OrderType.chapter]):.2f}
            """
            
            logger.info("月度统计报告生成完成")
            logger.info(report)
            
            # 可以发送邮件给管理员
            
        except Exception as e:
            logger.error(f"月度统计生成失败: {e}")
    
    def start(self):
        """启动定时任务"""
        try:
            self.scheduler.start()
            logger.info("定时任务服务已启动")
        except Exception as e:
            logger.error(f"启动定时任务失败: {e}")
    
    def stop(self):
        """停止定时任务"""
        try:
            self.scheduler.shutdown()
            logger.info("定时任务服务已停止")
        except Exception as e:
            logger.error(f"停止定时任务失败: {e}")


# 定时任务服务实例
cron_service = CronService()