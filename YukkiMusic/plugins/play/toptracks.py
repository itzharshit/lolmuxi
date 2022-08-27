#
# Copyright (C) 2021-2022 by TeamYukki@Github, < https://github.com/TeamYukki >.
#
# This file is part of < https://github.com/TeamYukki/YukkiMusicBot > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/TeamYukki/YukkiMusicBot/blob/master/LICENSE >
#
# All rights reserved.

import asyncio

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup

from config import BANNED_USERS
from YukkiMusic import app
from YukkiMusic.utils.database import get_global_tops, get_particulars, get_userss
from YukkiMusic.utils.decorators.language import languageCB
from YukkiMusic.utils.inline.playlist import (botplaylist_markup, failed_top_markup,
                                              top_play_markup)
from YukkiMusic.utils.stream.stream import stream

loop = asyncio.get_running_loop()


@app.on_callback_query(filters.regex("get_playmarkup") & ~BANNED_USERS)
@languageCB
async def get_play_markup(client, CallbackQuery, _):
    try:
        await CallbackQuery.answer()
    except:
        pass
    buttons = botplaylist_markup(_)
    return await CallbackQuery.edit_message_reply_markup(
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@app.on_callback_query(filters.regex("get_top_playlists") & ~BANNED_USERS)
@languageCB
async def get_topz_playlists(client, CallbackQuery, _):
    try:
        await CallbackQuery.answer()
    except:
        pass
    buttons = top_play_markup(_)
    return await CallbackQuery.edit_message_reply_markup(
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@app.on_callback_query(filters.regex("SERVERTOP") & ~BANNED_USERS)
@languageCB
async def server_to_play(client, CallbackQuery, _):
    await CallbackQuery.answer("This feature is currently disabled!", show_alert=True)
