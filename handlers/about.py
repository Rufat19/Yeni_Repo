from handlers.start import get_main_buttons
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
import asyncio
from handlers.start import main_menu_keyboard

router = Router()

def get_text(key: str) -> str:
    texts = {
        "about_bot_info": (
            "<b>DSMF və DOST Mərkəzləri — Sosial xidmətlər bir pəncərədə!</b>\n\n"
            "🏛️ <b>DSMF</b> — pensiya, sosial müavinət, sığorta və fərdi uçotla bağlı xidmətlər.\n\n"
            "📍 <b>Əsas qəbul mərkəzləri (seçilmiş):</b>\n"
            "• Sosial Ödənişlərin Təyinatı Mərkəzi — Bakı, H. Əliyev 143\n"
            "• Sosial Sığorta və Fərdi Uçot — Bakı, H. Əliyev 135A\n"
            "• Abşeron-Xızı regional — Sumqayıt, Z. Hacıyev 266\n"
            "• Qarabağ regional — Bərdə, İ. Qayıbov 15\n"
            "• Dağlıq Şirvan regional — Şamaxı, Aşıq Məmmədağa 54\n\n"
            "🔗 <a href='https://dsmf.gov.az/az/muraciet/elaqe'>dsmf.gov.az</a>\n\n"
            "🤝 <b>DOST</b> — sosial müdafiə, məşğulluq, əlillik, pensiya və digər xidmətlər üçün <i>bir pəncərə</i>.\n\n"
            "🏢 <b>Bakı DOST Mərkəzləri:</b>\n"
            "• 1-saylı DOST — Yasamal, İ. Qutqaşınlı 86\n"
            "• 2-saylı DOST — Şüvəlan, A. İldırım 30b\n"
            "• 3-saylı DOST — Nizami, H. Əliyev pr. 183b\n"
            "• 4-saylı DOST — Binəqədi, Z. Bünyadov 31-03\n"
            "• 5-saylı DOST — Xətai, Mehdi Mehdizadə 31\n"
            "• Abşeron DOST — Xırdalan, Bakı-Sumqayıt şossesi 7-ci km\n"
            "• Qarabağ Regional DOST — Bərdə, Ü. Hacıbəyov küç.\n\n"
            "🕘 <b>İş saatları:</b> B.e.–Cümə, 09:00–18:00\n"
            "📞 <b>Çağrı mərkəzi:</b> 142\n"
            "🌐 <a href='https://dost.gov.az/dost-centers'>dost.gov.az</a>\n\n"
            "💡 <b>Niyə vacibdir?</b>\n"
            "• DSMF – ödəniş və sığorta xidmətləri\n"
            "• DOST – pensiya, müavinət, məşğulluq, əlillik və s. üçün sürətli xidmət\n"
            "• Şəffaflıq, operativlik və vətəndaş yönümlülük prinsipi\n\n"
            "<b>Sosial Mühit — Peşəkar inkişaf məkanı 🏆</b>"
        ),
        "about_channels_info": (
            "<b>Faydalı kanallar seçimi</b>\n\n"
            "Aşağıdakı kanallar sosial sahədə gündəlik işinizi asanlaşdıracaq.\n"
            "Mövzular: qanunvericilik yenilikləri, hesabat nümunələri, praktiki məsləhətlər."
        ),
        "channel_sosial_muhit": (
            "<b>Sosial Mühit — peşəkar bilik məkanı</b>\n\n"
            "• Pensiyaların indeksləşməsi və kapital qaydaları\n"
            "• Müavinət məbləğləri və göstəricilər\n"
            "• Fərmanlar, qərarlar və yeniliklər\n\n"
            "<i>İştirakçılar üçün mütəmadi yenilənən fayl bazası və sual-cavab.</i>"
        ),
    }
    return texts.get(key, "")

async def timed_delete(message, delay=20):
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except Exception:
        pass

@router.message(F.text == "/info")
async def info_menu(message: Message, state: FSMContext):
    await message.answer(get_text("about_bot_info"), parse_mode="HTML")

@router.callback_query(F.data == "about_bot")
async def about_bot_callback(callback: CallbackQuery, state: FSMContext):
    if callback.message:
        main_menu_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🏠 Əsas menyuya qayıt", callback_data="main_menu")]
            ]
        )
        msg = await callback.message.answer(get_text("about_bot_info"), parse_mode="HTML", reply_markup=main_menu_kb)
        asyncio.create_task(timed_delete(msg))
    await callback.answer()
@router.callback_query(F.data == "main_menu")
async def main_menu_callback(callback: CallbackQuery, state: FSMContext):
    if callback.message:
        await callback.message.answer("Aşağıdakı seçimlərdən birini seçin və bütün funksiyalara rahat giriş əldə edin:", reply_markup=get_main_buttons())
    await callback.answer()

@router.callback_query(F.data == "about_channels")
async def about_channels_callback(callback: CallbackQuery, state: FSMContext):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Sosial Mühit", callback_data="channel_sosial_muhit")],
            [InlineKeyboardButton(text="Burada sizin kanalınız ola bilərdi", callback_data="channel_empty1")],
            [InlineKeyboardButton(text="Burada sizin kanalınız ola bilərdi", callback_data="channel_empty2")]
        ]
    )
    if callback.message:
        msg = await callback.message.answer(get_text("about_channels_info"), reply_markup=keyboard)
        asyncio.create_task(timed_delete(msg))
    await callback.answer()

@router.callback_query(F.data == "channel_sosial_muhit")
async def channel_sosial_muhit_callback(callback: CallbackQuery, state: FSMContext):
    if callback.message:
        msg = await callback.message.answer(get_text("channel_sosial_muhit"), parse_mode="HTML")
        asyncio.create_task(timed_delete(msg))
    await callback.answer()

@router.callback_query(F.data == "main_action")
async def main_action_callback(callback: CallbackQuery, state: FSMContext):
    if callback.message is not None:
        await callback.message.answer("🏠 Əsas menyuya qayıtdınız.")
    await callback.answer()

@router.callback_query(F.data == "back")
async def back_callback(callback: CallbackQuery, state: FSMContext):
    if callback.message is not None:
        await callback.message.answer("🏠 Əsas menyuya qayıt:", reply_markup=main_menu_keyboard)
    await callback.answer()