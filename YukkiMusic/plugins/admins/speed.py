#
# Copyright (C) 2021-2022 by TeamYukki@Github, < https://github.com/TeamYukki >.
#
# This file is part of < https://github.com/TeamYukki/YukkiMusicBot > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/TeamYukki/YukkiMusicBot/blob/master/LICENSE >
#
# All rights reserved.

from asyncore import file_dispatcher

from pyrogram import filters
from pyrogram.types import Message

from config import BANNED_USERS, adminlist
from strings import get_command
from YukkiMusic import app
from YukkiMusic.core.call import Yukki
from YukkiMusic.misc import SUDOERS, db
from YukkiMusic.utils import AdminRightsCheck
from YukkiMusic.utils.database.memorydatabase import is_active_chat, is_nonadmin_chat
from YukkiMusic.utils.decorators.language import languageCB
from YukkiMusic.utils.inline.speed import speed_markup

checker = []

# Commands
SEEK_COMMAND = get_command("SEEK_COMMAND")


@app.on_message(
    filters.command(["cspeed", "speed", "cslow", "slow", "playback", "cplayback"])
    & filters.group
    & ~filters.edited
    & ~BANNED_USERS
)
@AdminRightsCheck
async def playback(cli, message: Message, _, chat_id):
    playing = db.get(chat_id)
    if not playing:
        return await message.reply_text(_["queue_2"])
    duration_seconds = int(playing[0]["seconds"])
    if duration_seconds == 0:
        return await message.reply_text(_["admin_35"])
    file_path = playing[0]["file"]
    if "downloads" not in file_path:
        return await message.reply_text(_["admin_35"])
    upl = speed_markup(_, chat_id)
    return await message.reply_text(
        "**𝙀𝙝𝙨𝙖𝙖𝙨 𝙋𝙡𝙖𝙮𝘽𝙖𝙘𝙠 𝙎𝙥𝙚𝙚𝙙 𝙋𝙖𝙣𝙚𝙡**\n\n𝘾𝙡𝙞𝙘𝙠 𝙤𝙣 𝙩𝙝𝙚 𝙗𝙪𝙩𝙩𝙤𝙣𝙨 𝙗𝙚𝙡𝙤𝙬 𝙩𝙤 𝙘𝙝𝙖𝙣𝙜𝙚 𝙩𝙝𝙚 𝙨𝙥𝙚𝙚𝙙 𝙤𝙛 𝙘𝙪𝙧𝙧𝙚𝙣𝙩𝙡𝙮 𝙥𝙡𝙖𝙮𝙞𝙣𝙜 𝙢𝙪𝙨𝙞𝙘 𝙤𝙣 𝙫𝙤𝙞𝙘𝙚 𝙘𝙝𝙖𝙩..",
        reply_markup=upl,
    )


