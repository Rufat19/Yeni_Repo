from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
import datetime
import asyncio
from database.queries import add_user, get_all_news, get_news_by_id
from utils.logger_utils import log_event
from config import ADMIN_ID

router = Router()


# Kanal seçimi callback
@router.callback_query(F.data == "channels")
async def channels_callback(callback: CallbackQuery, state: FSMContext):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Sosial Mühit", callback_data="channel_sosial_muhit")]
        ]
    )
    if callback.message is not None:
        await callback.message.answer("Kanala daxil olmaq üçün aşağıdakı düyməyə basın:", reply_markup=keyboard)
    await callback.answer()


# İstifadəçi start tarixçəsini log fayla yazır
def log_user_start(user_id):
    with open("user_start_history.log", "a", encoding="utf-8") as f:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"{user_id}|{now}\n")


# Əsas menyu düymələri
def get_main_buttons():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⚡ Əmsal Oyunu", callback_data="fast_test_start")],
            [InlineKeyboardButton(text="🏆 Sosial Mühit kanalına daxil ol", callback_data="channel_access_menu")],
            [InlineKeyboardButton(text="🌍 Dünya Görüşü- quiz paketlər", callback_data="quiz_world_menu")],
            [InlineKeyboardButton(text="📊 Power BI Sertifikat Testləri", callback_data="cert_menu")],
            [InlineKeyboardButton(text="📦 Sosial ödənişlər- quiz paketlər", callback_data="quiz")],
            [InlineKeyboardButton(text="📄 Müsahibələrə Hazırlıq Texnikası", callback_data="get_pdf")],
            [InlineKeyboardButton(text="🆕 Yeniliklər", callback_data="news_menu")],
            [InlineKeyboardButton(text="🕹️ Komanda Köstəbək Oyunu", callback_data="game_info")],
            [InlineKeyboardButton(text="🛠️ Bot sifarişi (depozit)", callback_data="order_bot")],
            [InlineKeyboardButton(text="💰 RBCron balansım", callback_data="balance_menu")],
            [InlineKeyboardButton(text="🌟 İstifadəçi rəyləri", callback_data="reviews_menu")],
            [InlineKeyboardButton(text="ℹ️ Qəbul Mərkəzləri haqqında", callback_data="about_bot")]
        ]
    )


# /start komandası
@router.message(F.text == "/start")
async def start_menu(message: Message, state: FSMContext):
    if message.chat.type != "private":
        if message.from_user is not None:
            await message.reply(
                "ℹ️ Botun əsas menyusunu açmaq üçün şəxsi mesajda (/start) yazın.\n\n👉 "
                f"<a href='https://t.me/{message.bot.username}'>Botu aç</a>",
                parse_mode="HTML"
            )
        return

    if message.from_user is not None:
        log_user_start(message.from_user.id)

        # 🔹 İstifadəçi əlavə et (lokal JSON-a)
        try:
            add_user(
                user_id=message.from_user.id,
                name=message.from_user.full_name or message.from_user.username or "Unknown",
                lang=message.from_user.language_code or "unknown"
            )
        except Exception as e:
            print(f"[DB ERROR] add_user failed: {e}")

        # 🔹 Aktivlik logu və adminə məlumat
        try:
            user = message.from_user
            display_name = user.full_name or user.username or str(user.id)
            lang = getattr(user, "language_code", None) or "unknown"
            log_event(user.id, display_name, "start", lang)

            if ADMIN_ID:
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                admin_text = (
                    f"🔔 Yeni istifadəçi botu işə saldı:\n"
                    f"👤 {display_name} (id: {user.id})\n"
                    f"🕒 {now}\n"
                    f"🌐 lang: {lang}"
                )
                try:
                    await message.bot.send_message(ADMIN_ID, admin_text)
                except Exception:
                    pass
        except Exception as e:
            print(f"[LOG ERROR] {e}")

    # 🔸 1. Təqdimat videosu
    try:
        video = FSInputFile("media/about_bot.mp4")
        await message.answer_video(
            video,
            caption="🎬 Qısaca təqdimat: Bot nələr edə bilir?",
        )
    except Exception as e:
        print(f"[VIDEO ERROR] {e}")

    # 🔸 2. 5 saniyə gözləyir və menyunu göstərir
    await asyncio.sleep(5)

    await message.answer(
        "Aşağıdakı seçimlərdən birini seçin və bütün funksiyalara rahat giriş əldə edin:",
        reply_markup=get_main_buttons()
    )


# ✅ YENİLİKLƏR (lokal işlək versiya)
@router.callback_query(F.data == "news_menu")
async def news_menu_callback(callback: CallbackQuery):
    try:
        news_list = get_all_news()
    except Exception as e:
        await callback.message.answer(f"⚠️ Yaxın zamanda:\n{e}")
        await callback.answer()
        return

    if not news_list:
        await callback.message.answer("📭 Hələ ki, yenilik yoxdur.")
        await callback.answer()
        return

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=n['title'], callback_data=f"read_news:{n['id']}")]
            for n in news_list
        ]
    )
    await callback.message.answer("🆕 Bütün yeniliklər:", reply_markup=kb)
    await callback.answer()


# ✅ Xəbəri oxuma callback
@router.callback_query(F.data.startswith("read_news:"))
async def read_news_callback(callback: CallbackQuery):
    try:
        news_id = int(callback.data.split(":")[1])
        news = get_news_by_id(news_id)
        if not news:
            await callback.message.answer("❌ Yenilik tapılmadı.")
            return

        await callback.message.answer(
            f"📰 <b>{news['title']}</b>\n\n{news['content']}",
            parse_mode="HTML"
        )
    except Exception as e:
        await callback.message.answer(f"⚠️ Xəbəri oxumaq mümkün olmadı:\n{e}")
    await callback.answer()
main_menu_keyboard = get_main_buttons()
