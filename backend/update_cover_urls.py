"""Update cover_url for all existing works to point to actual cover SVGs"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "novel.db")

def update_cover_urls():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all works
    cursor.execute("SELECT id, title FROM works ORDER BY id")
    works = cursor.fetchall()
    
    print(f"Found {len(works)} works to update:")
    
    for work_id, title in works:
        cover_url = f"/covers/cover-{work_id}.svg"
        cursor.execute(
            "UPDATE works SET cover_url = ? WHERE id = ?",
            (cover_url, work_id)
        )
        print(f"  Updated work #{work_id}: '{title}' -> {cover_url}")
    
    conn.commit()
    conn.close()
    print("\nDone! All cover_urls updated.")

if __name__ == "__main__":
    update_cover_urls()
