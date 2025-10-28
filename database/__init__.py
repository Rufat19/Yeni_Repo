import sqlite3
from config import DB_PATH
from datetime import datetime


def _get_conn():
	conn = sqlite3.connect(DB_PATH)
	conn.row_factory = sqlite3.Row
	return conn


def add_news_to_db(title, content, admin_id):
	"""Insert a news item and return its id."""
	with _get_conn() as conn:
		conn.execute(
			"""
			CREATE TABLE IF NOT EXISTS news (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				title TEXT,
				content TEXT,
				admin_id INTEGER,
				created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
			)
			"""
		)
		cur = conn.execute(
			"INSERT INTO news (title, content, admin_id, created_at) VALUES (?, ?, ?, ?)",
			(title, content, admin_id, datetime.utcnow().isoformat()),
		)
		conn.commit()
		return cur.lastrowid


def get_all_news():
	"""Return list of news dicts ordered by newest first."""
	with _get_conn() as conn:
		# ensure table exists to avoid OperationalError when reading on a fresh DB
		conn.execute(
			"""
			CREATE TABLE IF NOT EXISTS news (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				title TEXT,
				content TEXT,
				admin_id INTEGER,
				created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
			)
			"""
		)
		rows = conn.execute("SELECT id, title, content, admin_id, created_at FROM news ORDER BY created_at DESC").fetchall()
		return [dict(r) for r in rows]


def get_news_by_id(news_id):
	with _get_conn() as conn:
		conn.execute(
			"""
			CREATE TABLE IF NOT EXISTS news (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				title TEXT,
				content TEXT,
				admin_id INTEGER,
				created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
			)
			"""
		)
		row = conn.execute("SELECT id, title, content, admin_id, created_at FROM news WHERE id=?", (news_id,)).fetchone()
		return dict(row) if row else None


def get_all_users():
	"""Return list of users as dicts {'id': user_id} for broadcasting."""
	with _get_conn() as conn:
		rows = conn.execute("SELECT user_id FROM users").fetchall()
		return [{"id": r[0]} for r in rows]

