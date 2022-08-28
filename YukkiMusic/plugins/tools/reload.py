#
# Copyright (C) 2021-2022 by TeamYukki@Github, < https://github.com/TeamYukki >.
#
# This file is part of < https://github.com/TeamYukki/YukkiMusicBot > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/TeamYukki/YukkiMusicBot/blob/master/LICENSE >
#
# All rights reserved.
import asyncio
import time

from pyrogram import filters
from pyrogram.types import CallbackQuery, Message

from config import BANNED_USERS, MUSIC_BOT_NAME, adminlist, lyrical
from strings import get_command
from YukkiMusic import app
from YukkiMusic.core.call import Yukki
from YukkiMusic.misc import db
from YukkiMusic.utils.database import get_authuser_names, get_cmode
from YukkiMusic.utils.database.assistantdatabase import get_assistant
from YukkiMusic.utils.decorators import ActualAdminCB, AdminActual, language
from YukkiMusic.utils.formatters import alpha_to_int, get_readable_time

### Multi-Lang Commands
RELOAD_COMMAND = get_command("RELOAD_COMMAND")
RESTART_COMMAND = get_command("RESTART_COMMAND")

rel = {}


@app.on_message(
    filters.command(RELOAD_COMMAND) & filters.group & ~filters.edited & ~BANNED_USERS
)
@language
async def reload_admin_cache(client, message: Message, _):
    try:
        chat_id = message.chat.id
        if chat_id not in rel:
            rel[chat_id] = {}
        else:
            saved = rel[chat_id]
            if saved > time.time():
                left = get_readable_time((int(saved) - int(time.time())))
                return await message.reply_text(
                    f"𝙔𝙤𝙪 𝙘𝙖𝙣 𝙤𝙣𝙡𝙮 𝙧𝙚𝙛𝙧𝙚𝙨𝙝 𝙖𝙙𝙢𝙞𝙣 𝙘𝙖𝙘𝙝𝙚 𝙞𝙣 𝙚𝙫𝙚𝙧𝙮 5 𝙢𝙞𝙣𝙨.\n\n𝙋𝙡𝙚𝙖𝙨𝙚 𝙩𝙧𝙮 𝙖𝙛𝙩𝙚𝙧 {left}"
                )
        admins = await app.get_chat_members(chat_id, filter="administrators")
        authusers = await get_authuser_names(chat_id)
        adminlist[chat_id] = []
        for user in admins:
            if user.can_manage_voice_chats:
                adminlist[chat_id].append(user.user.id)
        for user in authusers:
            user_id = await alpha_to_int(user)
            adminlist[chat_id].append(user_id)
        now = int(time.time()) + 300
        rel[chat_id] = now
        await message.reply_text(_["admin_20"])

    except:
        await message.reply_text(
            "𝙁𝙖𝙞𝙡𝙚𝙙 𝙩𝙤 𝙧𝙚𝙡𝙤𝙖𝙙 𝙖𝙙𝙢𝙞𝙣𝙘𝙖𝙘𝙝𝙚. 𝙈𝙖𝙠𝙚 𝙨𝙪𝙧𝙚 𝘽𝙤𝙩 𝙞𝙨 𝙖𝙙𝙢𝙞𝙣 𝙞𝙣 𝙮𝙤𝙪𝙧 𝙘𝙝𝙖𝙩."
        )


