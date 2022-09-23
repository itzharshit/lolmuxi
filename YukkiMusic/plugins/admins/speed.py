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
        "**Yukki PlayBack Speed Panel**\n\nClick on the buttons below to change the speed of currently playing music on voice chat..",
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
                f"Sorry ! But bot is already playing on {speed} speed.\n\nSelect any other speed.",
                show_alert=True,
            )
    else:
        if str(speed) == str("1.0"):
            return await CallbackQuery.answer(
                f"Sorry! But bot is already playing on Normal Speed.\n\nSelect any other speed.",
                show_alert=True,
            )
    if chat_id in checker:
        return await CallbackQuery.answer(
            "There has been a conversion of speed already going on. Please wait for it to get completed first",
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
        text=f"Please Wait... Bot is trying to change speed of track. This could take some time depending upon file size.\n\nRequested by: {CallbackQuery.from_user.mention}",
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
        return await mystic.edit_text("Failed to change speed. Sorry😭")
    if chat_id in checker:
        checker.remove(chat_id)
    await mystic.edit_text(
        f"Sucessfully changed speed of currently playing music to **{speed}x**\n\nChanged by : {CallbackQuery.from_user.mention}"
    )
