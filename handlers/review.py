from handlers.start import get_main_buttons
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import json
import os

router = Router()

# Yeni "istifadəçi rəyləri" menyusu üçün handler
@router.callback_query(F.data == "reviews_menu")
async def reviews_menu_callback(callback: CallbackQuery, state: FSMContext):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Rəyini yaz və qiymətləndir", callback_data="review")],
            [InlineKeyboardButton(text="Bütün rəylərə bax", callback_data="show_reviews")],
            [InlineKeyboardButton(text="🏠 Əsas menyuya qayıt", callback_data="main_menu")]
        ]
    )
    if callback.message:
        await callback.message.answer("İstifadəçi rəyləri menyusu:", reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data == "main_menu")
async def main_menu_callback(callback: CallbackQuery, state: FSMContext):
    if callback.message:
        await callback.message.answer("Aşağıdakı seçimlərdən birini seçin və bütün funksiyalara rahat giriş əldə edin:", reply_markup=get_main_buttons())
    await callback.answer()

REVIEWS_FILE = "reviews.json"

class ReviewForm(StatesGroup):
    waiting_rating = State()
    waiting_text = State()

def save_review(user_id, rating, text, reply=None):
    reviews = []
    if os.path.exists(REVIEWS_FILE):
        with open(REVIEWS_FILE, "r", encoding="utf-8") as f:
            reviews = json.load(f)
    reviews.append({
        "user_id": user_id,
        "rating": rating,
        "text": text,
        "reply": reply
    })
    with open(REVIEWS_FILE, "w", encoding="utf-8") as f:
        json.dump(reviews, f, ensure_ascii=False, indent=2)

def get_all_reviews():
    if os.path.exists(REVIEWS_FILE):
        with open(REVIEWS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

@router.callback_query(F.data == "review")
async def review_callback(callback: CallbackQuery, state: FSMContext):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⭐⭐⭐⭐⭐", callback_data="rate_5")],
            [InlineKeyboardButton(text="⭐⭐⭐⭐", callback_data="rate_4")],
            [InlineKeyboardButton(text="⭐⭐⭐", callback_data="rate_3")],
            [InlineKeyboardButton(text="⭐⭐", callback_data="rate_2")],
            [InlineKeyboardButton(text="⭐", callback_data="rate_1")],
        ]
    )
    await state.set_state(ReviewForm.waiting_rating)
    if callback.message:
        await callback.message.answer("Qiymətləndirmə üçün ulduz seçin:", reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data.startswith("rate_"))
async def rate_callback(callback: CallbackQuery, state: FSMContext):
    if callback.data is not None:
        rating = int(callback.data.split("_")[1])
        await state.update_data(rating=rating)
        await state.set_state(ReviewForm.waiting_text)
        if callback.message:
            await callback.message.answer("Rəyinizi yazın:")
        await callback.answer()
    else:
        if callback.message:
            await callback.message.answer("Xəta baş verdi: rating məlumatı tapılmadı.")
        await callback.answer()

@router.message(ReviewForm.waiting_text)
async def review_text(message: Message, state: FSMContext):
    data = await state.get_data()
    rating = data.get("rating")
    text = message.text
    user_id = message.from_user.id if message.from_user else "unknown"
    save_review(user_id, rating, text)
    main_menu_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Əsas menyuya qayıt", callback_data="main_menu")]
        ]
    )
    await message.answer("Rəyiniz və qiymətləndirməniz üçün təşəkkürlər!", reply_markup=main_menu_kb)
    await state.clear()

@router.callback_query(F.data == "show_reviews")
async def show_reviews_callback(callback: CallbackQuery, state: FSMContext):
    import asyncio
    reviews = get_all_reviews()
    if not reviews:
        if callback.message:
            msg_obj = await callback.message.answer("Hələ rəy yoxdur.")
            await asyncio.sleep(10)
            await msg_obj.delete()
    else:
        msg = ""
        for idx, r in enumerate(reviews, 1):
            stars = "⭐" * r["rating"]
            reply = f"\nAdmin cavabı: {r['reply']}" if r.get("reply") else ""
            msg += f"{idx}) {stars}\n{r['text']}{reply}\n\n"
        if callback.message:
            msg_obj = await callback.message.answer(msg)
            await asyncio.sleep(10)
            await msg_obj.delete()
    await callback.answer()

# Admin cavab vermək üçün (ADMIN_ID ilə yoxla)
class AdminReplyForm(StatesGroup):
    waiting_reply = State()

@router.callback_query(F.data.startswith("admin_reply_"))
async def admin_reply_callback(callback: CallbackQuery, state: FSMContext):
    if callback.data is not None:
        review_idx = int(callback.data.split("_")[-1])
        await state.set_state(AdminReplyForm.waiting_reply)
        await state.update_data(review_idx=review_idx)
        if callback.message:
            await callback.message.answer("Rəy üçün cavabınızı yazın:")
    else:
        if callback.message:
            await callback.message.answer("Xəta baş verdi: review_idx məlumatı tapılmadı.")
    await callback.answer()

@router.message(AdminReplyForm.waiting_reply)
async def process_admin_reply(message: Message, state: FSMContext):
    from config import ADMIN_ID
    if not message.from_user or message.from_user.id != ADMIN_ID:
        await message.answer("Yalnız admin cavab verə bilər.")
        await state.clear()
        return
    data = await state.get_data()
    review_idx = data.get("review_idx")
    reviews = get_all_reviews()
    if review_idx is not None and isinstance(review_idx, int) and 0 <= review_idx < len(reviews):
        reviews[review_idx]["reply"] = message.text
        with open(REVIEWS_FILE, "w", encoding="utf-8") as f:
            json.dump(reviews, f, ensure_ascii=False, indent=2)
        await message.answer("Cavab əlavə olundu.")
    else:
        await message.answer("Rəy tapılmadı.")
    await state.clear()