from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import FSInputFile
import os

router = Router()

# Fayl yolu
pdf_path = "pdfs/MHT.pdf"

# 📌 PDF seçmək üçün menyu
@router.callback_query(F.data == "get_pdf")
async def get_pdf_menu(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📄 Müsahibəyə hazırlıq texnikaları", callback_data="pdf_musahibe")],
            [InlineKeyboardButton(text="🏠 Əsas menyuya qayıt", callback_data="main_menu")]
        ]
    )
    await callback.message.answer("🎁 Kiçik hədiyyə: Müsahibəyə hazırlıq üçün faydalı bir PDF paylaşımım var.", reply_markup=keyboard)
    await callback.answer()

# 📌 PDF göndərmək
@router.callback_query(F.data == "pdf_musahibe")
async def send_musahibe_pdf(callback: CallbackQuery):
    if not os.path.exists(pdf_path):
        await callback.message.answer("❗ Fayl hazır deyil. Bir azdan yenidən yoxlayın.")
        await callback.answer()
        return
    await callback.message.answer_document(
        FSInputFile(pdf_path),
        caption=(
            "<b>Müsahibəyə hazırlıq texnikaları</b>\n"
            "Qısa, praktik, faydalı — uğurlar! 🚀"
        ),
        parse_mode="HTML"
    )
    await callback.answer()