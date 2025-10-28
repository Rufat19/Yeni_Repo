from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
import time
from handlers.balance_utils import get_balance, set_balance  # balans funksiyaları
from handlers.start import get_main_buttons  # Əsas menyu düymələri

router = Router()


CHANNELS = {

    "sosial_muhit": {
        "chat_id": -1002299496126,
        "title": "Sosial Mühit",
        "price": 0,
        "description": (
            "📌 Sosial Mühit kanalı — Rüfət Babayev tərəfindən yaradılmış peşəkar platforma\n\n"
            "Burada sosial sahə üzrə qanunvericiliklə bağlı bütün PDF sənədləri bir araya toplanıb. Kanal vasitəsilə siz:\n\n"
            "✅ Pensiyaların illər üzrə indeksləşmə əmsallarını,\n"
            "✅ İstifadə olunmayan kapitalın indeksləşmə qaydalarını,\n"
            "✅ Təqaüdlərlə bağlı Fərman və tarixləri,\n"
            "✅ Müavinətlərin məbləğləri və yenilənmiş göstəricilərini,\n"
            "✅ Habelə edilmiş dəyişikliklərlə bağlı digər faydalı məlumatları tapa bilərsiniz.\n\n"
            "🔗 Sosial sahədə çalışan mütəxəssislər üçün etibarlı bilik məkanı – Sosial Mühit"
        )
    }
}


# Kanal seçimi menyusu
@router.callback_query(F.data == "channel_access_menu")
async def channel_access_menu(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    balance = get_balance(user_id)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[

            [InlineKeyboardButton(text="🌐 Sosial Mühit", callback_data="info_sosial_muhit")],
            [InlineKeyboardButton(text="🏠 Əsas menyuya qayıt", callback_data="main_menu")]
        ]
    )
    msg = f"Kanal seçin:\n\nCari balansınız: {balance} RBCron"
    await callback.message.answer(msg, reply_markup=keyboard)
    await callback.answer()

# Kanal haqqında info və ödəniş təsdiqi
@router.callback_query(lambda c: c.data in ["info_excel", "info_sosial_muhit"])
async def channel_info_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    key = "excel" if callback.data == "info_excel" else "sosial_muhit"
    data = CHANNELS[key]
    balance = get_balance(user_id)
    msg = (
        f"{data['description']}\n\n"
        f"Kanal: {data['title']}\n"
        f"Giriş üçün çıxılacaq məbləğ: {data['price']} RBCron\n"
        f"Cari balansınız: {balance} RBCron\n\n"
        f"Davam etmək üçün aşağıdakı düyməyə basın."
    )
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Giriş et", callback_data=f"access_{key}")],
            [InlineKeyboardButton(text="💳 Balansı artır", callback_data="fill_balance")],
            [InlineKeyboardButton(text="🏠 Əsas menyuya qayıt", callback_data="main_menu")]
        ]
    )
    await callback.message.answer(msg, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(lambda c: c.data in ["access_sosial_muhit"])
async def access_channel(callback: CallbackQuery):
    user_id = callback.from_user.id
    key = "sosial_muhit"
    data = CHANNELS[key]
    balance = get_balance(user_id)
    if balance < data["price"]:
        await callback.message.answer(
            f"⚠️ Balansınız yetərli deyil!\nBu kanal üçün {data['price']} RBCron lazımdır."
        )
        await callback.answer()
        return
    set_balance(user_id, balance - data["price"])
    try:
        invite = await callback.bot.create_chat_invite_link(
            chat_id=data["chat_id"],
            expire_date=int(time.time()) + 7 * 24 * 3600,  # 7 gün
            member_limit=1
        )
        await callback.message.answer(
            f"✅ Qeydiyyat uğurlu!\n\n"
            f"📌 Kanal: {data['title']}\n"
            f"🔗 Linkiniz: {invite.invite_link}\n"
            f"💰 Yeni balansınız: {get_balance(user_id)} RBCron"
        )
    except Exception as e:
        await callback.message.answer(f"❌ Link yaradıla bilmədi.\nSəbəb: {e}")
    await callback.answer()

@router.callback_query(F.data == "main_menu")
async def main_menu_callback(callback: CallbackQuery, state: FSMContext):
    if callback.message:
        await callback.message.answer("Aşağıdakı seçimlərdən birini seçin və bütün funksiyalara rahat giriş əldə edin:", reply_markup=get_main_buttons())
    await callback.answer()
