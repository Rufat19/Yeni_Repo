import asyncio
import os
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN, ADMIN_ID, DB_PATH
from utils.logging_config import setup_logging, get_logger
import background_tasks
from handlers import (
    start, fast_test, about, admin, quiz, quiz_world,
    order_bot, cert, balance, payment, review, pdf,
    news_handler, game, channel_access, misc
)
from handlers.db_utils import init_db
from database.db import create_tables


async def on_startup(bot: Bot):
    """Bot işə düşəndə fon tapşırıqları başladılır."""
    logger = get_logger(__name__)
    logger.info("Bot started successfully ✅")

    try:
        bot_chat_id = ADMIN_ID
        asyncio.create_task(background_tasks.send_regular_message(bot, bot_chat_id, interval=3600))
        asyncio.create_task(background_tasks.monitor_new_users(bot, bot_chat_id))
        logger.info("Background tasks scheduled")
    except Exception as e:
        logger.exception(f"Failed to start background tasks: {e}")


async def main():
    """Botu işə salır."""
    setup_logging()
    logger = get_logger(__name__)
    logger.info("Program başladı")

    # Database kataloqu
    db_dir = os.path.dirname(DB_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    # Database inicializasiya
    init_db()
    create_tables()

    # Token yoxlaması
    if not BOT_TOKEN:
        logger.critical("BOT_TOKEN is not set!")
        raise ValueError("BOT_TOKEN is not set!")

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Router-lar əlavə olunur
    for router in [
        start.router, fast_test.router, about.router, admin.router,
        quiz.router, quiz_world.router, order_bot.router, cert.router,
        balance.router, payment.payment_router, review.router, pdf.router,
        news_handler.router, game.router, channel_access.router, misc.misc_router
    ]:
        dp.include_router(router)

    logger.info("Router-lar əlavə olundu ✅")
    logger.info("Bot işə düşür...")

    # Aiogram 3.7 üçün startup event
    @dp.startup()
    async def _on_startup():
        await on_startup(bot)

    # Polling start
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        print("🚀 Railway-də bot işə düşür...")
        asyncio.run(main())
    except Exception as e:
        print(f"❌ Botda xəta baş verdi: {e}")
