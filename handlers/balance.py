import json
import os
import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from translations import get_text
from config import CARD_NUMBER, ADMIN_ID
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from handlers.payment import send_receipt_to_admin
from handlers.balance_utils import get_balance, set_balance, add_balance
from handlers.start import get_main_buttons

router = Router()
BALANCE_FILE = "user_balance.json"

@router.message(F.text == "/balance")
async def balance_query(message: Message):
    if message.from_user is None:
        await message.answer("İstifadəçi məlumatı tapılmadı.")
        return
    user_id = message.from_user.id
    balance = get_balance(user_id)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=get_text("show_balance_btn"), callback_data="show_balance")],
            [InlineKeyboardButton(text=get_text("fill_balance_btn"), callback_data="fill_balance")]
        ]
    )
    await message.answer(get_text("your_balance").format(balance=balance), reply_markup=keyboard)

@router.message(StateFilter("waiting_recipient_id"))
async def recipient_id_handler(message: Message, state: FSMContext):
    recipient_id = message.text.strip()
    if not recipient_id.isdigit():
        await message.answer(get_text("invalid_id"))
        return
    sender_id = message.from_user.id
    if int(recipient_id) == sender_id:
        await message.answer(get_text("cannot_send_to_self"))
        return
    balance = get_balance(sender_id)
    if balance < 10:
        await message.answer(get_text("not_enough_balance"))
        await state.clear()
        return
    await state.update_data(recipient_id=int(recipient_id))
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=get_text("confirm_send_btn"), callback_data="confirm_send_rbcrypt")],
            [InlineKeyboardButton(text=get_text("cancel_btn"), callback_data="cancel_send_rbcrypt")],
            [InlineKeyboardButton(text="🏠 Əsas menyuya qayıt", callback_data="main_menu")],
        ]
    )
    await message.answer(get_text("confirm_send_text").format(recipient_id=recipient_id), reply_markup=keyboard)
    await state.set_state("waiting_send_confirm")

@router.callback_query(F.data == "confirm_send_rbcrypt")
async def confirm_send_rbcrypt_callback(callback: CallbackQuery, state: FSMContext):
    pass

@router.callback_query(F.data == "cancel_send_rbcrypt")
async def cancel_send_rbcrypt_callback(callback: CallbackQuery, state: FSMContext):
    pass

@router.callback_query(F.data == "show_balance")
async def show_balance_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    balance = get_balance(user_id)
    if callback.message is not None:
        msg = await callback.message.answer(f"Sizin balansınız: {balance} RBCron")
        await asyncio.sleep(5)
        try:
            await msg.delete()
        except Exception:
            pass
    await callback.answer()

@router.callback_query(F.data == "fill_balance")
async def fill_balance_callback(callback: CallbackQuery):
    if callback.message is not None:
        user_id = callback.from_user.id
        balance = get_balance(user_id)
        await callback.message.answer(
            f"Balansınızı artırmaq üçün aşağıdakı karta ödəniş edin:\n\n"
            f"<b>Kart nömrəsi:</b> <code>{CARD_NUMBER}</code>\n\n"
            "<b>Paketlər və qiymətlər:</b>\n"
            "100 RBCron — 3 AZN\n"
            "250 RBCron — 5 AZN\n"
            "750 RBCron — 10 AZN\n"
            "1500 RBCron — 20 AZN\n\n"
            f"💰 Cari balansınız: <b>{balance} RBCron</b>\n\n"
            "Ödəniş etdikdən sonra qəbzin şəklini buraya, mənə göndərin.\n"
            "Qəbz təsdiqləndikdən sonra balansınız artırılacaq.\n"
            "Təsdiq adətən 24 saat ərzində baş verir.\n"
            "Anlayışınız üçün təşəkkür edirik.",
            parse_mode="HTML"
        )
    await callback.answer()

class BalanceForm:
    waiting_receipt = "waiting_receipt"
    waiting_reject_reason = "waiting_reject_reason"

@router.message(F.text.regexp(r"^\d+$").as_("amount"))
async def deposit_amount(message: Message, state: FSMContext):
    # Əgər ayrıca məbləğ istəsəniz, bu handleri istifadə edə bilərsiniz
    pass

@router.message(F.text == "Qəbz göndər")
async def ask_receipt(message: Message, state: FSMContext):
    await state.set_state(BalanceForm.waiting_receipt)
    await message.answer("Ödəniş qəbzinin şəklini göndərin:")

