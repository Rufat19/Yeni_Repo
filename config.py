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

# --- Versiya / informasiya ---
APP_VERSION = os.getenv("APP_VERSION", "dev")
REPO_NAME = os.getenv("REPO_NAME", "Yeni_Repo")

# --- Verilənlər bazası və persistens ---
# DATA_DIR prioritetləri:
# 1) DATA_DIR env var (məs: /mnt/data — Railway Volume)
# 2) Əgər /mnt/data mövcuddursa, ondan istifadə et
# 3) Repository daxilindəki data/ (lokal inkişaf üçün)
DATA_DIR = os.getenv("DATA_DIR")
if not DATA_DIR:
    if os.path.isdir("/mnt/data"):
        DATA_DIR = "/mnt/data"
    else:
        DATA_DIR = os.path.join(BASE_DIR, "data")

# DB_PATH prioritetləri:
# 1) DB_PATH env var (əgər nisbi yol verilərsə, DATA_DIR ilə birləşdiriləcək)
# 2) DATA_DIR/database.db
_env_db = os.getenv("DB_PATH")
if _env_db:
    DB_PATH = _env_db if os.path.isabs(_env_db) else os.path.join(DATA_DIR, _env_db)
else:
    DB_PATH = os.path.join(DATA_DIR, "database.db")

# --- Təhlükəsizlik yoxlaması ---
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN .env faylında təyin olunmalıdır.")
