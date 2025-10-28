import json
import os
from datetime import datetime

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import ADMIN_ID
from handlers.balance_utils import get_balance, set_balance, add_balance

router = Router()

class OrderBotForm(StatesGroup):
    waiting_user_info = State()
    waiting_confirm = State()
    waiting_details = State()
    waiting_admin_reason = State()

# --- köməkçi funksiya ---
def save_order_to_file(user_id: int, full_name: str, phone: str, details: str):
    order_data = {
        "user_id": user_id,
        "full_name": full_name,
        "phone": phone,
        "details": details,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    file_path = "orders.json"
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                orders = json.load(f)
            except json.JSONDecodeError:
                orders = []
    else:
        orders = []

    orders.append(order_data)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(orders, f, indent=4, ensure_ascii=False)


# --- sifariş başlanğıcı ---
@router.callback_query(F.data == "order_bot")
async def order_bot_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "📋 Sifariş üçün məlumatları daxil edin:\n\n"
        "Ad, soyad, əlaqə nömrəsi yazın.",
        parse_mode="HTML"
    )
    await state.set_state(OrderBotForm.waiting_user_info)
    await callback.answer()


# --- istifadəçi məlumatı ---
@router.message(OrderBotForm.waiting_user_info)
async def order_bot_user_info(message: Message, state: FSMContext):
    # İstifadəçi istənilən formada məlumat daxil edə bilər
    await state.update_data(full_name=message.text, phone="Sərbəst qeyd")

    user_id = message.from_user.id
    current_balance = get_balance(user_id)
    info = (
        "<b>🤖 Bot Sifarişi – Depozit Şərtləri</b>\n\n"
        "• Sifariş üçün ilkin depozit: <b>1000 RBCron</b>.\n"
        "• Bu məbləğ sifarişlərin ciddi qəbul olunması üçün təminat xarakteri daşıyır.\n"
        "• Botun yekun qiyməti və hazırlanma müddəti barədə əlavə məlumatı Admin təqdim edəcək.\n"
        "• Sifariş təsdiqlənməzsə, depozit tam şəkildə balansınıza qaytarılacaq.\n\n"
        f"💰 Cari balansınız: <b>{current_balance} RBCron</b>\n\n"
        "👉 Əgər şərtlərlə razısınızsa, balansınızdan 1000 RBCron çıxılacaq və sizdən sifariş detallarını təqdim etməyiniz xahiş olunacaq.\n"
        "Bu proses qarşılıqlı öhdəlikləri təsdiq edən müqavilə xarakterli addım hesab olunur."
    )
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Şərtlərlə razıyam", callback_data="order_bot_confirm")],
            [InlineKeyboardButton(text="💳 Balansı artır", callback_data="fill_balance")],
            [InlineKeyboardButton(text="🏠 Əsas menyuya qayıt", callback_data="main_menu")]
        ]
    )
    await message.answer(info, reply_markup=keyboard, parse_mode="HTML")
    await state.set_state(OrderBotForm.waiting_confirm)


# --- təsdiq mərhələsi ---
@router.callback_query(F.data == "order_bot_confirm")
async def order_bot_confirm(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    balance = get_balance(user_id)

    if balance < 1000:
        await callback.message.answer(
            "⚠️ <b>Yetərli balans yoxdur.</b>\n"
            "Bot sifarişi üçün <b>1000 RBCron</b> tələb olunur.",
            parse_mode="HTML"
        )
        await state.clear()
        await callback.answer()
        return

    set_balance(user_id, balance - 1000)
    new_balance = get_balance(user_id)
    await callback.message.answer(
        f"✅ Depozit çıxıldı.\n\n"
        f"Cari balansınız: <b>{new_balance} RBCron</b>\n\n"
        "Zəhmət olmasa sifarişinizin detalları barədə məlumat verin:\n"
        "• Botun əsas məqsədi\n"
        "• İstədiyiniz funksiyalar\n"
        "• Əlavə qeydlər",
        parse_mode="HTML"
    )
    await state.set_state(OrderBotForm.waiting_details)
    await callback.answer()


@router.callback_query(F.data == "order_bot_decline")
async def order_bot_decline(callback: CallbackQuery, state: FSMContext):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Əsas menyuya qayıt", callback_data="main_menu")]
        ]
    )
    await callback.message.answer("ℹ️ Sifariş ləğv edildi. Balansınızdan heç bir vəsait çıxılmadı.", reply_markup=keyboard)
    await state.clear()
    await callback.answer()


