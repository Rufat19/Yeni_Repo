from aiogram import Router, F
from aiogram.types import Message
misc_router = Router()


@misc_router.message(F.text == "/ping")
async def ping_command(message: Message):
    await message.answer("🏓 Pong!")


@misc_router.message(F.text == "/get_channel_id")
async def get_channel_id(message: Message):
    await message.answer(f"📢 Bu çatın ID-si: `{message.chat.id}`")
