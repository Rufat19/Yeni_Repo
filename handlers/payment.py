from aiogram import Router, F
from aiogram.types import Message, ContentType, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from config import ADMIN_ID
from database.db import get_db_connection
from handlers.balance_utils import get_balance, set_balance, add_balance

payment_router = Router()

async def send_receipt_to_admin(bot, user_id, photo_id):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Təsdiqlə", callback_data=f"payment_confirm_{user_id}")],
            [InlineKeyboardButton(text="Rədd et", callback_data=f"payment_reject_{user_id}")]
        ]
    )
    await bot.send_photo(
        ADMIN_ID,
        photo=photo_id,
        caption=(
            f"Balans artırmaq üçün yeni ödəniş:\n"
            f"Telegram ID: {user_id}\n"
            "100 RBCron — 3 AZN\n"
            "250 RBCron — 5 AZN\n"
            "750 RBCron — 10 AZN\n"
            "1500 RBCron — 20 AZN\n\n"
        ),
        reply_markup=keyboard
    )

@payment_router.message(F.photo)
async def payment_screenshot(message: Message):
    if message.from_user is None:
        await message.answer("Xəta baş verdi: istifadəçi məlumatı tapılmadı.")
        return

    user_id = message.from_user.id
    caption = message.caption or "Naməlum məhsul"
    
    with get_db_connection() as conn:
        conn.execute("""
            INSERT INTO orders (user_id, name, phone, product_name, color, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, message.from_user.full_name, "Yox", caption, "Naməlum", "Ödəniş gözləyir"))
        conn.commit()
    
    await message.answer(
        "📥 Ödəniş qəbzi qəbul edildi! Admin təsdiqləyəndən sonra xəbər veriləcək."
    )
    if message.photo and len(message.photo) > 0:
        await send_receipt_to_admin(message.bot, user_id, message.photo[-1].file_id)
    else:
        await message.answer("Xəta baş verdi: foto tapılmadı.")

@payment_router.callback_query(F.data.startswith("payment_confirm_"))
async def payment_confirm_callback(callback: CallbackQuery, state: FSMContext):
    if callback.data is None:
        if callback.message is not None:
            await callback.message.answer("Xəta baş verdi: callback data tapılmadı.")
        await callback.answer()
        return
    user_id = int(callback.data.split("_")[-1])
    await state.set_state("waiting_manual_coin")
    await state.update_data(manual_user_id=user_id)
    if callback.message is not None:
        await callback.message.answer("Coin sayını daxil edin:")
    await callback.answer()

@payment_router.message(StateFilter("waiting_manual_coin"))
async def manual_coin_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    manual_user_id = data.get("manual_user_id")
    if manual_user_id is None:
        await message.answer("Xəta baş verdi: istifadəçi ID tapılmadı.")
        return
    user_id = int(manual_user_id)
    if message.text is None:
        await message.answer("Xəta baş verdi: mesaj mətnini tapmaq olmadı.")
        return
    try:
        coin_amount = int(message.text)
    except ValueError:
        await message.answer("Yalnız rəqəm daxil edin!")
        return
    add_balance(user_id, coin_amount)
    bot = getattr(message, "bot", None)
    main_menu_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Əsas menyuya qayıt", callback_data="main_menu")]
        ]
    )
    if bot is not None:
        await bot.send_message(
            user_id,
            f"Ödəniş təsdiqləndi! Balansınız artırıldı: +{coin_amount} RBCron\nYeni balans: {get_balance(user_id)} RBCron",
            reply_markup=main_menu_keyboard
        )
        await message.answer(f"Təsdiqləndi və istifadəçiyə {coin_amount} RBCron əlavə olundu.", reply_markup=main_menu_keyboard)
    else:
        await message.answer("Xəta baş verdi: bot instance tapılmadı.", reply_markup=main_menu_keyboard)
    await state.clear()

@payment_router.callback_query(F.data.startswith("payment_reject_"))
async def payment_reject_callback(callback: CallbackQuery, state: FSMContext):
    if callback.data is None:
        if callback.message is not None:
            await callback.message.answer("Xəta baş verdi: callback data tapılmadı.")
        await callback.answer()
        return
    user_id = int(callback.data.split("_")[-1])
    await state.set_state("waiting_payment_reject_reason")
    await state.update_data(reject_user_id=user_id)
    if callback.message is not None:
        await callback.message.answer("Rədd səbəbini yazın:")
    await callback.answer()

@payment_router.message(StateFilter("waiting_payment_reject_reason"))
async def payment_reject_reason_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get("reject_user_id")
    reason = message.text
    main_menu_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Əsas menyuya qayıt", callback_data="main_menu")]
        ]
    )
    if user_id is not None:
        bot = message.bot
        if bot is not None:
            await bot.send_message(
                user_id,
                f"Ödəniş admin tərəfindən rədd edildi.\nSəbəb: {reason}",
                reply_markup=main_menu_keyboard
            )
            await message.answer("Rədd səbəbi istifadəçiyə göndərildi.", reply_markup=main_menu_keyboard)
        else:
            await message.answer("Xəta baş verdi: bot instance tapılmadı.", reply_markup=main_menu_keyboard)
    else:
        await message.answer("Xəta baş verdi: istifadəçi ID tapılmadı.", reply_markup=main_menu_keyboard)
    await state.clear()
