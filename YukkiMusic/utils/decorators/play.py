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
from pyrogram.errors import (ChatAdminRequired, FloodWait, InviteHashExpired,
                             UserAlreadyParticipant, UserNotParticipant)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from config import LOG_GROUP_ID, PLAYLIST_IMG_URL, PRIVATE_BOT_MODE, adminlist
from strings import get_string
from YukkiMusic import YouTube, app
from YukkiMusic.misc import SUDOERS
from YukkiMusic.utils.database import (get_cmode, get_lang, get_playmode, get_playtype,
                                       is_active_chat, is_commanddelete_on,
                                       is_served_private_chat, is_served_user)
from YukkiMusic.utils.database.assistantdatabase import get_assistant
from YukkiMusic.utils.database.memorydatabase import is_maintenance
from YukkiMusic.utils.inline.playlist import botplaylist_markup

checker = []
passed = []

USER = []
links = {}


def PlayWrapper(command):
    async def wrapper(client, message):
        language = await get_lang(message.chat.id)
        _ = get_string(language)
        if message.sender_chat:
            upl = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="𝙃𝙤𝙬 𝙩𝙤 𝙁𝙞𝙭 𝙩𝙝𝙞𝙨?",
                            callback_data="AnonymousAdmin",
                        ),
                    ]
                ]
            )
            return await message.reply_text(_["general_4"], reply_markup=upl)
        if message.from_user.id not in passed:
            if not await is_served_user(message.from_user.id):
                upl = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="🚀 𝘾𝙡𝙞𝙘𝙠 𝙃𝙚𝙧𝙚 𝙩𝙤 𝙎𝙩𝙖𝙧𝙩",
                                url=f"https://t.me/{app.username}?start=verify",
                            ),
                        ]
                    ]
                )
                return await message.reply_text(
                    "⚠️  𝙀𝙧𝙧𝙤𝙧 , 𝙉𝙤𝙩 𝙖 𝙑𝙚𝙧𝙞𝙛𝙞𝙚𝙙 𝙐𝙨𝙚𝙧 ⚠️\n\n𝙋𝙡𝙚𝙖𝙨𝙚 𝙨𝙩𝙖𝙧𝙩 𝙩𝙝𝙚 𝙗𝙤𝙩 𝙞𝙣 𝙋𝙧𝙞𝙫𝙖𝙩𝙚 𝙈𝙚𝙨𝙨𝙖𝙜𝙚 𝘽𝙤𝙭 𝙁𝙞𝙧𝙨𝙩 𝙖𝙣𝙙 𝙏𝙝𝙚𝙣 𝙪𝙨𝙚 𝙞𝙩.",
                    reply_markup=upl,
                )
            else:
                passed.append(message.from_user.id)
        if message.chat.id not in checker:
            checker.append(message.chat.id)
            BOT_NAMES = [
                "YukkiOneBot",
                "YukkiTwoBot",
                "YukkiThreeBot",
                "YukkiFourBot",
                "YukkiFiveBot",
                "YukkiSixBot",
                "YukkiSevenBot",
                "YukkiEightBot",
                "YukkiNineBot",
                "YukkiTenBot",
                "CheemsMusicRobot",
                "CheemsVideoBot",
            ]
            if app.username in BOT_NAMES:
                if message.chat.id != LOG_GROUP_ID:
                    bots = await app.get_chat_members(message.chat.id, filter="bots")
                    for x in bots:
                        name = x.user.username
                        if name in BOT_NAMES:
                            if str(name) != str(app.username):
                                await app.send_message(
                                    message.chat.id,
                                    text="**Ehsaas Music Bots Abuse Protection**\n\nPlease maintain the dignity and usage of Yukki Bots, Add only one yukki bot in your chat.\n\nOther Yukki Bots present inside your chat will leave now.... Check status of bots on: @YukkiStatus",
                                )
                                try:
                                    from YukkiMusic import userbot

                                    ub = userbot.one
                                    await ub.send_message(
                                        LOG_GROUP_ID,
                                        f"/leaveallbotnowbropleasexxd {message.chat.id}",
                                    )
                                    break
                                except Exception as e:
                                    print(e)
        if await is_maintenance() is False:
            if message.from_user.id not in SUDOERS:
                return await message.reply_text(
                    "Bot is under maintenance. Please wait for some time..."
                )
        if PRIVATE_BOT_MODE == str(True):
            if not await is_served_private_chat(message.chat.id):
                await message.reply_text(
                    "**Private Music Bot**\n\nOnly for authorized chats from the owner. Ask my owner to allow your chat first."
                )
                return await app.leave_chat(message.chat.id)
        if await is_commanddelete_on(message.chat.id):
            try:
                await message.delete()
            except:
                pass
        audio_telegram = (
            (message.reply_to_message.audio or message.reply_to_message.voice)
            if message.reply_to_message
            else None
        )
        video_telegram = (
            (message.reply_to_message.video or message.reply_to_message.document)
            if message.reply_to_message
            else None
        )
        url = await YouTube.url(message)
        if audio_telegram is None and video_telegram is None and url is None:
            if len(message.command) < 2:
                if "stream" in message.command:
                    return await message.reply_text(_["str_1"])
                buttons = botplaylist_markup(_)
                return await message.reply_photo(
                    photo=PLAYLIST_IMG_URL,
                    caption=_["playlist_1"],
                    reply_markup=InlineKeyboardMarkup(buttons),
                )
        if message.command[0][0] == "c":
            chat_id = await get_cmode(message.chat.id)
            if chat_id is None:
                return await message.reply_text(_["setting_12"])
            try:
                chat = await app.get_chat(chat_id)
            except:
                return await message.reply_text(_["cplay_4"])
            channel = chat.title
        else:
            chat_id = message.chat.id
            channel = None
        playmode = await get_playmode(message.chat.id)
        playty = await get_playtype(message.chat.id)
        if playty != "Everyone":
            if message.from_user.id not in SUDOERS:
                admins = adminlist.get(message.chat.id)
                if not admins:
                    return await message.reply_text(_["admin_18"])
                else:
                    if message.from_user.id not in admins:
                        return await message.reply_text(_["play_4"])
        if message.command[0][0] == "v":
            video = True
        else:
            if "-v" in message.text:
                video = True
            else:
                video = True if message.command[0][1] == "v" else None
        if message.command[0][-1] == "e":
            if not await is_active_chat(chat_id):
                return await message.reply_text(_["play_18"])
            fplay = True
        else:
            fplay = None

        # Assistant Here now:

        if not await is_active_chat(chat_id):
            userbot = await get_assistant(chat_id)
            try:
                try:
                    get = await app.get_chat_member(chat_id, userbot.id)
                except ChatAdminRequired:
                    return await message.reply_text(
                        "𝘽𝙤𝙩 𝙧𝙚𝙦𝙪𝙞𝙧𝙚𝙨 **𝘼𝙙𝙢𝙞𝙣** 𝙋𝙚𝙧𝙢𝙞𝙨𝙨𝙞𝙤𝙣 𝙩𝙤 𝙞𝙣𝙫𝙞𝙩𝙚 𝙖𝙨𝙨𝙞𝙨𝙩𝙖𝙣𝙩 𝙖𝙘𝙘𝙤𝙪𝙣𝙩 𝙩𝙤 𝙮𝙤𝙪𝙧 𝙘𝙝𝙖𝙣𝙣𝙚𝙡"
                    )
                if get.status == "banned" or get.status == "kicked":
                    upl = InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text="Unban Assistant",
                                    callback_data=f"unban_assistant {chat_id}|{userbot.id}",
                                ),
                            ]
                        ]
                    )
                    return await message.reply_text(
                        f"𝘼𝙨𝙨𝙞𝙨𝙩𝙖𝙣𝙩 𝙞𝙨 𝙗𝙖𝙣𝙣𝙚𝙙 𝙞𝙣 𝙮𝙤𝙪𝙧 𝙜𝙧𝙤𝙪𝙥 𝙤𝙧 𝙘𝙝𝙖𝙣𝙣𝙚𝙡, 𝙥𝙡𝙚𝙖𝙨𝙚 𝙪𝙣𝙗𝙖𝙣.\n\n**Assistant Username:** @{userbot.username}\n**Assistant ID:** {userbot.id}",
                        reply_markup=upl,
                    )
            except UserNotParticipant:
                if chat_id in links:
                    invitelink = links[chat_id]
                else:
                    if message.chat.username:
                        invitelink = message.chat.username
                        try:
                            await userbot.resolve_peer(invitelink)
                        except Exception as e:
                            print(e)
                            pass
                    else:
                        try:
                            invitelink = await app.export_chat_invite_link(chat_id)
                        except ChatAdminRequired:
                            return await message.reply_text(
                                "𝘽𝙤𝙩 𝙧𝙚𝙦𝙪𝙞𝙧𝙚𝙨 **Invite Users Via Link** 𝘼𝙙𝙢𝙞𝙣 𝙋𝙚𝙧𝙢𝙞𝙨𝙨𝙞𝙤𝙣 𝙩𝙤 𝙞𝙣𝙫𝙞𝙩𝙚 𝙖𝙨𝙨𝙞𝙨𝙩𝙖𝙣𝙩 𝙖𝙘𝙘𝙤𝙪𝙣𝙩 𝙩𝙤 𝙮𝙤𝙪𝙧 𝙘𝙝𝙖𝙩 𝙜𝙧𝙤𝙪𝙥.\n𝙋𝙡𝙚𝙖𝙨𝙚 𝙜𝙞𝙫𝙚 𝘽𝙤𝙩 𝙩𝙝𝙚 𝙖𝙙𝙢𝙞𝙣 𝙥𝙚𝙧𝙢𝙞𝙨𝙨𝙞𝙤𝙣."
                            )
                        except Exception as e:
                            return await message.reply_text(
                                f"𝙀𝙧𝙧𝙤𝙧 𝙊𝙘𝙘𝙪𝙧𝙚𝙙 𝙒𝙝𝙞𝙡𝙚 𝙄𝙣𝙫𝙞𝙩𝙞𝙣𝙜 𝘼𝙨𝙨𝙞𝙨𝙩𝙖𝙣𝙩 𝘼𝙘𝙘𝙤𝙪𝙣𝙩 𝙩𝙤 𝙮𝙤𝙪𝙧 𝙘𝙝𝙖𝙩.\n\n**Reason**: {e}"
                            )

                if invitelink.startswith("https://t.me/+"):
                    invitelink = invitelink.replace(
                        "https://t.me/+", "https://t.me/joinchat/"
                    )
                myu = await message.reply_text(
                    "𝘼𝙨𝙨𝙞𝙨𝙩𝙖𝙣𝙩 𝘼𝙘𝙘𝙤𝙪𝙣𝙩 𝙬𝙞𝙡𝙡 𝙗𝙚 𝙟𝙤𝙞𝙣𝙞𝙣𝙜 𝙞𝙣 5 𝙎𝙚𝙘𝙤𝙣𝙙𝙨..𝙋𝙡𝙚𝙖𝙨𝙚 𝙒𝙖𝙞𝙩...!"
                )
                try:
                    await asyncio.sleep(5)
                    await userbot.join_chat(invitelink)
                    await asyncio.sleep(2)
                    await myu.edit(
                        f"𝘼𝙨𝙨𝙞𝙨𝙩𝙖𝙣𝙩 𝘼𝙘𝙘𝙤𝙪𝙣𝙩[{userbot.name}] 𝙅𝙤𝙞𝙣𝙚𝙙 𝙎𝙪𝙘𝙘𝙚𝙨𝙨𝙛𝙪𝙡𝙡𝙮.\n\n𝙎𝙩𝙖𝙧𝙩𝙞𝙣𝙜 𝙈𝙪𝙨𝙞𝙘 𝙉𝙤𝙬"
                    )
                except UserAlreadyParticipant:
                    pass
                except Exception as e:
                    return await message.reply_text(
                        f"𝙀𝙧𝙧𝙤𝙧 𝙊𝙘𝙘𝙪𝙧𝙚𝙙 𝙒𝙝𝙞𝙡𝙚 𝙄𝙣𝙫𝙞𝙩𝙞𝙣𝙜 𝘼𝙨𝙨𝙞𝙨𝙩𝙖𝙣𝙩 𝘼𝙘𝙘𝙤𝙪𝙣𝙩 𝙩𝙤 𝙮𝙤𝙪𝙧 𝙘𝙝𝙖𝙩.\n\n**Reason**: {e}"
                    )

                links[chat_id] = invitelink

                try:
                    await userbot.resolve_peer(chat_id)
                except:
                    pass

        return await command(
            client,
            message,
            _,
            chat_id,
            video,
            channel,
            playmode,
            url,
            fplay,
        )

    return wrapper
