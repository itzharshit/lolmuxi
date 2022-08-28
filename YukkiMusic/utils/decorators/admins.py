#
# Copyright (C) 2021-2022 by TeamYukki@Github, < https://github.com/TeamYukki >.
#
# This file is part of < https://github.com/TeamYukki/YukkiMusicBot > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/TeamYukki/YukkiMusicBot/blob/master/LICENSE >
#
# All rights reserved.

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import adminlist, confirmer
from strings import get_string
from YukkiMusic import app
from YukkiMusic.misc import SUDOERS, db
from YukkiMusic.utils.database import (get_authuser_names, get_cmode, get_lang,
                                       is_active_chat, is_commanddelete_on,
                                       is_maintenance, is_nonadmin_chat)
from YukkiMusic.utils.database.memorydatabase import get_upvote_count, is_skipmode

from ..formatters import int_to_alpha


def AdminRightsCheck(mystic):
    async def wrapper(client, message):
        if await is_maintenance() is False:
            if message.from_user.id not in SUDOERS:
                return await message.reply_text(
                    "𝘽𝙤𝙩 𝙞𝙨 𝙪𝙣𝙙𝙚𝙧 𝙢𝙖𝙞𝙣𝙩𝙚𝙣𝙖𝙣𝙘𝙚. 𝙋𝙡𝙚𝙖𝙨𝙚 𝙬𝙖𝙞𝙩 𝙛𝙤𝙧 𝙨𝙤𝙢𝙚 𝙩𝙞𝙢𝙚..."
                )
        if await is_commanddelete_on(message.chat.id):
            try:
                await message.delete()
            except:
                pass
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)
        except:
            _ = get_string("en")
        if message.sender_chat:
            upl = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="How to Fix this? ",
                            callback_data="AnonymousAdmin",
                        ),
                    ]
                ]
            )
            return await message.reply_text(_["general_4"], reply_markup=upl)
        if message.command[0][0] == "c":
            chat_id = await get_cmode(message.chat.id)
            if chat_id is None:
                return await message.reply_text(_["setting_12"])
            try:
                await app.get_chat(chat_id)
            except:
                return await message.reply_text(_["cplay_4"])
        else:
            chat_id = message.chat.id
        if not await is_active_chat(chat_id):
            return await message.reply_text(_["general_6"])
        is_non_admin = await is_nonadmin_chat(message.chat.id)
        if not is_non_admin:
            if message.from_user.id not in SUDOERS:
                admins = adminlist.get(message.chat.id)
                if not admins:
                    return await message.reply_text(_["admin_18"])
                else:
                    if message.from_user.id not in admins:
                        if await is_skipmode(message.chat.id):
                            upvote = await get_upvote_count(chat_id)
                            text = f"""**Admin Right Needed**

𝙄𝙛 𝙮𝙤𝙪'𝙧𝙚 𝙖𝙡𝙧𝙚𝙖𝙙𝙮 𝙖𝙣 𝙖𝙙𝙢𝙞𝙣 , 𝙧𝙚𝙡𝙤𝙖𝙙 𝙖𝙙𝙢𝙞𝙣𝙡𝙞𝙨𝙩 : /admincache

𝙄𝙛 𝙩𝙝𝙞𝙨 𝙜𝙚𝙩𝙨 𝙖 𝙩𝙤𝙩𝙖𝙡 𝙤𝙛 **{upvote}** 𝙪𝙥𝙫𝙤𝙩𝙚𝙨, 𝘽𝙤𝙩 𝙬𝙞𝙡𝙡 𝙥𝙚𝙧𝙛𝙤𝙧𝙢 𝙩𝙝𝙚 𝙖𝙘𝙩𝙞𝙤𝙣 𝙗𝙮 𝙞𝙩𝙨𝙚𝙡𝙛. 𝘼𝙙𝙢𝙞𝙣𝙨 𝙘𝙖𝙣 𝙙𝙞𝙨𝙖𝙗𝙡𝙚 𝙩𝙝𝙞𝙨 𝙫𝙤𝙩𝙞𝙣𝙜 𝙢𝙤𝙙𝙚 𝙛𝙧𝙤𝙢 𝙨𝙚𝙩𝙩𝙞𝙣𝙜𝙨
."""

                            command = message.command[0]
                            if command[0] == "c":
                                command = command[1:]
                            if command == "speed":
                                return await message.reply_text(_["admin_19"])
                            MODE = command.title()
                            upl = InlineKeyboardMarkup(
                                [
                                    [
                                        InlineKeyboardButton(
                                            text="👍",
                                            callback_data=f"ADMIN  UpVote|{chat_id}_{MODE}",
                                        ),
                                    ]
                                ]
                            )
                            if chat_id not in confirmer:
                                confirmer[chat_id] = {}
                            try:
                                vidid = db[chat_id][0]["vidid"]
                                file = db[chat_id][0]["file"]
                            except:
                                return await message.reply_text(_["admin_19"])
                            senn = await message.reply_text(text, reply_markup=upl)
                            confirmer[chat_id][senn.message_id] = {
                                "vidid": vidid,
                                "file": file,
                            }
                            return
                        else:
                            return await message.reply_text(_["admin_19"])

        return await mystic(client, message, _, chat_id)

    return wrapper