# --- sifariş detallarının alınması ---
@router.message(OrderBotForm.waiting_details)
async def order_bot_details(message: Message, state: FSMContext):
    user_id = message.from_user.id
    details = message.text
    data = await state.get_data()
    full_name = data.get("full_name")
    phone = data.get("phone")

    # fayla yazırıq
    save_order_to_file(user_id, full_name, phone, details)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Təsdiqlə", callback_data=f"order_bot_admin_confirm_{user_id}")],
            [InlineKeyboardButton(text="❌ Rədd et", callback_data=f"order_bot_admin_reject_{user_id}")]
        ]
    )

    if ADMIN_ID:
        await message.bot.send_message(
            ADMIN_ID,
            f"📩 <b>Yeni bot sifarişi</b>\n"
            f"👤 İstifadəçi ID: {user_id}\n"
            f"👤 Ad Soyad: {full_name}\n"
            f"📞 Əlaqə: {phone}\n"
            f"📝 Detallar: {details}",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        await message.answer("✅ Sifarişiniz adminə göndərildi.\nQısa müddət ərzində cavab təqdim ediləcək.")
    else:
        await message.answer("⚠️ Admin ID tapılmadı. Sifarişiniz göndərilə bilmədi.")

    await state.clear()


# --- admin rədd ---
@router.callback_query(F.data.startswith("order_bot_admin_reject_"))
async def order_bot_admin_reject(callback: CallbackQuery, state: FSMContext):
    user_id = int(callback.data.split("_")[-1])
    await state.set_state(OrderBotForm.waiting_admin_reason)
    await state.update_data(reject_user_id=user_id)
    await callback.message.answer("❌ Rədd səbəbini daxil edin:")
    await callback.answer()


@router.message(OrderBotForm.waiting_admin_reason)
async def order_bot_admin_reason(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get("reject_user_id")
    reason = message.text
    add_balance(int(user_id), 1000)
    current_balance = get_balance(int(user_id))
    main_menu_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Əsas menyuya qayıt", callback_data="main_menu")]
        ]
    )
    await message.bot.send_message(
        int(user_id),
        f"❌ Sifarişiniz admin tərəfindən rədd edildi.\n"
        f"📌 Səbəb: {reason}\n"
        f"💰 Depozit (1000 RBCron) balansınıza geri qaytarıldı.\n"
        f"Cari balansınız: <b>{current_balance} RBCron</b>",
        parse_mode="HTML",
        reply_markup=main_menu_keyboard
    )
    await message.answer("ℹ️ Rədd səbəbi istifadəçiyə göndərildi və depozit qaytarıldı.", reply_markup=main_menu_keyboard)
    await state.clear()


# --- admin təsdiq ---
@router.callback_query(F.data.startswith("order_bot_admin_confirm_"))
async def order_bot_admin_confirm(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[-1])
    await callback.message.answer("✅ Sifariş təsdiqləndi və istifadəçiyə məlumat göndərildi.")
    await callback.bot.send_message(
        user_id,
        "✅ Sifarişiniz təsdiqləndi!\n"
        "Admin sizinlə əlaqə saxlayacaq və yekun şərtləri (qiymət, vaxt və s.) təqdim edəcək.\n"
        "Zəhmət olmasa əlaqə üçün aktiv qalın."
    )
    await callback.answer()
