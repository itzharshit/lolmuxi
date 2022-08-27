from pyrogram import filters
from pyrogram.types import Message

from YukkiMusic import app
from YukkiMusic.core.call import Yukki

welcome = 20
close = 30


@app.on_message(filters.voice_chat_started, group=welcome)
@app.on_message(filters.voice_chat_ended, group=close)
async def welcome(client, message: Message):
    await Yukki.stop_stream_force(message.chat.id)