@router.message(StateFilter(BalanceForm.waiting_receipt))
async def receipt_handler(message: Message, state: FSMContext):
    if message.from_user is None:
        await message.answer("İstifadəçi məlumatı tapılmadı.")
        return
    user_id = message.from_user.id
    if not message.photo:
        await message.answer("Zəhmət olmasa, ödəniş qəbzinin şəklini göndərin.")
        return
    photo_id = message.photo[-1].file_id
    await send_receipt_to_admin(message.bot, user_id, photo_id)
    await message.answer("📥 Ödəniş qəbzi qəbul edildi! Admin təsdiqləyəndən sonra xəbər veriləcək.")
    await state.clear()

@router.callback_query(F.data.startswith("balance_confirm_"))
async def balance_confirm_callback(callback: CallbackQuery):
    # balance_confirm_{user_id}_{coin_amount}
    if callback.data is None:
        if callback.message is not None:
            await callback.message.answer("Callback data tapılmadı.")
        await callback.answer()
        return
    parts = callback.data.split("_")
    user_id = int(parts[2])
    coin_amount = int(parts[3])
    add_balance(user_id, coin_amount)
    bot_instance = callback.bot if hasattr(callback, "bot") and callback.bot is not None else getattr(callback, "bot", None)
    if bot_instance is not None:
        await bot_instance.send_message(
            user_id,
            f"Ödəniş təsdiqləndi! Balansınız artırıldı: +{coin_amount} RBCron\nYeni balans: {get_balance(user_id)} RBCron"
        )
    else:
        if callback.message is not None:
            await callback.message.answer("Bot instance tapılmadı, mesaj göndərilə bilmədi.")
    if callback.message is not None:
        await callback.message.answer(f"Təsdiqləndi və istifadəçiyə {coin_amount} RBCron əlavə olundu.")
    await callback.answer()

@router.callback_query(F.data.startswith("balance_reject_"))
async def balance_reject_callback(callback: CallbackQuery, state: FSMContext):
    if callback.data is None:
        if callback.message is not None:
            await callback.message.answer("Callback data tapılmadı.")
        await callback.answer()
        return
    user_id = int(callback.data.split("_")[-1])
    await state.set_state(BalanceForm.waiting_reject_reason)
    await state.update_data(reject_user_id=user_id)
    if callback.message is not None:
        await callback.message.answer("Rədd səbəbini yazın:")
    await callback.answer()
    await state.set_state(BalanceForm.waiting_reject_reason)
    await state.update_data(reject_user_id=user_id)
    if callback.message is not None:
        await callback.message.answer("Rədd səbəbini yazın:")
    await callback.answer()

@router.message(StateFilter(BalanceForm.waiting_reject_reason))
async def reject_reason_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get("reject_user_id")
    reason = message.text
    if user_id is not None:
        bot_instance = message.bot if message.bot is not None else getattr(message, "bot", None)
        if bot_instance is not None:
            await bot_instance.send_message(
                user_id,
                f"Ödəniş admin tərəfindən rədd edildi.\nSəbəb: {reason}"
            )
            await message.answer("Rədd səbəbi istifadəçiyə göndərildi.")
        else:
            await message.answer("Bot instance tapılmadı, mesaj göndərilə bilmədi.")
    else:
        await message.answer("İstifadəçi ID tapılmadı, mesaj göndərilə bilmədi.")
    await state.clear()

@router.callback_query(F.data == "main_menu")
async def main_menu_callback(callback: CallbackQuery, state: FSMContext):
    if callback.message:
        await callback.message.answer("Aşağıdakı seçimlərdən birini seçin və bütün funksiyalara rahat giriş əldə edin:", reply_markup=get_main_buttons())
    await callback.answer()

async def send_receipt_to_admin(bot, user_id, photo_id):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="100 RBCron (3 AZN)", callback_data=f"balance_confirm_{user_id}_100")],
            [InlineKeyboardButton(text="250 RBCron (5 AZN)", callback_data=f"balance_confirm_{user_id}_250")],
            [InlineKeyboardButton(text="750 RBCron (10 AZN)", callback_data=f"balance_confirm_{user_id}_750")],
            [InlineKeyboardButton(text="1500 RBCron (20 AZN)", callback_data=f"balance_confirm_{user_id}_1500")],
            [InlineKeyboardButton(text="Rədd et", callback_data=f"balance_reject_{user_id}")]
        ]
    )
    await bot.send_photo(
        ADMIN_ID,
        photo=photo_id,
        caption=(
            f"Balans artırmaq üçün yeni ödəniş: Telegram ID: {user_id}\n"
            "Ödəniş seçimləri:\n"
            "100 RBCron — 3 AZN\n"
            "250 RBCron — 5 AZN\n"
            "750 RBCron — 10 AZN\n"
            "1500 RBCron — 20 AZN"
        ),
        reply_markup=keyboard
    )