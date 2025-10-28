import os
from dotenv import load_dotenv

# .env faylını oxu
load_dotenv()

# Layihənin əsas qovluğunu tapırıq
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Əsas dəyişənlər ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 6520873307))  # .env-də olmasa, default
CARD_NUMBER = os.getenv("CARD_NUMBER", "4098 5844 6547 4300")

# --- Verilənlər bazası ---
DB_PATH = os.path.join(BASE_DIR, "data", "database.db")

# --- Təhlükəsizlik yoxlaması ---
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN .env faylında təyin olunmalıdır.")
