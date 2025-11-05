import json
import os
from datetime import datetime
from utils.timezone_utils import baku_now_for_history
from config import DATA_DIR


HISTORY_PATH = os.path.join(DATA_DIR, "user_history.json")


def _ensure_dir():
    os.makedirs(os.path.dirname(HISTORY_PATH), exist_ok=True)


def _load_all():
    if not os.path.exists(HISTORY_PATH):
        return {}
    try:
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f) or {}
    except Exception:
        # If file is corrupted, back it up and start fresh
        try:
            backup = HISTORY_PATH + ".bak"
            os.replace(HISTORY_PATH, backup)
        except Exception:
            pass
        return {}


def _save_all(data: dict):
    _ensure_dir()
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def log_balance_change(user_id: int, prev_balance: int, new_balance: int, reason: str = None, source: str = None, meta: dict | None = None):
    """Append a balance change event for a user.

    Event shape:
    {
      "ts": ISO8601,
      "type": "balance_change",
      "delta": int,
      "prev": int,
      "new": int,
      "reason": str | null,
      "source": str | null,
      "meta": { ... }
    }
    """
    data = _load_all()
    key = str(user_id)
    events = data.get(key) or []
    delta = int(new_balance) - int(prev_balance)
    events.append({
        "ts": baku_now_for_history(),
        "type": "balance_change",
        "delta": delta,
        "prev": int(prev_balance),
        "new": int(new_balance),
        "reason": reason,
        "source": source or "db_utils.set_balance",
        "meta": meta or {},
    })
    data[key] = events
    _save_all(data)


def get_user_history(user_id: int) -> list:
    data = _load_all()
    return data.get(str(user_id), [])


def summarize_user_history(user_id: int) -> dict:
    events = get_user_history(user_id)
    total_topup = sum(e.get("delta", 0) for e in events if e.get("delta", 0) > 0)
    total_spent = -sum(e.get("delta", 0) for e in events if e.get("delta", 0) < 0)
    first_ts = events[0]["ts"] if events else None
    last_ts = events[-1]["ts"] if events else None
    return {
        "count": len(events),
        "total_topup": total_topup,
        "total_spent": total_spent,
        "first_ts": first_ts,
        "last_ts": last_ts,
    }
