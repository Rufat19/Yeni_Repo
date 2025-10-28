from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ChatPermissions,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramBadRequest
import asyncio
import random
from typing import Dict, Set

router = Router()

# ===================== KONFİQURASİYA =====================
# Oyun parametrləri
MIN_PLAYERS = 3
MAX_PLAYERS = 10  # istəsən artır/azalt
DESCRIBE_SECONDS = 60  # sözləri təsvir mərhələsi
VOTING_SECONDS = 45    # səsvermə mərhələsi

# Söz cütləri — istəyə görə artır
GAME_WORDS = [
    ("alma", "armud"),
    ("kitab", "jurnal"),
    ("it", "pişik"),
    ("qələm", "karandaş"),
    ("çay", "qəhvə"),
    ("şəkər", "duz"),
    ("qatar", "təyyarə"),
    ("yay", "qış"),
    ("gün", "gecə"),
    ("su", "süd"),
    ("telefon", "kompüter"),
    ("balıq", "toyuq"),
    ("dəftər", "kağız"),
    ("paltar", "ayaqqabı"),
    ("yemək", "içmək"),
    ("şəhər", "kənd"),
    ("ağ", "qara"),
    ("yaşıl", "mavi"),
    ("göz", "qulaq"),
    ("dost", "tanış"),
    ("qapı", "pəncərə"),
    ("saat", "tarix"),
    ("uçmaq", "üzmək"),
    ("yaz", "payız"),
    ("ata", "ana"),
    ("uşaq", "böyük"),
    ("dərs", "imtahan"),
    ("film", "kitab"),
    ("maşın", "velosiped"),
    ("meyvə", "tərəvəz"),
    ("qələm", "silgi"),
    ("səbir", "qəzəb"),
    ("sevinc", "kədər"),
    ("gülmək", "ağlamaq"),
    ("düz", "səhv"),
    ("sabah", "axşam"),
    ("dəmir", "taxta"),
    ("pul", "vaxt"),
    ("internet", "televiziya"),
    ("qəhvə", "çay"),
    ("dəftər", "kitab"),
    ("söz", "cümlə"),
    ("rəng", "şəkil"),
    ("açar", "kilid"),
    ("yol", "küçə"),
    ("göy", "yer"),
    ("hava", "su"),
    ("gəmi", "qayıq"),
    ("dərə", "dağ"),
    ("səma", "ulduz"),
    ("qəlb", "beyin"),
    ("sevgi", "dostluq"),
    ("qorxu", "ümid"),
    ("gözəl", "çirkin"),
    ("yumşaq", "sərt"),
    ("isti", "soyuq"),
    ("sürətli", "yavaş"),
    ("ucuz", "bahalı"),
    ("ağır", "yüngül"),
    ("səssiz", "səsli"),
]

# Stikerlər (file_id-ni öz botunla bir dəfə əldə edib bura yaz)
STICKERS = {
    "lobby": None,      # lobbi açılarkən
    "start": None,      # oyun başlayanda
    "vote": None,       # səsvermə açılanda
    "win": None,        # komanda köstəbəyi tapanda
    "impostor_win": None,  # köstəbək qalib olanda
}

# ===================== FSM (opsional) =====================
class GameState(StatesGroup):
    lobby = State()       # qoşulma mərhələsi
    describing = State()  # sözləri təsvir etmə
    voting = State()      # səsvermə

# ===================== OYUN SAXLAMA STRUKTURU =====================
# chat_id -> oyun məlumatı
active_games: Dict[int, dict] = {}

# Struktura nümunə:
# {
#   "creator_id": int,
#   "lobby_msg_id": int,        # iştirakçı siyahısı olan mesaj (edit üçün)
#   "players": {user_id: full_name, ...},
#   "impostor": int | None,
#   "words": {user_id: str, ...},
#   "votes": {voter_id: voted_id, ...},
#   "phase": str,                # lobby | describing | voting
#   "restricted": set[int],      # oyun zamanı susdurulan kənar istifadəçilər
# }

