from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
import os

router = Router()

PDF_DIR = "pdfs"
pdf_files = {
    "musahibe": {
        "path": f"{PDF_DIR}/MHT.pdf",
        "title": "Müsahibəyə hazırlıq texnikaları",
        "active": True
    },
    "cv": {
        "path": f"{PDF_DIR}/CV.pdf",
        "title": "Müəllif haqqında (CV/Resume)",
        "active": True
    },
    "pdf3": {
        "path": f"{PDF_DIR}/PDF3.pdf",
        "title": "PDF 3",
        "active": False
    },
    "pdf4": {
        "path": f"{PDF_DIR}/PDF4.pdf",
        "title": "PDF 4",
        "active": False
    },
}

@router.callback_query(F.data == "get_pdf")
async def get_pdf_menu(callback: CallbackQuery):
    buttons = []
    for key, info in pdf_files.items():
        if info["active"]:
            buttons.append([
                InlineKeyboardButton(
                    text=f" {info['title']}",
                    callback_data=f"pdf_{key}"
                )
            ])
    
    buttons.append([
        InlineKeyboardButton(text=" Əsas menyuya qayıt", callback_data="main_menu")
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.answer(
        " <b>PDF Kitabxana</b>\n\nAşağıdakı fayllardan birini seçin:",
        parse_mode="HTML",
        reply_markup=keyboard
    )
    await callback.answer()

@router.callback_query(F.data == "pdf_musahibe")
async def send_musahibe_pdf(callback: CallbackQuery):
    pdf_path = pdf_files["musahibe"]["path"]
    if not os.path.exists(pdf_path):
        await callback.message.answer(" Fayl hazır deyil.")
        await callback.answer()
        return
    
    await callback.message.answer_document(
        FSInputFile(pdf_path),
        caption="<b> Müsahibəyə hazırlıq texnikaları</b>\n\nQısa, praktik, faydalı  uğurlar! ",
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "pdf_cv")
async def send_cv_pdf(callback: CallbackQuery):
    pdf_path = pdf_files["cv"]["path"]
    if not os.path.exists(pdf_path):
        await callback.message.answer(" Fayl hazır deyil.")
        await callback.answer()
        return
    
    motivation_text = (
        " <b>Müəllif haqqında</b>\n\n"
        "Mən rəqəmsal sistemlərdə çalışmağa və karyera inkişafına açığam. "
        "İş təklifləri, layihə əməkdaşlığı və peşəkar yüksəliş imkanlarına marağım var.\n\n"
        " <b>İxtisas sahələri:</b>\n"
        " Sosial təminat sistemləri və pensiya hesablamaları\n"
        " Bot development və avtomatlaşdırma\n"
        " Data analitika və rəqəmsal transformasiya\n\n"
        " Əlaqə və əməkdaşlıq təkliflərinizi gözləyirəm.\nBuyurun, CV/Resume-m:"
    )
    
    await callback.message.answer(motivation_text, parse_mode="HTML")
    await callback.message.answer_document(
        FSInputFile(pdf_path),
        caption="<b>CV / Resume</b>",
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("pdf_"))
async def send_generic_pdf(callback: CallbackQuery):
    key = callback.data.replace("pdf_", "")
    if key in ["musahibe", "cv"]:
        return
    if key not in pdf_files:
        await callback.message.answer(" Bu PDF mövcud deyil.")
        await callback.answer()
        return
    info = pdf_files[key]
    if not info["active"]:
        await callback.message.answer(" Bu PDF hələ aktiv deyil.")
        await callback.answer()
        return
    pdf_path = info["path"]
    if not os.path.exists(pdf_path):
        await callback.message.answer(" Fayl hazır deyil.")
        await callback.answer()
        return
    await callback.message.answer_document(
        FSInputFile(pdf_path),
        caption=f"<b>{info['title']}</b>",
        parse_mode="HTML"
    )
    await callback.answer()