def AdminActual(mystic):
    async def wrapper(client, message):
        if await is_maintenance() is False:
            if message.from_user.id not in SUDOERS:
                return await message.reply_text(
                    "𝘽𝙤𝙩 𝙞𝙨 𝙪𝙣𝙙𝙚𝙧 𝙢𝙖𝙞𝙣𝙩𝙚𝙣𝙖𝙣𝙘𝙚. 𝙋𝙡𝙚𝙖𝙨𝙚 𝙬𝙖𝙞𝙩 𝙛𝙤𝙧 𝙨𝙤𝙢𝙚 𝙩𝙞𝙢𝙚..."
                )
        if await is_commanddelete_on(message.chat.id):
            try:
                await message.delete()
            except:
                pass
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)
        except:
            _ = get_string("en")
        if message.sender_chat:
            upl = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="How to Fix this? ",
                            callback_data="AnonymousAdmin",
                        ),
                    ]
                ]
            )
            return await message.reply_text(_["general_4"], reply_markup=upl)
        if message.from_user.id not in SUDOERS:
            try:
                member = await app.get_chat_member(message.chat.id, message.from_user.id)
            except:
                return
            if not member.can_manage_voice_chats:
                return await message.reply(_["general_5"])
        return await mystic(client, message, _)

    return wrapper


def ActualAdminCB(mystic):
    async def wrapper(client, CallbackQuery):
        if await is_maintenance() is False:
            if CallbackQuery.from_user.id not in SUDOERS:
                return await CallbackQuery.answer(
                    "𝘽𝙤𝙩 𝙞𝙨 𝙪𝙣𝙙𝙚𝙧 𝙢𝙖𝙞𝙣𝙩𝙚𝙣𝙖𝙣𝙘𝙚. 𝙋𝙡𝙚𝙖𝙨𝙚 𝙬𝙖𝙞𝙩 𝙛𝙤𝙧 𝙨𝙤𝙢𝙚 𝙩𝙞𝙢𝙚...",
                    show_alert=True,
                )
        try:
            language = await get_lang(CallbackQuery.message.chat.id)
            _ = get_string(language)
        except:
            _ = get_string("en")
        if CallbackQuery.message.chat.type == "private":
            return await mystic(client, CallbackQuery, _)
        is_non_admin = await is_nonadmin_chat(CallbackQuery.message.chat.id)
        if not is_non_admin:
            try:
                a = await app.get_chat_member(
                    CallbackQuery.message.chat.id,
                    CallbackQuery.from_user.id,
                )
            except:
                return await CallbackQuery.answer(_["general_5"], show_alert=True)
            if not a.can_manage_voice_chats:
                if CallbackQuery.from_user.id not in SUDOERS:
                    token = await int_to_alpha(CallbackQuery.from_user.id)
                    _check = await get_authuser_names(CallbackQuery.from_user.id)
                    if token not in _check:
                        try:
                            return await CallbackQuery.answer(
                                _["general_5"],
                                show_alert=True,
                            )
                        except:
                            return
        return await mystic(client, CallbackQuery, _)

    return wrapper
