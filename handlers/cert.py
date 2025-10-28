from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from handlers.balance_utils import get_balance, set_balance
from handlers.start import get_main_buttons

router = Router()

CERT_TOPICS = [
    ("PL300 First - Practice Test", "cert_pl300"),
    ("PL300 Second - Practice Test", "cert_pl300_2"),
    ("PL300 Third - Practice Test", "cert_pl300_3"),
    ("PL300 Fourth - Practice Test", "cert_pl300_4"),
]

CERT_LINKS = {
    "cert_pl300": "https://t.me/Allien_BiBot/first_pl300",
    "cert_pl300_2": "https://t.me/Allien_BiBot/second_pl300",
    "cert_pl300_3": "https://t.me/Allien_BiBot/third_pl300",
    "cert_pl300_4": "https://t.me/Allien_BiBot/fourth_pl300",
}

@router.callback_query(F.data == "cert_menu")
async def cert_menu_callback(callback: CallbackQuery, state: FSMContext):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=
            [[InlineKeyboardButton(text=topic, callback_data=cb)] for topic, cb in CERT_TOPICS] +
            [[InlineKeyboardButton(text="🏠 Əsas menyuya qayıt", callback_data="main_menu")]]
    )
    if callback.message:
        await callback.message.answer("Power BI və analitik alətlər üzrə sertifikat testini seçin:", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.in_([cb for _, cb in CERT_TOPICS]))
async def cert_topic_selected(callback: CallbackQuery, state: FSMContext):
    await state.update_data(cert_topic=callback.data)
    price = 300
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Razıyam", callback_data="cert_accept"),
                InlineKeyboardButton(text="💳 Balansı artır", callback_data="fill_balance")
            ],
            [InlineKeyboardButton(text="🏠 Əsas menyuya qayıt", callback_data="main_menu")]
        ]
    )
    if callback.message:
        await callback.message.answer(
            f"Bu əməliyyat üçün sizdən <b>{price} RBCron</b> çıxılacaq. Razısınız?",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    await state.update_data(cert_price=price)
    await callback.answer()

@router.callback_query(F.data == "cert_accept")
async def cert_accept_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    topic = data.get("cert_topic", "")
    user_id = callback.from_user.id
    coin_required = data.get("cert_price", 300)
    balance = get_balance(user_id)
    if balance < coin_required:
        if callback.message is not None:
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="💳 Balansı artır", callback_data="fill_balance")],
                    [InlineKeyboardButton(text="🏠 Əsas menyuya qayıt", callback_data="main_menu")]
                ]
            )
            await callback.message.answer(
                f"<b>Balansınızda kifayət qədər RBCron yoxdur.</b>\n"
                f"Testə giriş üçün <b>{coin_required} RBCron</b> lazımdır.\n"
                f"Balansınızı artırmaq üçün <b>Balansı artır</b> düyməsinə klikləyin.",
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        await state.clear()
        await callback.answer()
        return
    set_balance(user_id, balance - coin_required)
    link = CERT_LINKS.get(topic, "https://www.google.com")
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Testə başla", url=link)],
            [InlineKeyboardButton(text="🏠 Əsas menyuya qayıt", callback_data="main_menu")]
        ]
    )
    if callback.message is not None:
        await callback.message.answer(
            f"Testə giriş təsdiqləndi!\nBalansınızdan <b>{coin_required} RBCron</b> çıxıldı. Yeni balans: <b>{balance - coin_required} RBCron</b>",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    await state.clear()
    await callback.answer()

@router.callback_query(F.data == "cert_decline")
async def cert_decline_callback(callback: CallbackQuery, state: FSMContext):
    main_menu_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Əsas menyuya qayıt", callback_data="main_menu")]
        ]
    )
    if callback.message is not None:
        await callback.message.answer("Əməliyyat ləğv olundu. Balansınızdan heç nə çıxılmadı.", reply_markup=main_menu_kb)
    await state.clear()
    await callback.answer()

@router.callback_query(F.data == "main_menu")
async def main_menu_callback(callback: CallbackQuery, state: FSMContext):
    if callback.message:
        await callback.message.answer("Aşağıdakı seçimlərdən birini seçin və bütün funksiyalara rahat giriş əldə edin:", reply_markup=get_main_buttons())
    await callback.answer()

@router.callback_query(F.data.startswith("cert_reject_"))
async def cert_reject_callback(callback: CallbackQuery, state: FSMContext):
    if not callback.data:
        if callback.message:
            await callback.message.answer("Xəta baş verdi: callback məlumatı tapılmadı.")
        await callback.answer()
        return
    try:
        user_id = int(callback.data.split("_")[-1])
    except Exception:
        if callback.message:
            await callback.message.answer("Xəta baş verdi: istifadəçi ID tapılmadı.")
        await callback.answer()
        return
    await state.set_state("waiting_cert_reject_reason")
    await state.update_data(reject_user_id=user_id)
    if callback.message:
        await callback.message.answer("Rədd səbəbini yazın:")
    await callback.answer()

@router.message(StateFilter("waiting_cert_reject_reason"))
async def cert_reject_reason_handler(message: Message, state: FSMContext):
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
                f"Sertifikat testinə giriş admin tərəfindən rədd edildi.\nSəbəb: {reason}",
                reply_markup=main_menu_keyboard
            )
            await message.answer("Rədd səbəbi istifadəçiyə göndərildi.", reply_markup=main_menu_keyboard)
        else:
            await message.answer("Xəta baş verdi: bot instance tapılmadı.", reply_markup=main_menu_keyboard)
    else:
        await message.answer("Xəta baş verdi: istifadəçi ID tapılmadı.", reply_markup=main_menu_keyboard)
    await state.clear()
