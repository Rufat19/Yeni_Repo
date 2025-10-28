from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import FSInputFile
import os

router = Router()

# Check if the PDF file exists
pdf_path = "pdfs/MHT.pdf"
pdf_exists = os.path.exists(pdf_path)
print(pdf_exists)

# 📌 PDF seçmək üçün menyu
@router.callback_query(F.data == "get_pdf")
async def get_pdf_menu(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📄 Müsahibəyə hazırlıq texnikaları", callback_data="pdf_musahibe")],
            [InlineKeyboardButton(text="🏠 Əsas menyuya qayıt", callback_data="main_menu")]
        ]
    )
    await callback.message.answer("Buna sənə məndən hədiyyə olsun:", reply_markup=keyboard)
    await callback.answer()

# 📌 PDF göndərmək
@router.callback_query(F.data == "pdf_musahibe")
async def send_musahibe_pdf(callback: CallbackQuery):
    pdf_path = "pdfs/MHT.pdf"
    await callback.message.answer_document(FSInputFile(pdf_path), caption="PDF göndərildi ✅")
    await callback.answer()