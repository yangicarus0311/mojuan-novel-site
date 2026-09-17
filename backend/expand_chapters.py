"""Expand the local SQLite demo library without discarding author-written chapters.

Usage: python expand_chapters.py /path/to/novel.db --apply
Without --apply, prints a read-only preview. The apply path creates a SQLite backup.
"""
import argparse
from datetime import datetime
from pathlib import Path
import sqlite3

from app.services.demo_story import STORIES, demo_title, expanded_content, is_seed_stub


def expand(database: Path, apply: bool = False):
    database = database.resolve()
    with sqlite3.connect(f"file:{database}?mode=ro", uri=True) as source:
        rows = source.execute("""SELECT c.id, c.chapter_number, c.title, c.content, w.title
            FROM chapters c JOIN works w ON c.work_id = w.id ORDER BY c.id""").fetchall()
        has_tracking = source.execute("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'demo_expansions'").fetchone()
        expanded_ids = {row[0] for row in source.execute("SELECT chapter_id FROM demo_expansions")} if has_tracking else set()
        updates = []
        for chapter_id, number, chapter_title, content, work_title in rows:
            if work_title not in STORIES or chapter_id in expanded_ids:
                continue
            is_stub = is_seed_stub(content or "")
            new_title = demo_title(work_title, number) if is_stub else chapter_title
            changed = expanded_content(work_title, number, new_title, content or "")
            updates.append((changed, len(changed), new_title, chapter_id))
        print(f"Chapters: {len(rows)}; to expand: {len(updates)}")
        if not apply or not updates:
            return len(updates)
        backup = database.parent / f"{database.stem}-before-expansion-{datetime.now():%Y%m%d-%H%M%S-%f}.db"
        with sqlite3.connect(backup) as saved:
            source.backup(saved)
        print(f"Backup: {backup}")
    with sqlite3.connect(database) as target:
        target.execute("CREATE TABLE IF NOT EXISTS demo_expansions (chapter_id INTEGER PRIMARY KEY, version INTEGER NOT NULL DEFAULT 2)")
        target.executemany("UPDATE chapters SET content = ?, word_count = ?, title = ? WHERE id = ?", updates)
        target.executemany("INSERT INTO demo_expansions (chapter_id, version) VALUES (?, 2)", ((item[3],) for item in updates))
        target.execute("""UPDATE works SET word_count = COALESCE(
            (SELECT SUM(word_count) FROM chapters WHERE work_id = works.id), 0)
            WHERE title IN ({})""".format(",".join("?" for _ in STORIES)), tuple(STORIES))
        target.commit()
    return len(updates)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("database", type=Path)
    parser.add_argument("--apply", action="store_true")
    arguments = parser.parse_args()
    expand(arguments.database, arguments.apply)
