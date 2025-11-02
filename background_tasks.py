import asyncio
import logging
from aiogram import Bot
from datetime import datetime, time

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
    Gündə bir dəfə səhər 7:00-8:00 arası "Bot canlıdır" mesajı göndərir.
    """
    logger.info("send_regular_message background task started (daily at 7-8 AM)")
    
    while True:
        try:
            now = datetime.now()
            current_time = now.time()
            
            # Səhər 7:00 - 8:00 arasındamı?
            target_start = time(7, 0)  # 07:00
            target_end = time(8, 0)    # 08:00
            
            if target_start <= current_time <= target_end:
                # Bugün artıq göndərdikmi yoxla (hər gün yalnız bir dəfə)
                # Növbəti mesaj üçün sabahın 07:00-na qədər gözlə
                await bot.send_message(chat_id, "✅ Bot canlıdır — gündəlik yoxlama")
                logger.info("Daily heartbeat sent at %s", now)
                
                # Sabahın 07:00-a qədər gözlə (təxminən 23 saat)
                await asyncio.sleep(23 * 3600)
            else:
                # Hələ 07:00 olmayıbsa və ya 08:00-dan keçibsə
                # Növbəti yoxlama üçün 1 saat gözlə
                await asyncio.sleep(3600)
                
        except Exception as e:
            logger.exception("Failed to send regular message: %s", e)
            await asyncio.sleep(3600)  # Xəta zamanı 1 saat gözlə
