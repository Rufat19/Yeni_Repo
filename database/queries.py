import os
import json
from config import BASE_DIR
from .db import add_user as _sqlite_add_user, get_all_users as _sqlite_get_all_users

# ========== İSTİFADƏÇİLƏR ÜÇÜN ==========
def add_user(user_id: int, name: str, lang: str | None = None):
    """Yeni istifadəçini lokal SQLite bazaya əlavə et.

    Qeyd: 'lang' hazırda saxlanmır; gələcəkdə lazım olarsa, sxemə əlavə edilə bilər.
    """
    try:
        _sqlite_add_user(user_id, name)
    except Exception as e:
        print(f"[WARN] add_user (SQLite) uğursuz: {e}")


def get_all_users():
    """Bütün istifadəçiləri göstər (SQLite)."""
    try:
        return _sqlite_get_all_users()
    except Exception as e:
        print(f"[WARN] get_all_users (SQLite) uğursuz: {e}")
        return []


# ========== YENİLİKLƏR ÜÇÜN (JSON SAXLAMA) ==========

NEWS_FILE = os.path.join(BASE_DIR, "data", "news.json")

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
