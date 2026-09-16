import os
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from pathlib import Path
from threading import Barrier

os.environ['DATABASE_URL'] = 'sqlite://'
os.environ['SECRET_KEY'] = 'test-only-key-not-for-deployment-1234567890'

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.models.models import User, Work, Chapter, WorkPrice, UserBalance, Order, ChapterPurchase
from app.services.payment_service import PaymentService


class ConcurrentPurchaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.engine = create_engine('sqlite:///' + str(Path(self.temp.name) / 'test.db'),
            connect_args={'check_same_thread': False, 'timeout': 10})
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        with self.Session() as db:
            db.add_all([
                User(id=1, username='reader', email='reader@example.com', password_hash='unused'),
                Work(id=1, title='并发测试', author='作者', category='仙侠'),
                Chapter(id=1, work_id=1, chapter_number=1, title='一'),
                Chapter(id=2, work_id=1, chapter_number=2, title='二'),
                WorkPrice(work_id=1, chapter_price=Decimal('7.00')),
                UserBalance(user_id=1, balance=Decimal('10.00')),
            ])
            db.commit()

    def tearDown(self):
        self.engine.dispose()
        self.temp.cleanup()

    def purchase_together(self, chapters):
        barrier = Barrier(2)
        def purchase(chapter_id):
            with self.Session() as db:
                barrier.wait(timeout=5)
                try:
                    return PaymentService.purchase_chapter(db, 1, 1, chapter_id)
                except ValueError:
                    return {'success': False}
        with ThreadPoolExecutor(max_workers=2) as executor:
            return list(executor.map(purchase, chapters))

    def test_parallel_purchases_cannot_overdraw(self):
        outcomes = self.purchase_together([1, 2])
        self.assertEqual(sum(item['success'] for item in outcomes), 1)
        with self.Session() as db:
            self.assertEqual(db.query(UserBalance).one().balance, Decimal('3.00'))
            self.assertEqual(db.query(Order).count(), 1)
            self.assertEqual(db.query(ChapterPurchase).count(), 1)

    def test_parallel_duplicate_purchase_only_charges_once(self):
        self.assertTrue(all(item['success'] for item in self.purchase_together([1, 1])))
        with self.Session() as db:
            self.assertEqual(db.query(UserBalance).one().balance, Decimal('3.00'))
            self.assertEqual(db.query(Order).count(), 1)