@app.on_callback_query(filters.regex("SpeedUP") & ~BANNED_USERS)
@languageCB
async def del_back_playlist(client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    chat, speed = callback_request.split("|")
    chat_id = int(chat)
    if not await is_active_chat(chat_id):
        return await CallbackQuery.answer(_["general_6"], show_alert=True)
    is_non_admin = await is_nonadmin_chat(CallbackQuery.message.chat.id)
    if not is_non_admin:
        if CallbackQuery.from_user.id not in SUDOERS:
            admins = adminlist.get(CallbackQuery.message.chat.id)
            if not admins:
                return await CallbackQuery.answer(_["admin_18"], show_alert=True)
            else:
                if CallbackQuery.from_user.id not in admins:
                    return await CallbackQuery.answer(_["admin_19"], show_alert=True)
    playing = db.get(chat_id)
    if not playing:
        return await CallbackQuery.answer(_["queue_2"], show_alert=True)
    duration_seconds = int(playing[0]["seconds"])
    if duration_seconds == 0:
        return await CallbackQuery.answer(_["admin_35"], show_alert=True)
    file_path = playing[0]["file"]
    if "downloads" not in file_path:
        return await CallbackQuery.answer(_["admin_35"], show_alert=True)
    checkspeed = (playing[0]).get("speed")
    if checkspeed:
        if str(checkspeed) == str(speed):
            if str(speed) == str("1.0"):
                speed = "Normal"
            return await CallbackQuery.answer(
                f"𝙎𝙤𝙧𝙧𝙮 ! 𝘽𝙪𝙩 𝙗𝙤𝙩 𝙞𝙨 𝙖𝙡𝙧𝙚𝙖𝙙𝙮 𝙥𝙡𝙖𝙮𝙞𝙣𝙜 𝙤𝙣 {speed} 𝙨𝙥𝙚𝙚𝙙.\n\n𝙎𝙚𝙡𝙚𝙘𝙩 𝙖𝙣𝙮 𝙤𝙩𝙝𝙚𝙧 𝙨𝙥𝙚𝙚𝙙.",
                show_alert=True,
            )
    else:
        if str(speed) == str("1.0"):
            return await CallbackQuery.answer(
                f"𝙎𝙤𝙧𝙧𝙮! 𝘽𝙪𝙩 𝙗𝙤𝙩 𝙞𝙨 𝙖𝙡𝙧𝙚𝙖𝙙𝙮 𝙥𝙡𝙖𝙮𝙞𝙣𝙜 𝙤𝙣 𝙉𝙤𝙧𝙢𝙖𝙡 𝙎𝙥𝙚𝙚𝙙.\n\n𝙎𝙚𝙡𝙚𝙘𝙩 𝙖𝙣𝙮 𝙤𝙩𝙝𝙚𝙧 𝙨𝙥𝙚𝙚𝙙.",
.",
                show_alert=True,
            )
    if chat_id in checker:
        return await CallbackQuery.answer(
            "𝙏𝙝𝙚𝙧𝙚 𝙝𝙖𝙨 𝙗𝙚𝙚𝙣 𝙖 𝙘𝙤𝙣𝙫𝙚𝙧𝙨𝙞𝙤𝙣 𝙤𝙛 𝙨𝙥𝙚𝙚𝙙 𝙖𝙡𝙧𝙚𝙖𝙙𝙮 𝙜𝙤𝙞𝙣𝙜 𝙤𝙣. 𝙋𝙡𝙚𝙖𝙨𝙚 𝙬𝙖𝙞𝙩 𝙛𝙤𝙧 𝙞𝙩 𝙩𝙤 𝙜𝙚𝙩 𝙘𝙤𝙢𝙥𝙡𝙚𝙩𝙚𝙙 𝙛𝙞𝙧𝙨𝙩",
            show_alert=True,
        )
    else:
        checker.append(chat_id)
    try:
        await CallbackQuery.answer("Changing Speed....")
    except:
        pass
    mystic = await app.send_message(
        CallbackQuery.message.chat.id,
        text=f"𝙋𝙡𝙚𝙖𝙨𝙚 𝙒𝙖𝙞𝙩... 𝘽𝙤𝙩 𝙞𝙨 𝙩𝙧𝙮𝙞𝙣𝙜 𝙩𝙤 𝙘𝙝𝙖𝙣𝙜𝙚 𝙨𝙥𝙚𝙚𝙙 𝙤𝙛 𝙩𝙧𝙖𝙘𝙠. 𝙏𝙝𝙞𝙨 𝙘𝙤𝙪𝙡𝙙 𝙩𝙖𝙠𝙚 𝙨𝙤𝙢𝙚 𝙩𝙞𝙢𝙚 𝙙𝙚𝙥𝙚𝙣𝙙𝙞𝙣𝙜 𝙪𝙥𝙤𝙣 𝙛𝙞𝙡𝙚 𝙨𝙞𝙯𝙚.\n\n𝙍𝙚𝙦𝙪𝙚𝙨𝙩𝙚𝙙 𝙗𝙮: {CallbackQuery.from_user.mention}",
    )
    try:
        await Yukki.speedup_stream(
            chat_id,
            file_path,
            speed,
            playing,
        )
    except Exception as e:
        print(e)
        if chat_id in checker:
            checker.remove(chat_id)
        return await mystic.edit_text("𝙁𝙖𝙞𝙡𝙚𝙙 𝙩𝙤 𝙘𝙝𝙖𝙣𝙜𝙚 𝙨𝙥𝙚𝙚𝙙. 𝙎𝙤𝙧𝙧𝙮😭")
    if chat_id in checker:
        checker.remove(chat_id)
    await mystic.edit_text(
        f"𝙎𝙪𝙘𝙚𝙨𝙨𝙛𝙪𝙡𝙡𝙮 𝙘𝙝𝙖𝙣𝙜𝙚𝙙 𝙨𝙥𝙚𝙚𝙙 𝙤𝙛 𝙘𝙪𝙧𝙧𝙚𝙣𝙩𝙡𝙮 𝙥𝙡𝙖𝙮𝙞𝙣𝙜 𝙢𝙪𝙨𝙞𝙘 𝙩𝙤 **{speed}x**\n\n𝗖𝗵𝗮𝗻𝗴𝗲𝗱 𝗯𝘆 : {CallbackQuery.from_user.mention}"
    )
