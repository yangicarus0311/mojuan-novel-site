import sqlite3
import tempfile
import unittest
from pathlib import Path

from expand_chapters import expand
from app.services.demo_story import continuation, demo_title


class DemoExpansionTests(unittest.TestCase):
    def test_expansion_preserves_authored_text_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as folder:
            database = Path(folder) / 'novel.db'
            original = '晨光初破。叶尘看见了剑，仍不知它从何而来。'
            stub = '第1章\n\n云中客 笔下的世界，总是让人沉浸其中不能自拔。未完待续...'
            with sqlite3.connect(database) as db:
                db.execute('CREATE TABLE works (id INTEGER PRIMARY KEY, title TEXT, word_count INTEGER)')
                db.execute('CREATE TABLE chapters (id INTEGER PRIMARY KEY, work_id INTEGER, chapter_number INTEGER, title TEXT, content TEXT, word_count INTEGER)')
                db.executemany('INSERT INTO works VALUES (?, ?, ?)', [(1, '苍穹之上', 999999), (2, '青云劫', 999999)])
                db.executemany('INSERT INTO chapters VALUES (?, ?, ?, ?, ?, ?)', [
                    (1, 1, 1, '第1章 占位', stub, 600),
                    (2, 2, 1, '第一章 叶家废柴', original, len(original)),
                ])
            self.assertEqual(expand(database), 2)
            self.assertEqual(expand(database, True), 2)
            self.assertEqual(expand(database, True), 0)
            with sqlite3.connect(database) as db:
                first, second = db.execute('SELECT content FROM chapters ORDER BY id').fetchall()
                first_title = db.execute('SELECT title FROM chapters WHERE id = 1').fetchone()[0]
                self.assertTrue(second[0].startswith(original))
                self.assertNotIn('笔下的世界', first[0])
                self.assertEqual(first_title, demo_title('苍穹之上', 1))
                self.assertEqual(db.execute('SELECT count(*),min(version) FROM demo_expansions').fetchone(), (2, 2))
                self.assertEqual(db.execute('SELECT word_count FROM works WHERE id = 1').fetchone()[0], len(first[0]))
                self.assertGreaterEqual(len(first[0]), 4000)
            self.assertEqual(len(list(Path(folder).glob('*before-expansion*.db'))), 1)

    def test_story_uses_work_and_chapter_plot(self):
        first = continuation('苍穹之上', 1, demo_title('苍穹之上', 1))
        second = continuation('苍穹之上', 2, demo_title('苍穹之上', 2))
        other = continuation('末世手记', 1, demo_title('末世手记', 1))
        self.assertIn('林家旧宅出现一张陌生星图', first)
        self.assertIn('阿蘅认出监天司的封印', second)
        self.assertIn('灰港避难区', other)
        self.assertNotEqual(first, second)
        self.assertNotEqual(first, other)


if __name__ == '__main__':
    unittest.main()