@app.on_message(
    filters.command(RESTART_COMMAND) & filters.group & ~filters.edited & ~BANNED_USERS
)
@AdminActual
async def restartbot(client, message: Message, _):
    mystic = await message.reply_text(
        f"Please Wait.. Restarting {MUSIC_BOT_NAME} for your chat.."
    )
    await asyncio.sleep(1)
    try:
        db[message.chat.id] = []
        await Yukki.stop_stream_force(message.chat.id)
    except:
        pass
    userbot = await get_assistant(message.chat.id)
    try:
        if message.chat.username:
            await userbot.resolve_peer(message.chat.username)
        else:
            await userbot.resolve_peer(message.chat.id)
    except:
        pass
    chat_id = await get_cmode(message.chat.id)
    if chat_id:
        try:
            got = await app.get_chat(chat_id)
        except:
            pass
        userbot = await get_assistant(chat_id)
        try:
            if got.username:
                await userbot.resolve_peer(got.username)
            else:
                await userbot.resolve_peer(chat_id)
        except:
            pass
        try:
            db[chat_id] = []
            await Yukki.stop_stream_force(chat_id)
        except:
            pass
    return await mystic.edit_text("𝙎𝙪𝙘𝙘𝙚𝙨𝙨𝙛𝙪𝙡𝙡𝙮 𝙧𝙚𝙨𝙩𝙖𝙧𝙩𝙚𝙙. 𝙏𝙧𝙮 𝙥𝙡𝙖𝙮𝙞𝙣𝙜 𝙣𝙤𝙬..")


@app.on_callback_query(filters.regex("close") & ~BANNED_USERS)
async def close_menu(_, CallbackQuery):
    try:
        await CallbackQuery.message.delete()
        await CallbackQuery.answer()
    except:
        return


@app.on_callback_query(filters.regex("stop_downloading") & ~BANNED_USERS)
@ActualAdminCB
async def stop_download(client, CallbackQuery: CallbackQuery, _):
    message_id = CallbackQuery.message.message_id
    task = lyrical.get(message_id)
    if not task:
        return await CallbackQuery.answer(
            "Downloading already Completed.", show_alert=True
        )
    if task.done() or task.cancelled():
        return await CallbackQuery.answer(
            "Downloading already Completed or Cancelled.",
            show_alert=True,
        )
    if not task.done():
        try:
            task.cancel()
            try:
                lyrical.pop(message_id)
            except:
                pass
            await CallbackQuery.answer("Downloading Cancelled", show_alert=True)
            return await CallbackQuery.edit_message_text(
                f"𝘿𝙤𝙬𝙣𝙡𝙤𝙖𝙙 𝘾𝙖𝙣𝙘𝙚𝙡𝙡𝙚𝙙 𝙗𝙮 {CallbackQuery.from_user.mention}"
            )
        except:
            return await CallbackQuery.answer(
                "𝙁𝙖𝙞𝙡𝙚𝙙 𝙩𝙤 𝙨𝙩𝙤𝙥 𝙩𝙝𝙚 𝘿𝙤𝙬𝙣𝙡𝙤𝙖𝙙𝙞𝙣𝙜.", show_alert=True
            )
    await CallbackQuery.answer("𝙁𝙖𝙞𝙡𝙚𝙙 𝙩𝙤 𝙧𝙚𝙘𝙤𝙜𝙣𝙞𝙯𝙚 𝙩𝙝𝙚 𝙧𝙪𝙣𝙣𝙞𝙣𝙜 𝙩𝙖𝙨𝙠", show_alert=True)


@app.on_callback_query(filters.regex("unban_assistant"))
async def unban_assistant_(_, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    chat_id, user_id = callback_request.split("|")
    a = await app.get_chat_member(int(chat_id), app.id)
    if not a.can_restrict_members:
        return await CallbackQuery.answer(
            "𝙄 𝙖𝙢 𝙣𝙤𝙩 𝙝𝙖𝙫𝙞𝙣𝙜 𝙗𝙖𝙣/𝙪𝙣𝙗𝙖𝙣 𝙪𝙨𝙚𝙧 𝙥𝙚𝙧𝙢𝙞𝙨𝙨𝙞𝙤𝙣. 𝘼𝙨𝙠 𝙖𝙣𝙮 𝙖𝙙𝙢𝙞𝙣 𝙩𝙤 𝙪𝙣𝙗𝙖𝙣 𝙩𝙝𝙚 𝙖𝙨𝙨𝙞𝙨𝙩𝙖𝙣𝙩.",
            show_alert=True,
        )
    else:
        try:
            await app.unban_chat_member(int(chat_id), int(user_id))
        except:
            return await CallbackQuery.answer(
                "Failed to unban",
                show_alert=True,
            )
        return await CallbackQuery.edit_message_text(
            "Assistant Unbanned. Try Playing Now."
        )
