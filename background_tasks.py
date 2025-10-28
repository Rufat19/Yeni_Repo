import asyncio
import logging
from aiogram import Bot

logger = logging.getLogger(__name__)

async def monitor_new_users(bot: Bot, admin_id: int):
    """
    Hər 60 saniyədən bir user_start_history.log faylını yoxlayır
    və yeni gələn istifadəçiləri adminə bildirir.
    """
    logger.info("Yeni istifadəçilər üçün fon izləmə başladı.")
    seen_users = set()

    while True:
        try:
            with open("user_start_history.log", "r", encoding="utf-8") as f:
                lines = f.readlines()

            for line in lines:
                user_id, date = line.strip().split("|")
                if user_id not in seen_users:
                    seen_users.add(user_id)
                    await bot.send_message(
                        admin_id,
                        f"🆕 Yeni istifadəçi botu işə saldı:\n<code>{user_id}</code> — {date}",
                        parse_mode="HTML"
                    )
        except FileNotFoundError:
            logger.warning("user_start_history.log tapılmadı.")
        except Exception as e:
            logger.error(f"Monitor xətası: {e}")

        await asyncio.sleep(60)  # hər 60 saniyədən bir yenidən yoxla

async def send_regular_message(bot: Bot, chat_id: int, interval: int = 3600):
    """
    Periodically send a simple heartbeat message to `chat_id`.
    Kept lightweight so startup can schedule it safely.
    """
    logger.info("send_regular_message background task started (interval=%s)", interval)
    while True:
        try:
            await bot.send_message(chat_id, "✅ Bot canlıdır — heartbeat")
        except Exception as e:
            logger.exception("Failed to send regular message: %s", e)
        await asyncio.sleep(interval)
