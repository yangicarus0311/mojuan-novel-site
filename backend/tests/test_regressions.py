import os
import unittest
from datetime import datetime, timedelta
from decimal import Decimal

os.environ['DATABASE_URL'] = 'sqlite://'
os.environ['SECRET_KEY'] = 'test-only-key-not-for-deployment-1234567890'

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.core.database import Base, get_db
from app.core.security import create_access_token
from app.models.models import (
    User, Work, Chapter, WorkPrice, UserBalance, Order, OrderType, OrderStatus,
    PaymentPlan, UserSubscription, SubscriptionStatus, ReadingSession,
)


class RegressionTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()
        self.db.add_all([
            User(id=1, username='reader', email='reader@example.com', password_hash='unused'),
            User(id=2, username='admin', email='admin@example.com', password_hash='unused', is_admin=1),
            Work(id=1, title='墨卷测试', author='作者', category='仙侠', clicks=5),
            Work(id=2, title='第二部墨卷', author='作者', category='仙侠', clicks=20),
            Chapter(id=1, work_id=1, chapter_number=1, title='第一章', content='正文' * 500, word_count=1000),
            Chapter(id=2, work_id=1, chapter_number=2, title='第二章', content='后续' * 500, word_count=1000),
            Chapter(id=3, work_id=2, chapter_number=1, title='另一作品', content='正文' * 500, word_count=1000),
            WorkPrice(work_id=1, chapter_price=Decimal('2.00'), is_premium=False),
            UserBalance(user_id=1, balance=Decimal('10.00')),
            PaymentPlan(id=1, name='月度会员', price=10, duration_days=30, is_active=True),
        ])
        self.db.commit()

        def override_db():
            with self.Session() as db:
                yield db
        app.dependency_overrides[get_db] = override_db
        self.client = TestClient(app)
        self.headers = {'Authorization': 'Bearer ' + create_access_token({'sub': '1'})}
        self.admin = {'Authorization': 'Bearer ' + create_access_token({'sub': '2'})}

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.clear()
        self.db.close()
        self.engine.dispose()

    def test_catalog_never_returns_content(self):
        response = self.client.get('/api/chapters', params={'work_id': 1})
        self.assertEqual(response.status_code, 200)
        for chapter in response.json()['chapters']:
            self.assertNotIn('content', chapter)
        self.assertNotIn('正文', response.text)

    def test_search_route_sort_and_pagination(self):
        response = self.client.get('/api/works/search', params={'q': '墨卷', 'sort': 'clicks', 'page_size': 1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['total'], 2)
        self.assertEqual(response.json()['works'][0]['id'], 2)

    def test_normal_users_cannot_publish(self):
        work = {'title': '新增', 'author': '作者', 'category': '仙侠'}
        chapter = {'chapter_number': 3, 'title': '新增', 'content': '文本'}
        self.assertEqual(self.client.post('/api/works', json=work, headers=self.headers).status_code, 403)
        self.assertEqual(self.client.post('/api/chapters?work_id=1', json=chapter, headers=self.headers).status_code, 403)
        self.assertEqual(self.client.post('/api/works', json=work, headers=self.admin).status_code, 200)

    def test_anonymous_content_requires_login(self):
        self.assertEqual(self.client.get('/api/chapters/1').status_code, 401)

    def test_balance_is_not_a_purchase(self):
        for path in ['/api/chapters/1', '/api/chapters/1/content']:
            self.assertEqual(self.client.get(path, headers=self.headers).status_code, 402)

    def test_legacy_order_does_not_grant_every_chapter(self):
        self.db.add(Order(order_no='legacy', user_id=1, order_type=OrderType.chapter, amount=2, status=OrderStatus.paid))
        self.db.commit()
        self.assertEqual(self.client.get('/api/chapters/2', headers=self.headers).status_code, 402)

    def test_purchase_is_specific_and_idempotent(self):
        for _ in range(2):
            response = self.client.post('/api/payment/chapter/purchase?work_id=1&chapter_id=1', headers=self.headers)
            self.assertEqual(response.status_code, 200, response.text)
        self.db.expire_all()
        self.assertEqual(self.db.query(UserBalance).filter_by(user_id=1).one().balance, Decimal('8.00'))
        self.assertEqual(self.db.query(Order).count(), 1)
        self.assertEqual(self.client.get('/api/chapters/1', headers=self.headers).status_code, 200)
        self.assertEqual(self.client.get('/api/chapters/2', headers=self.headers).status_code, 402)

    def test_purchase_rejects_wrong_work(self):
        response = self.client.post('/api/payment/chapter/purchase?work_id=2&chapter_id=1', headers=self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.db.query(Order).count(), 0)

    def test_purchase_insufficient_balance_does_not_create_order(self):
        self.db.query(UserBalance).update({'balance': Decimal('0.00')})
        self.db.commit()
        response = self.client.post('/api/payment/chapter/purchase?work_id=1&chapter_id=1', headers=self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.db.query(Order).count(), 0)

    def test_vip_status_and_access(self):
        self.db.add(UserSubscription(user_id=1, plan_id=1, status=SubscriptionStatus.active,
            start_date=datetime.now(), end_date=datetime.now() + timedelta(days=30)))
        self.db.commit()
        response = self.client.get('/api/payment/subscription/status', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['plan_name'], '月度会员')
        self.assertEqual(self.client.get('/api/chapters/1', headers=self.headers).status_code, 200)

    def test_balance_and_admin_payment_use_user_objects(self):
        self.assertEqual(self.client.get('/api/payment/balance', headers=self.headers).json()['balance'], 10)
        self.assertEqual(self.client.get('/api/admin/payment/plans', headers=self.headers).status_code, 403)
        self.assertEqual(self.client.get('/api/admin/payment/plans', headers=self.admin).status_code, 200)

    def test_unconfigured_checkout_creates_no_order(self):
        for url in ['/api/payment/subscribe?plan_id=1&payment_method=alipay', '/api/payment/recharge?amount=10&payment_method=alipay']:
            self.assertEqual(self.client.post(url, headers=self.headers).status_code, 503)
        self.assertEqual(self.db.query(Order).count(), 0)

    def test_callbacks_cannot_mark_orders_paid(self):
        self.db.add(Order(order_no='pending', user_id=1, order_type=OrderType.subscription, amount=10, status=OrderStatus.pending))
        self.db.commit()
        for method, url in [('get', '/api/payment/webhook/test/success'), ('post', '/api/payment/webhook/balance'), ('post', '/api/payment/webhook/payment'), ('post', '/api/payment/webhook/wechat'), ('post', '/api/payment/webhook/alipay')]:
            response = getattr(self.client, method)(url, params={'order_no': 'pending', 'status': 'paid'})
            self.assertIn(response.status_code, (404, 405, 503))
        self.db.expire_all()
        self.assertEqual(self.db.query(Order).one().status, OrderStatus.pending)

    def test_heartbeat_caps_and_saves_progress(self):
        payload = {'work_id': 2, 'chapter_id': 3, 'duration_seconds': 30, 'chars_read': 250, 'progress': 25}
        for _ in range(2):
            self.assertEqual(self.client.post('/api/reading/heartbeat', json=payload, headers=self.headers).status_code, 200)
        self.assertEqual(sum(row.chars_read for row in self.db.query(ReadingSession)), 250)
        self.assertLessEqual(sum(row.duration_seconds for row in self.db.query(ReadingSession)), 30)
        progress = self.client.get('/api/bookshelf/progress/2', headers=self.headers)
        self.assertEqual(progress.json()['progress'], 25)

    def test_heartbeat_rejects_invalid_metrics_and_chapter(self):
        payload = {'work_id': 2, 'chapter_id': 3, 'duration_seconds': 30, 'chars_read': 250, 'progress': 25}
        for field, value in [('duration_seconds', -1), ('duration_seconds', 99999), ('chars_read', -1), ('progress', 101)]:
            self.assertEqual(self.client.post('/api/reading/heartbeat', json={**payload, field: value}, headers=self.headers).status_code, 422)
        self.assertEqual(self.client.post('/api/reading/heartbeat', json={**payload, 'work_id': 1}, headers=self.headers).status_code, 404)

    def test_statistics_return_daily_totals_on_sqlite(self):
        self.db.add(ReadingSession(user_id=1, work_id=2, chapter_id=3, duration_seconds=120,
            chars_read=250, session_date=datetime.now()))
        self.db.commit()
        response = self.client.get('/api/reading/stats', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['total_duration_minutes'], 2)
        self.assertEqual(response.json()['daily_stats'][0]['chars_read'], 250)
        self.assertEqual(response.json()['streak_days'], 1)


if __name__ == '__main__':
    unittest.main()