# ===================== KÖMƏKÇİ FUNKSİYALAR =====================
async def send_sticker_or_emoji(bot, chat_id: int, key: str, fallback: str = ""):
    file_id = STICKERS.get(key)
    if file_id:
        try:
            await bot.send_sticker(chat_id, file_id)
            return
        except TelegramBadRequest:
            pass
    if fallback:
        await bot.send_message(chat_id, fallback)

async def list_text_players(players: Dict[int, str]) -> str:
    if not players:
        return "—"
    return "\n".join([f"• {name} (#{uid})" for uid, name in players.items()])

async def build_lobby_keyboard(creator_id: int, players_count: int):
    # Ready düyməsi yalnız yaradıcının görəcəyi callback-də yoxlanır
    buttons = [
        [InlineKeyboardButton(text="➕ Oyuna qoşul", callback_data="join")],
        [InlineKeyboardButton(text="➖ Oyundan çıx", callback_data="leave")],
    ]
    # Ready yalnız creator üçün aktiv olacaq (callback daxilində yoxlayacağıq)
    ready_text = "✅ Ready (başlat)" if players_count >= MIN_PLAYERS else f"⏳ Ən azı {MIN_PLAYERS} nəfər"
    buttons.append([InlineKeyboardButton(text=ready_text, callback_data="ready")])
    buttons.append([InlineKeyboardButton(text="✖️ Lobbini bağla", callback_data="cancel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def edit_lobby_message(bot, chat_id: int):
    game = active_games.get(chat_id)
    if not game:
        return
    players_txt = await list_text_players(game["players"])
    kb = await build_lobby_keyboard(game["creator_id"], len(game["players"]))
    text = (
        "🕹️ <b>Köstəbək</b> — Lobbi açıqdır!\n\n"
        f"<b>Yaradıcı:</b> {game['players'].get(game['creator_id'], '—')}\n"
        f"<b>İştirakçılar ({len(game['players'])}/{MAX_PLAYERS}):</b>\n{players_txt}\n\n"
        "Qoşul: eyni söz hamıya, fərqli söz birinə. Təsvir et, ifşa et, səs ver!"
    )
    try:
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=game["lobby_msg_id"],
            text=text,
            reply_markup=kb,
            parse_mode="HTML",
        )
    except TelegramBadRequest:
        pass

async def get_is_admin(bot, chat_id: int, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in {"administrator", "creator"}
    except Exception:
        return False

async def restrict_user(bot, chat_id: int, user_id: int):
    perms = ChatPermissions(
        can_send_messages=False,
        can_send_audios=False,
        can_send_documents=False,
        can_send_photos=False,
        can_send_videos=False,
        can_send_video_notes=False,
        can_send_voice_notes=False,
        can_send_polls=False,
        can_send_other_messages=False,
        can_add_web_page_previews=False,
        can_pin_messages=False,
    )
    try:
        await bot.restrict_chat_member(chat_id, user_id, perms)
    except TelegramBadRequest:
        pass

async def unrestrict_user(bot, chat_id: int, user_id: int):
    perms = ChatPermissions(
        can_send_messages=True,
        can_send_audios=True,
        can_send_documents=True,
        can_send_photos=True,
        can_send_videos=True,
        can_send_video_notes=True,
        can_send_voice_notes=True,
        can_send_polls=True,
        can_send_other_messages=True,
        can_add_web_page_previews=True,
        can_pin_messages=False,
    )
    try:
        await bot.restrict_chat_member(chat_id, user_id, perms)
    except TelegramBadRequest:
        pass

async def cleanup_restrictions(bot, chat_id: int):
    game = active_games.get(chat_id)
    if not game:
        return
    for uid in list(game.get("restricted", set())):
        await unrestrict_user(bot, chat_id, uid)
    game["restricted"].clear()

# ===================== OYUN AXINI =====================
@router.message(F.text == "/stop")
async def cmd_stop(message: Message):
    chat_id = message.chat.id
    if chat_id in active_games:
        await end_game(chat_id, message.bot, reason="/stop komandası ilə oyun dayandırıldı.")
        await message.reply("Aktiv oyun dayandırıldı.")
    else:
        await message.reply("Aktiv oyun yoxdur.")

@router.message(F.text == "/game")
async def cmd_game(message: Message, state: FSMContext):
    chat_id = message.chat.id
    bot_id = (await message.bot.get_me()).id
    # Botun admin olub-olmadığını yoxla
    try:
        member = await message.bot.get_chat_member(chat_id, bot_id)
        is_admin = member.status in {"administrator", "creator"}
    except Exception:
        is_admin = False

    if not is_admin:
        await message.reply("❗ Oyun başlaya bilməz. Botu qrupda admin təyin edin və yenidən cəhd edin.")
        return

    # Əgər artıq lobbi/oyun varsa, xəbər ver
    if chat_id in active_games:
        await message.reply("Bu çatda artıq aktiv oyun var. Onu bitirib yenidən başlat! ✋")
        return

    creator_id = message.from_user.id
    creator_name = message.from_user.full_name

    # Oyun strukturunu qur
    active_games[chat_id] = {
        "creator_id": creator_id,
        "lobby_msg_id": None,
        "players": {creator_id: creator_name},
        "impostor": None,
        "words": {},
        "votes": {},
        "phase": "lobby",
        "restricted": set(),
    }

    await state.set_state(GameState.lobby)

    kb = await build_lobby_keyboard(creator_id, 1)
    msg = await message.answer(
        "🕹️ <b>Köstəbək</b> oyununa xoş gəldiniz!\n\n"
        "➕ Qoşul düyməsinə bas, \n"
        f"✅ Ready — yalnız yaradıcının ixtiyarındadır (min {MIN_PLAYERS} nəfər).",
        reply_markup=kb,
        parse_mode="HTML",
    )
    await asyncio.sleep(1)
    # Sticker (lobbi)
    await send_sticker_or_emoji(message.bot, chat_id, "lobby", "Lobbi açıldı. Oyunçular toplanır…")
    await asyncio.sleep(1)
    # yadda saxla
    if chat_id in active_games:
        active_games[chat_id]["lobby_msg_id"] = msg.message_id
        # iştirakçı siyahısını göstər
        await edit_lobby_message(message.bot, chat_id)


@router.callback_query(F.data == "join")
async def cb_join(callback: CallbackQuery):
    if not callback.message or not callback.message.chat:
        return
    chat_id = callback.message.chat.id
    user_id = callback.from_user.id
    name = callback.from_user.full_name

    game = active_games.get(chat_id)
    if not game or game.get("phase") != "lobby":
        await callback.answer("Hazırda lobbi açıq deyil.")
        return

    if user_id in game["players"]:
        await callback.answer("Artıq lobbiesən!", show_alert=False)
        return

    if len(game["players"]) >= MAX_PLAYERS:
        await callback.answer("Lobbi doludur.")
        return

    game["players"][user_id] = name
    await callback.answer("Qoşuldun! 🎮")
    await edit_lobby_message(callback.bot, chat_id)


@router.callback_query(F.data == "leave")
async def cb_leave(callback: CallbackQuery):
    if not callback.message or not callback.message.chat:
        return
    chat_id = callback.message.chat.id
    user_id = callback.from_user.id

    game = active_games.get(chat_id)
    if not game or game.get("phase") != "lobby":
        await callback.answer("Hazırda lobbi açıq deyil.")
        return

    if user_id not in game["players"]:
        await callback.answer("Lobbidə deyilsən.")
        return

    # Yaradıcı çıxmaq istəsə, lobbini bağla
    if user_id == game["creator_id"]:
        await callback.answer("Yaradıcı lobbini bağladı.")
        await end_game(chat_id, callback.bot, reason="Yaradıcı oyunu ləğv etdi.")
        return

    del game["players"][user_id]
    await callback.answer("Çıxdın.")
    await edit_lobby_message(callback.bot, chat_id)


@router.callback_query(F.data == "cancel")
async def cb_cancel(callback: CallbackQuery):
    if not callback.message or not callback.message.chat:
        return
    chat_id = callback.message.chat.id
    user_id = callback.from_user.id

    game = active_games.get(chat_id)
    if not game:
        await callback.answer("Aktiv oyun yoxdur.")
        return

    if user_id != game["creator_id"]:
        await callback.answer("Bu əməliyyat yalnız yaradıcıya məxsusdur.")
        return

    await callback.answer("Lobbi bağlandı.")
    await end_game(chat_id, callback.bot, reason="Lobbi bağlandı.")


@router.callback_query(F.data == "ready")
async def cb_ready(callback: CallbackQuery, state: FSMContext):
    if not callback.message or not callback.message.chat:
        return
    chat_id = callback.message.chat.id
    user_id = callback.from_user.id

    game = active_games.get(chat_id)
    if not game or game.get("phase") != "lobby":
        await callback.answer("Hazırda lobbi mərhələsindəyik.")
        return

    if user_id != game["creator_id"]:
        await callback.answer("Ready yalnız yaradıcının ixtiyarındadır.")
        return

    if len(game["players"]) < MIN_PLAYERS:
        await callback.answer(f"Ən azı {MIN_PLAYERS} nəfər lazımdır.")
        return

    # Başlat
    await callback.answer("Oyun başlayır! 🚀")
    game["phase"] = "describing"
    await state.set_state(GameState.describing)

    # Qaydalar izahı
    rules = (
        "<b>Köstəbək Oyununun Qaydaları:</b>\n"
        "• Hər kəsə bir söz, bir nəfərə fərqli söz göndəriləcək.\n"
        "• Gizli sözünü birbaşa demədən təsvir et.\n"
        "• Sonda səsvermə olacaq, köstəbəyi tapmağa çalışın.\n"
        "• Kənar şəxslər yazarsa, bot onları susdura bilər.\n"
        "• Ən azı 3 nəfər olmalıdır.\n"
        "• Əgər köstəbək sona qədər tapılmazsa, qalib köstəbəyə <b>5 RBC</b> hədiyyə verilir! 🎁\n"
        "Uğurlar! 🕵️‍♂️"
    )
    await callback.message.answer(rules, parse_mode="HTML")
    await asyncio.sleep(1)
    # Sticker (start)
    await send_sticker_or_emoji(callback.bot, chat_id, "start", "Başlayırıq! Köstəbək aramızdadır…")
    await asyncio.sleep(1)
    await send_words_and_describe_phase(chat_id, callback.bot)


async def send_words_and_describe_phase(chat_id: int, bot):
    """Sözləri DM ilə göndər, təsvir mərhələsini aç, sonra səsverməyə keç."""
    game = active_games.get(chat_id)
    if not game:
        return

    players = list(game["players"].keys())
    # Qrup üçün istifadə olunan söz cütlərini saxla
    if "used_word_pairs" not in game:
        game["used_word_pairs"] = set()
    available_words = [wp for wp in GAME_WORDS if wp not in game["used_word_pairs"]]
    if not available_words:
        # Hamısı istifadə olunubsa, siyahını sıfırla
        game["used_word_pairs"] = set()
        available_words = GAME_WORDS.copy()
    word_pair = random.choice(available_words)
    game["used_word_pairs"].add(word_pair)
    impostor_id = random.choice(players)

    words = {}
    not_received = []
    for uid in players:
        words[uid] = word_pair[1] if uid == impostor_id else word_pair[0]
        try:
            await bot.send_message(uid, f"Sənin gizli sözün: <b>{words[uid]}</b>", parse_mode="HTML")
        except Exception:
            not_received.append(uid)
    if not_received:
        names = [game["players"].get(uid, str(uid)) for uid in not_received]
        await bot.send_message(
            chat_id,
            f"⚠️ Bu istifadəçilərə gizli söz göndərilə bilmədi (DM bağlıdır):\n" + ", ".join(names) + "\nZəhmət olmasa botu başlatın və şəxsi mesajları açın.",
            parse_mode="HTML"
        )

    game["impostor"] = impostor_id
    game["words"] = words
    game["votes"] = {}

    # Təsvir müddətini elan et
    await bot.send_message(
        chat_id,
        (
            "🗣️ <b>Təsvir mərhələsi</b> başladı!\n"
            f"{DESCRIBE_SECONDS} saniyə ərzində sözü birbaşa demədən təsvir edin.\n"
            "Kənar şəxslər yazmasın — yazsalar, bot susdura bilər."
        ),
        parse_mode="HTML",
    )

    # TAYMER: təsvir -> səsvermə
    async def timer_to_voting():
        await asyncio.sleep(DESCRIBE_SECONDS)
        await start_voting(chat_id, bot)

    asyncio.create_task(timer_to_voting())


async def start_voting(chat_id: int, bot):
    game = active_games.get(chat_id)
    if not game or game.get("phase") != "describing":
        return

    game["phase"] = "voting"

    # Səsvermə düymələri (adlarla)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=name, callback_data=f"vote_{uid}")]
            for uid, name in game["players"].items()
        ]
    )

    await send_sticker_or_emoji(bot, chat_id, "vote")

    await bot.send_message(
        chat_id,
        (
            "🗳️ <b>Səsvermə başladı!</b>\n"
            f"{VOTING_SECONDS} saniyə ərzində köstəbəyi seçin."
        ),
        reply_markup=keyboard,
        parse_mode="HTML",
    )

    async def voting_timeout():
        await asyncio.sleep(VOTING_SECONDS)
        # kimsə səs verməsə də, nəticə hesablanacaq
        await show_results(chat_id, bot)

    asyncio.create_task(voting_timeout())


@router.callback_query(F.data.startswith("vote_"))
async def cb_vote(callback: CallbackQuery):
    if not callback.message or not callback.message.chat:
        return
    chat_id = callback.message.chat.id
    voter_id = callback.from_user.id

    game = active_games.get(chat_id)
    if not game or game.get("phase") != "voting":
        await callback.answer("İndi səsvermə mərhələsi deyil.")
        return

    if voter_id not in game["players"]:
        await callback.answer("Sən oyunçu deyilsən.")
        return

    try:
        voted_id = int(callback.data.split("_", 1)[1])
    except Exception:
        await callback.answer("Seçim xətası.")
        return

    if voted_id not in game["players"]:
        await callback.answer("Belə oyunçu yoxdur.")
        return

    game["votes"][voter_id] = voted_id
    await callback.answer("Səs qeydə alındı! ✅")

    # Hamı səs veribsə, dərhal nəticə
    if len(game["votes"]) == len(game["players"]):
        await show_results(chat_id, callback.bot)


async def show_results(chat_id: int, bot):
    game = active_games.get(chat_id)
    if not game or game.get("phase") != "voting":
        return

    # Nəticələri hesabla
    tally: Dict[int, int] = {}
    for voted in game["votes"].values():
        tally[voted] = tally.get(voted, 0) + 1

    if not tally:
        # Heç kim səs verməyibsə, təsadüfi birini çıxarmaq əvəzinə, turu keçər
        await bot.send_message(chat_id, "Heç kim səs vermədi. Tur keçildi.")
        # Növbəti tur
        await next_round_or_end(chat_id, bot)
        return

    max_votes = max(tally.values())
    eliminated = [uid for uid, cnt in tally.items() if cnt == max_votes]

    # Mesaj
    lines = ["<b>Səsvermə nəticələri:</b>"]
    for uid, cnt in tally.items():
        lines.append(f"{game['players'].get(uid, uid)}: {cnt} səs")
    lines.append("")

    # Eyni səs alanlar hamısı çıxır
    for uid in eliminated:
        # çıxarılanların adını əvvəlcə çək
        lines.append(f"Çıxarıldı: {game['players'].get(uid, uid)}")

    await bot.send_message(chat_id, "\n".join(lines), parse_mode="HTML")

    impostor = game["impostor"]

    # Oyunçulardan sil
    for uid in eliminated:
        game["players"].pop(uid, None)

    # Win/End şərtləri
    if impostor in eliminated:
        await send_sticker_or_emoji(bot, chat_id, "win", "🎉 Köstəbək tapıldı! Komanda qalibdir.")
        await end_game(chat_id, bot, reason=f"Köstəbək {impostor} tapıldı.")
        return

    # Köstəbək qalıb və oyunçu sayı <= 2 — köstəbək qalib
    if len(game["players"]) <= 2 and impostor in game["players"]:
        await send_sticker_or_emoji(bot, chat_id, "impostor_win", "😎 Köstəbək gizlənə bildi və qalib oldu!")
        await end_game(chat_id, bot, reason="Köstəbək qalib oldu.")
        return

    # Əks halda növbəti tur
    await next_round_or_end(chat_id, bot)


async def next_round_or_end(chat_id: int, bot):
    game = active_games.get(chat_id)
    if not game:
        return

    # Əgər 2-dən çox oyunçu varsa, yeni tur
    if len(game["players"]) >= 3:
        game["phase"] = "describing"
        await send_words_and_describe_phase(chat_id, bot)
    else:
        # Oyun bitir
        await end_game(chat_id, bot, reason="Kifayət qədər oyunçu qalmadı.")


async def end_game(chat_id: int, bot, reason: str = "Oyun bitdi."):
    game = active_games.get(chat_id)
    if game:
        # Restrict edilmiş kənarları aç
        await cleanup_restrictions(bot, chat_id)
        try:
            await bot.send_message(chat_id, f"<b>Oyun bitdi.</b> {reason}", parse_mode="HTML")
        except TelegramBadRequest:
            pass
        active_games.pop(chat_id, None)

# ===================== KƏNAR İSTİFADƏÇİ MESAJLARINI İDARƏ ET =====================
@router.message()
async def non_player_guard(message: Message):
    """
    Oyun aktivdirsə: oyunçu olmayanın mesajını sil və onu müvəqqəti susdur.
    Adminlərə toxunmuruq.
    """
    chat_id = message.chat.id
    user_id = message.from_user.id if message.from_user else None

    game = active_games.get(chat_id)
    if not game:
        return  # aktiv oyun yoxdur

    # Yalnız oyun axını mərhələlərində sərt qayda tətbiq edirik
    if game.get("phase") not in {"describing", "voting"}:
        return

    if not user_id:
        return

    # Adminlər toxunulmaz
    if await get_is_admin(message.bot, chat_id, user_id):
        return

    # Oyunçu deyilsə → sil və restrict
    if user_id not in game["players"]:
        try:
            await message.delete()
        except TelegramBadRequest:
            pass
        await restrict_user(message.bot, chat_id, user_id)
        game["restricted"].add(user_id)
        try:
            await message.answer(
                "❗ Bu mərhələdə yalnız oyunçular yaza bilər. Oyundan sonra səsiniz açılacaq."
            )
        except TelegramBadRequest:
            pass

# ===================== THE END =====================
# QURAŞDIRMA QEYDLƏRİ
# 1) Bu router-i run.py-də daxil et:
#    from imposter_game_router import router as game_router
#    dp.include_router(game_router)
# 2) STICKERS dict-də öz file_id-lərini yerləşdirsən, bot stiker göndərəcək.
#    Yoxdursa, fallback mətnlər işləyəcək.
# 3) Botu qrupda administrator et və "Delete messages" + "Restrict members" icazələrini ver.
# 4) İstəsən DESCRIBE_SECONDS və VOTING_SECONDS dəyərlərini tənzimlə.
        