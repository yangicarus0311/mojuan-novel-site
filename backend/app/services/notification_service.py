"""通知服务 - 用于发送支付和订阅相关通知"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging

from app.models.models import User, UserSubscription, Order

logger = logging.getLogger(__name__)


class NotificationService:
    """通知服务类"""
    
    def __init__(self):
        self.smtp_host = "smtp.example.com"
        self.smtp_port = 587
        self.smtp_user = "noreply@example.com"
        self.smtp_password = "your_password"
        self.from_email = "墨卷网文 <noreply@example.com>"
    
    def send_subscription_success(
        self, 
        user: User, 
        subscription: UserSubscription,
        order: Order
    ) -> bool:
        """发送订阅成功通知"""
        try:
            subject = f"订阅成功！{subscription.plan.name}"
            
            # HTML邮件内容
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: 'Segoe UI', 'Microsoft YaHei', Arial, sans-serif; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #ff6b6b; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                    .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
                    .plan-name {{ font-size: 24px; color: #ff6b6b; font-weight: bold; }}
                    .details {{ margin-top: 20px; line-height: 1.8; }}
                    .expire-date {{ color: #666; font-size: 16px; }}
                    .support {{ margin-top: 30px; color: #999; font-size: 14px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>订阅成功！</h1>
                    </div>
                    <div class="content">
                        <p>亲爱的 <strong>{user.username}</strong>，</p>
                        <p>您已成功订阅 <span class="plan-name">{subscription.plan.name}</span>！</p>
                        <div class="details">
                            <p>🎫 订单号：{order.order_no}</p>
                            <p>💰 支付金额：¥{order.amount:.2f}</p>
                            <p>📅 生效时间：{subscription.start_date.strftime('%Y-%m-%d %H:%M:%S')}</p>
                            <p>⏰ 到期时间：{subscription.end_date.strftime('%Y-%m-%d %H:%M:%S')}</p>
                        </div>
                        <div class="expire-date">
                            <p>💡 您的VIP权限将在到期前3天提醒您续费，避免影响阅读体验。</p>
                        </div>
                        <div class="support">
                            <p>如有任何问题，请联系客服：support@mojuan.com</p>
                            <p>感谢您对墨卷的支持！</p>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            return self.send_email(user.email, subject, html_content)
            
        except Exception as e:
            logger.error(f"发送订阅成功通知失败: {e}")
            return False
    
    def send_recharge_success(self, user: User, order: Order) -> bool:
        """发送充值成功通知"""
        try:
            subject = "充值成功！"
            
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: 'Segoe UI', 'Microsoft YaHei', Arial, sans-serif; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #4CAF50; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                    .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
                    .amount {{ font-size: 32px; color: #4CAF50; font-weight: bold; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>充值成功！</h1>
                    </div>
                    <div class="content">
                        <p>亲爱的 <strong>{user.username}</strong>，</p>
                        <p>您的账户已成功充值：</p>
                        <div style="text-align: center; margin: 30px 0;">
                            <div class="amount">¥{order.amount:.2f}</div>
                            <p>订单号：{order.order_no}</p>
                        </div>
                        <p>💰 当前余额：¥{user.balance:.2f}</p>
                        <p>您现在可以使用余额购买单章或订阅VIP服务。</p>
                        <div style="margin-top: 30px; color: #999; font-size: 14px;">
                            <p>如有任何问题，请联系客服：support@mojuan.com</p>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            return self.send_email(user.email, subject, html_content)
            
        except Exception as e:
            logger.error(f"发送充值成功通知失败: {e}")
            return False
    
    def send_subscription_expiring(
        self, 
        user: User, 
        subscription: UserSubscription,
        days_before: int = 3
    ) -> bool:
        """发送订阅即将到期提醒"""
        try:
            subject = f"您的VIP会员即将到期（剩余{days_before}天）"
            
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: 'Segoe UI', 'Microsoft YaHei', Arial, sans-serif; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #ff9500; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                    .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
                    .warning {{ color: #ff9500; font-weight: bold; }}
                    .renew-btn {{ 
                        display: inline-block; 
                        background: #ff6b6b; 
                        color: white; 
                        padding: 12px 30px; 
                        text-decoration: none; 
                        border-radius: 5px; 
                        margin: 20px 0;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>VIP到期提醒</h1>
                    </div>
                    <div class="content">
                        <p>亲爱的 <strong>{user.username}</strong>，</p>
                        <p class="warning">您的VIP会员即将到期！</p>
                        <div style="margin: 20px 0; line-height: 1.8;">
                            <p>📅 会员类型：{subscription.plan.name}</p>
                            <p>⏰ 到期时间：{subscription.end_date.strftime('%Y-%m-%d %H:%M:%S')}</p>
                            <p>📊 剩余时间：<span class="warning">{days_before}天</span></p>
                        </div>
                        <p>续费后可继续享受：</p>
                        <ul>
                            <li>✓ VIP专属章节免费看</li>
                            <li>✓ 专属月票奖励</li>
                            <li>✓ 无广告阅读体验</li>
                        </ul>
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="http://localhost:8080/payment" class="renew-btn">立即续费</a>
                        </div>
                        <div style="color: #999; font-size: 14px;">
                            <p>💡 提示：续费享受更多优惠，连续订阅更划算！</p>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            return self.send_email(user.email, subject, html_content)
            
        except Exception as e:
            logger.error(f"发送到期提醒失败: {e}")
            return False
    
    def send_email(
        self, 
        to_email: str, 
        subject: str, 
        html_content: str
    ) -> bool:
        """发送邮件"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # 添加HTML内容
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # 连接SMTP服务器并发送
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"邮件发送成功：{to_email}")
            return True
            
        except Exception as e:
            logger.error(f"邮件发送失败：{to_email}, 错误：{e}")
            return False


# 通知服务实例
notification_service = NotificationService()