from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from config import ADMIN_ID
import datetime
from collections import Counter
import os
from datetime import datetime, timedelta

router = Router()

@router.message(Command(commands=["admin"]))
async def admin_panel(message: Message, state: FSMContext):
    if not message.from_user or message.from_user.id != ADMIN_ID:
        # provide short diagnostic to help configure ADMIN_ID if needed
        user_id = message.from_user.id if message.from_user else "unknown"
        await message.answer(
            f"Bu funksiya yalnız admin üçündür.\n"
            f"Sənin id: {user_id}\n"
            f"Konfiqdə ADMIN_ID: {ADMIN_ID}\n\n"
            f"Qeyd: Qrupda istifadə edirsinizsə, istifadəçi mesajı `/admin@BotUsername` şəklində gələ bilər; bu handler həm fərdi həm də qrupda işləyir."
        )
        return

    try:
        # If the log file doesn't exist, create an empty one and inform admin
        if not os.path.exists("user_activity.log"):
            # create empty file to avoid future FileNotFoundError
            open("user_activity.log", "w", encoding="utf-8").close()
            await message.answer("Heç bir fəaliyyət qeydi yoxdur.")
            return

        with open("user_activity.log", "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
        if not lines:
            await message.answer("Heç bir fəaliyyət qeydi yoxdur.")
            return

        users = set()
        actions = []
        langs = []
        # For top active users we count by username (fallback to id)
        user_activity_counter = Counter()
        # Track earliest seen date per user to compute new users in last 7 days
        earliest_seen = {}
        for line in lines:
            parts = line.split("|")
            # tolerate malformed lines
            if len(parts) < 5:
                continue
            user_id, username, action, date_str, lang = parts[:5]
            users.add(user_id)
            actions.append(action)
            langs.append(lang)

            who = username.strip() or user_id
            user_activity_counter[who] += 1

            # parse date with fallbacks
            parsed_date = None
            try:
                # try ISO first
                parsed_date = datetime.fromisoformat(date_str)
            except Exception:
                try:
                    parsed_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                except Exception:
                    parsed_date = None

            if parsed_date is not None:
                if user_id not in earliest_seen or parsed_date < earliest_seen[user_id]:
                    earliest_seen[user_id] = parsed_date

        total_users = len(users)
        most_common_actions = Counter(actions).most_common(3)
        most_common_langs = Counter(langs).most_common(3)
        # Top 10 active users
        top_10_users = user_activity_counter.most_common(10)
        # New users in last 7 days (based on earliest_seen)
        cutoff = datetime.utcnow() - timedelta(days=7)
        new_users_last_7 = sum(1 for d in earliest_seen.values() if d >= cutoff)

        text = (
            f"📊 <b>Admin Panel Hesabatı</b>\n"
            f"👥 Ümumi istifadəçilər: <b>{total_users}</b>\n"
            f"📅 Son qeyd: <i>{lines[-1].split('|')[3]}</i>\n\n"
            f"🔥 Ən çox əməl edilən fəaliyyətlər:\n"
        )

        for action, count in most_common_actions:
            text += f" — {action}: {count} dəfə\n"

        text += "\n"
        # include language breakdown
        text += "🌐 Ən çox istifadə olunan dillər:\n"
        for lang, count in most_common_langs:
            text += f" — {lang}: {count} dəfə\n"

        text += "\n"
        # Top 10 active users
        text += "👑 Top 10 ən aktiv istifadəçi:\n"
        if top_10_users:
            for i, (who, cnt) in enumerate(top_10_users, start=1):
                text += f" {i}. {who} — {cnt} əməliyyat\n"
        else:
            text += " Heç bir aktiv istifadəçi qeydə alınmayıb\n"

        text += "\n"
        text += f"🆕 Son 7 günə əlavə olunan yeni istifadəçilər: <b>{new_users_last_7}</b>\n"

        # send report to admin
        await message.answer(text, parse_mode="HTML")
        return
    except Exception as e:
        await message.answer(f"Fəaliyyət qeydləri oxunarkən xəta baş verdi: {e}")
        return
