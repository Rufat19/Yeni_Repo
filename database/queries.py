import os
import json
from .db_connect import create_pool, pool

# ========== İSTİFADƏÇİLƏR ÜÇÜN ==========
async def add_user(user_id: int, name: str, lang: str):
    """Yeni istifadəçi əlavə et — PostgreSQL varsa ora, yoxdursa, sadəcə keç."""
    try:
        if pool is None:
            await create_pool()
        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO users (user_id, name, lang)
                VALUES ($1, $2, $3)
                ON CONFLICT (user_id) DO NOTHING;
            """, user_id, name, lang)
    except Exception as e:
        print(f"[WARN] add_user PostgreSQL işləmədi: {e}")


async def get_all_users():
    """Bütün istifadəçiləri göstər (PostgreSQL)."""
    try:
        if pool is None:
            await create_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM users;")
            return rows
    except Exception as e:
        print(f"[WARN] get_all_users PostgreSQL işləmədi: {e}")
        return []


# ========== YENİLİKLƏR ÜÇÜN (JSON SAXLAMA) ==========

NEWS_FILE = "news.json"

def load_news():
    """news.json faylını oxuyur."""
    if not os.path.exists(NEWS_FILE):
        return []
    try:
        with open(NEWS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[WARN] load_news failed: {e}")
        return []


def save_news(news_list):
    """Yenilikləri news.json-a yazır."""
    try:
        with open(NEWS_FILE, "w", encoding="utf-8") as f:
            json.dump(news_list, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[WARN] save_news failed: {e}")


def add_news(title: str, content: str):
    """Yeni yeniliyi əlavə et (lokal JSON saxlanma)."""
    news_list = load_news()
    new_id = max([n["id"] for n in news_list], default=0) + 1
    news_list.append({
        "id": new_id,
        "title": title,
        "content": content
    })
    save_news(news_list)
    print(f"[INFO] Yeni yenilik əlavə olundu: {title}")
    return new_id


def get_all_news():
    """Bütün yenilikləri al."""
    return load_news()


def get_news_by_id(news_id: int):
    """ID-ə görə konkret yeniliyi tap."""
    for n in load_news():
        if n["id"] == news_id:
            return n
    return None
