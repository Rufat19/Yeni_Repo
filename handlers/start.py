from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
import datetime
import asyncio
from database.queries import add_user
from database import get_all_news, get_news_by_id
from utils.logger_utils import log_event
from config import ADMIN_ID, APP_VERSION

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
    rows = [
        [
            InlineKeyboardButton(text="⚡ Əmsal Oyunu", callback_data="fast_test_start"),
            InlineKeyboardButton(text="🕹️ Köstəbək Oyunu", callback_data="game_info"),
        ],
        [
            InlineKeyboardButton(text="🌐 Sosial Mühit", callback_data="channel_access_menu"),
            InlineKeyboardButton(text="🆕 Yeniliklər", callback_data="news_menu"),
        ],
        [
            InlineKeyboardButton(text="🌍 Dünya Görüşü (quiz)", callback_data="quiz_world_menu"),
            InlineKeyboardButton(text="🧾 Sosial ödənişlər", callback_data="quiz"),
        ],
        [
            InlineKeyboardButton(text="📊 Power BI Sertifikat", callback_data="cert_menu"),
            InlineKeyboardButton(text="📄 Müsahibə Texnikası", callback_data="get_pdf"),
        ],
        [
            InlineKeyboardButton(text="💳 RBCron balansım", callback_data="balance_menu"),
            InlineKeyboardButton(text="🌟 İstifadəçi rəyləri", callback_data="reviews_menu"),
        ],
        [
            InlineKeyboardButton(text="🛠️ Bot sifarişi", callback_data="order_bot"),
            InlineKeyboardButton(text="ℹ️ Qəbul Mərkəzləri", callback_data="about_bot"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


# /start komandası
@router.message(F.text == "/start")
async def start_menu(message: Message, state: FSMContext):
    if message.chat.type != "private":
        if message.from_user is not None:
            try:
                me = await message.bot.get_me()
                username = getattr(me, "username", "")
                open_link = f"https://t.me/{username}" if username else "https://t.me/"
            except Exception:
                open_link = "https://t.me/"
            await message.reply(
                "ℹ️ Botun əsas menyusunu açmaq üçün şəxsi mesajda (/start) yazın.\n\n👉 "
                f"<a href='{open_link}'>Botu aç</a>",
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
                    f"🔔 Yeni istifadəçi gəldi — bot işə düşdü!\n"
                    f"👤 {display_name} (id: {user.id})\n"
                    f"🕒 {now}\n"
                    f"🌐 Lang: {lang}"
                )
                try:
                    await message.bot.send_message(ADMIN_ID, admin_text)
                except Exception:
                    pass
        except Exception as e:
            print(f"[LOG ERROR] {e}")

    # 🔸 1. Səmimi salam və qısa izah
    greeting = (
        "👋 Salam! Xoş gəlmisiniz — burada istədiyiniz hər şey bir yerdə!\n\n"
        "🧭 Quizlər, oyunlar, faydalı kanallar və balans əməliyyatları — hamısı asan istifadə üçün hazırlanıb.\n"
        "Aşağıdan bir bölmə seçin, mən sizi yönləndirərəm!"
    )
    await message.answer(greeting)

    # 🔸 2. Qısa təqdimat videosu
    try:
        video = FSInputFile("media/about_bot.mp4")
        await message.answer_video(
            video,
            caption=(
                "<b>🎬 Qısa tanıtım</b>\n"
                "Bu bot kim üçündür və nələr edə bilir?\n"
                "<i>25 saniyəyə hər şey aydın olacaq. Səsi aç 😉</i>"
            ),
            parse_mode="HTML",
        )
    except Exception as e:
        print(f"[VIDEO ERROR] {e}")

    # 🔸 3. 2 saniyə gözləyir və əsas menyunu göstərir
    await asyncio.sleep(2)

    intro = "👇 İndi bir seçim edin — sürətli və rahat giriş üçün düymələr:"
    await message.answer(intro, reply_markup=get_main_buttons())


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
    await callback.message.answer("🆕 Yeniliklər — son paylaşımlar:", reply_markup=kb)
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


# 💰 RBCron menyusu (qısa yol)
@router.callback_query(F.data == "balance_menu")
async def balance_menu_callback(callback: CallbackQuery):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👛 Balansı göstər", callback_data="show_balance"),
                InlineKeyboardButton(text="💳 Balansı artır", callback_data="fill_balance"),
            ],
            [InlineKeyboardButton(text="🏠 Əsas menyuya qayıt", callback_data="main_menu")],
        ]
    )
    text = (
        "💡 <b>RBCron nədir?</b>\n"
        "RBCron — bot daxilində əməliyyat valyutasıdır. Testlər, quizlər, ödənişli kanallar və premium funksiyalarda istifadə olunur.\n\n"
        "🎯 <b>Niyə balansı artırmaq sərfəlidir?</b>\n"
        "• Çox yüklədikcə vahid qiymət <b>daha ucuz</b> olur.\n"
        "• Testlər, quizlər və digər ödəniş tələb edən bölmələrdə <b>endirimli istifadə</b>.\n"
        "• Kampaniya və xüsusi paketlər üçün hazır balans.\n\n"
        "👇 Aşağıdan seçim edin: balansınıza baxın və ya artırın."
    )
    await callback.message.answer(text, parse_mode="HTML", reply_markup=kb)
    await callback.answer()


# 🕹️ Köstəbək oyunu haqqında məlumat (qısa yol)
@router.callback_query(F.data == "game_info")
async def game_info_callback(callback: CallbackQuery):
    text = (
        "🕹️ <b>Köstəbək — komanda oyunu</b>\n"
        "━━━━━━━━━━━━\n"
        "• Qrupda <code>/game</code> yazın (bot admin olmalıdır).\n"
        f"• Minimum <b>{3}</b> nəfər tələb olunur.\n"
        "• Hamıya eyni söz, birinə fərqli söz düşür.\n"
        "• Təsvir edin, şübhəlini tapın, səs verin!\n\n"
        "😉 Eğlənmək üçün dostlarınızı dəvət edin!"
    )
    try:
        me = await callback.bot.get_me()
        username = getattr(me, "username", "")
        startgroup_url = f"https://t.me/{username}?startgroup=true" if username else "https://t.me/"
    except Exception:
        startgroup_url = "https://t.me/"
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Qrupa əlavə et", url=startgroup_url)],
            [InlineKeyboardButton(text="🎮 İctimai qrupda oyna", url="https://t.me/kostebeksen")],
            [InlineKeyboardButton(text="🏠 Əsas menyuya qayıt", callback_data="main_menu")],
        ]
    )
    await callback.message.answer(text, parse_mode="HTML", reply_markup=kb)
    await callback.answer()
