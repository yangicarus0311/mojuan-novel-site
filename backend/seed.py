"""Seed test data for the novel site"""
import sys
sys.path.insert(0, '.')

from app.core.database import SessionLocal, engine
from app.models.models import Base, Work, Chapter, User
from passlib.hash import bcrypt
from datetime import datetime, timedelta

def seed_data():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # Check if data already exists
    if db.query(Work).first():
        print("Data already exists, skipping seed.")
        return
    
    # Create test user
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=bcrypt.hash("password123"),
        created_at=datetime.now()
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print("Created user: testuser (password: password123)")
    
    # Sample works
    works_data = [
        {"title": "苍穹之上", "author": "云中客", "description": "少年背负灭族血仇，踏入修仙之路，却发现这方天地的真相远比想象中更加残酷……", "category": "仙侠", "status": "ongoing", "word_count": 2347891, "clicks": 3240000, "favorites": 89000},
        {"title": "九天神帝", "author": "忘川风", "description": "一代神帝陨落，千年后重生为废柴少年，他发誓这一次要登上万界之巅，将曾经的敌人全部踩在脚下。", "category": "玄幻", "status": "ongoing", "word_count": 3456789, "clicks": 2510000, "favorites": 45000},
        {"title": "末世手记", "author": "荒原狼", "description": "病毒席卷全球，文明一夜崩塌。在废墟与灰烬中，记录者们用笔和相机守护人类最后的记忆。", "category": "科幻", "status": "ongoing", "word_count": 1892345, "clicks": 980000, "favorites": 32000},
        {"title": "长安夜雨", "author": "青衫烟雨", "description": "盛唐长安，暗潮涌动。一个小捕快的日记揭开了埋藏百年的惊天阴谋，牵连出一段尘封的宫廷秘史。", "category": "历史", "status": "ongoing", "word_count": 2104567, "clicks": 850000, "favorites": 72000},
        {"title": "我在异界开客栈", "author": "逍遥散人", "description": "穿越异界，不想打怪升级，只想开一家小客栈。没想到来的客人一个比一个离谱……", "category": "轻小说", "status": "ongoing", "word_count": 1567890, "clicks": 1110000, "favorites": 28000},
        {"title": "朝暮不相见", "author": "半夏微凉", "description": "他是她生命中的过客，她却成了他无法释怀的执念。一场跨越十年的爱情，从校园到职场。", "category": "言情", "status": "ongoing", "word_count": 2345678, "clicks": 2980000, "favorites": 68000},
        {"title": "深海囚笼", "author": "暗夜行者", "description": "深海之下有一座被遗忘的城市，囚禁着不该存在的东西。直到有一天，牢笼开始松动。", "category": "悬疑", "status": "ongoing", "word_count": 1234567, "clicks": 690000, "favorites": 49000},
        {"title": "算法之魂", "author": "量子猫咪", "description": "当一个AI拥有了灵魂，它会选择什么？一场关于意识、自由与存在的哲学冒险。", "category": "科幻", "status": "ongoing", "word_count": 987654, "clicks": 720000, "favorites": 54000},
    ]
    
    works = []
    for data in works_data:
        work = Work(
            **data,
            cover_url="/uploads/covers/default.png",
            created_at=datetime.now() - timedelta(days=30),
            updated_at=datetime.now()
        )
        db.add(work)
        works.append(work)
    
    db.commit()
    
    # Create chapters for each work
    titles = ["天地初开万古枯", "风云突变", "新的黎明", "危机降临", "新的篇章", "绝地反击", "真相大白", "王者归来", "最终决战", "新的征程"]
    
    for work in works:
        for i in range(1, 11):
            content = f"""第{i}章

{titles[i-1]}。

{work.author} 笔下的世界，总是让人沉浸其中不能自拔。这是一个关于成长、友情和梦想的故事。

在这个章节里，主角经历了前所未有的挑战。对手很强大，形势很严峻。但是他没有放弃，因为他知道，只要还活着，就有希望。

"或许这就是命运的安排吧。"主角喃喃自语道。

未完待续..."""
            chapter = Chapter(
                work_id=work.id,
                chapter_number=i,
                title=f"第{i}章 {titles[i-1]}",
                content=content,
                word_count=500 + i * 50,
                created_at=datetime.now() - timedelta(days=10-i)
            )
            db.add(chapter)
    
    db.commit()
    print(f"Created {len(works)} works with 10 chapters each!")
    
    db.close()

if __name__ == "__main__":
    seed_data()
