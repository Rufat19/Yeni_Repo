import os
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile

router = Router()

EXCEL_LESSONS_DIR = "excel_lessons"

# Main menu for Excel lessons
@router.callback_query(F.data == "excel_lessons_menu")
async def excel_lessons_menu(callback: CallbackQuery):
    try:
        folders = [d for d in os.listdir(EXCEL_LESSONS_DIR) if os.path.isdir(os.path.join(EXCEL_LESSONS_DIR, d))]
        folders.sort()  # Sort folders for consistent order

        if not folders:
            await callback.message.answer("⚠️ Hazırda heç bir dərs materialı yoxdur.")
            await callback.answer()
            return

        keyboard = []
        for folder in folders:
            keyboard.append([InlineKeyboardButton(text=f"📁 {folder}", callback_data=f"list_files:{folder}")])
        
        keyboard.append([InlineKeyboardButton(text="🏠 Əsas menyuya qayıt", callback_data="main_menu")])

        await callback.message.answer("📚 Zəhmət olmasa, bir dərs qovluğu seçin:", reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))

    except FileNotFoundError:
        await callback.message.answer("❌ Dərslik qovluğu tapılmadı. Zəhmət olmasa adminlə əlaqə saxlayın.")
    
    await callback.answer()

# List files in a selected folder
@router.callback_query(F.data.startswith("list_files:"))
async def list_lesson_files(callback: CallbackQuery):
    folder_name = callback.data.split(":", 1)[1]
    folder_path = os.path.join(EXCEL_LESSONS_DIR, folder_name)

    try:
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        
        if not files:
            await callback.message.answer(f"⚠️ '{folder_name}' qovluğunda heç bir fayl tapılmadı.")
            await callback.answer()
            return

        keyboard = []
        for file in files:
            keyboard.append([InlineKeyboardButton(text=f"📄 {file}", callback_data=f"send_file:{folder_name}:{file}")])
        
        keyboard.append([InlineKeyboardButton(text="⬅️ Geri", callback_data="excel_lessons_menu")])

        await callback.message.edit_text(f"'{folder_name}' qovluğundakı fayllar:", reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))

    except FileNotFoundError:
        await callback.message.answer("❌ Qovluq tapılmadı.")
    
    await callback.answer()

# Send the selected file
@router.callback_query(F.data.startswith("send_file:"))
async def send_lesson_file(callback: CallbackQuery):
    try:
        _, folder_name, file_name = callback.data.split(":", 2)
        file_path = os.path.join(EXCEL_LESSONS_DIR, folder_name, file_name)

        if os.path.exists(file_path):
            document = FSInputFile(file_path)
            await callback.message.answer_document(document, caption=f"Buyurun, '{file_name}' faylı.")
        else:
            await callback.message.answer("❌ Fayl tapılmadı.")
            
    except Exception as e:
        await callback.message.answer(f"❗️ Fayl göndərilərkən xəta baş verdi: {e}")

    await callback.answer()
