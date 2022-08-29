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
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from youtubesearchpython.__future__ import VideosSearch

import config
from config import BANNED_USERS
from config.config import OWNER_ID
from strings import get_command, get_string
from YukkiMusic import Telegram, YouTube, app, userbot
from YukkiMusic.misc import SUDOERS
from YukkiMusic.plugins.play.playlist import del_plist_msg
from YukkiMusic.plugins.sudo.sudoers import sudoers_list
from YukkiMusic.utils.database import (add_served_chat, add_served_user,
                                       blacklisted_chats, get_assistant, get_lang,
                                       get_userss, is_on_off, is_served_private_chat)
from YukkiMusic.utils.database.mongodatabase import is_banned_user, is_gbanned_user
from YukkiMusic.utils.decorators.language import LanguageStart
from YukkiMusic.utils.inline import help_pannel, private_panel, start_pannel

loop = asyncio.get_running_loop()


@app.on_message(
    filters.command(get_command("START_COMMAND"))
    & filters.private
    & ~filters.edited
    & ~BANNED_USERS
)
@LanguageStart
async def start_comm(client, message: Message, _):
    await add_served_user(message.from_user.id)
    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]
        if name[0:4] == "veri":
            return await message.reply_text(
                "𝙏𝙝𝙖𝙣𝙠 𝙔𝙤𝙪 𝙛𝙤𝙧 𝙎𝙩𝙖𝙧𝙩𝙞𝙣𝙜 𝙈𝙚 𝙞𝙣 𝙋𝙧𝙞𝙫𝙖𝙩𝙚 𝙈𝙚𝙨𝙨𝙖𝙜𝙚 𝘽𝙤𝙭. 𝙔𝙤𝙪 𝙖𝙧𝙚 𝙉𝙤𝙬 𝙑𝙚𝙧𝙞𝙛𝙞𝙚𝙙 ✅. 𝙋𝙡𝙚𝙖𝙨𝙚 𝙂𝙤 𝙗𝙖𝙘𝙠 𝘼𝙣𝙙 𝙎𝙩𝙖𝙧𝙩 𝙐𝙨𝙞𝙣𝙜 𝙏𝙝𝙚 𝘽𝙤𝙩."
            )
        if name[0:4] == "help":
            keyboard = help_pannel(_)
            return await message.reply_text(_["help_1"], reply_markup=keyboard)
        if name[0:4] == "song":
            return await message.reply_text(_["song_2"])
        if name[0:3] == "sta":
            m = await message.reply_text("🔎 Fetching your personal stats.!")
            stats = await get_userss(message.from_user.id)
            tot = len(stats)
            if not stats:
                await asyncio.sleep(1)
                return await m.edit(_["ustats_1"])

            def get_stats():
                msg = ""
                limit = 0
                results = {}
                for i in stats:
                    top_list = stats[i]["spot"]
                    results[str(i)] = top_list
                    list_arranged = dict(
                        sorted(
                            results.items(),
                            key=lambda item: item[1],
                            reverse=True,
                        )
                    )
                if not results:
                    return m.edit(_["ustats_1"])
                tota = 0
                videoid = None
                for vidid, count in list_arranged.items():
                    tota += count
                    if limit == 10:
                        continue
                    if limit == 0:
                        videoid = vidid
                    limit += 1
                    details = stats.get(vidid)
                    title = (details["title"][:35]).title()
                    if vidid == "telegram":
                        msg += f"🔗[𝙏𝙚𝙡𝙚𝙜𝙧𝙖𝙢 𝙁𝙞𝙡𝙚𝙨 𝙖𝙣𝙙 𝘼𝙪𝙙𝙞𝙤𝙨](https://t.me/telegram) ** 𝙥𝙡𝙖𝙮𝙚𝙙 {count} 𝙩𝙞𝙢𝙚𝙨**\n\n"
                    else:
                        msg += f"🔗 [{title}](https://www.youtube.com/watch?v={vidid}) ** 𝙥𝙡𝙖𝙮𝙚𝙙 {count} 𝙩𝙞𝙢𝙚𝙨**\n\n"
                msg = _["ustats_2"].format(tot, tota, limit) + msg
                return videoid, msg

            try:
                videoid, msg = await loop.run_in_executor(None, get_stats)
            except Exception as e:
                print(e)
                return
            thumbnail = await YouTube.thumbnail(videoid, True)
            await m.delete()
            await message.reply_photo(photo=thumbnail, caption=msg)
            return
        if name[0:3] == "sud":
            await sudoers_list(client=client, message=message, _=_)
            if await is_on_off(config.LOG):
                sender_id = message.from_user.id
                sender_name = message.from_user.first_name
                return await app.send_message(
                    config.LOG_GROUP_ID,
                    f"{message.from_user.mention} has just started bot to check <code>SUDOLIST</code>\n\n**USER ID:** {sender_id}\n**USER NAME:** {sender_name}",
                )
            return
        if name[0:3] == "lyr":
            query = (str(name)).replace("lyrics_", "", 1)
            lyrical = config.lyrical
            lyrics = lyrical.get(query)
            if lyrics:
                return await Telegram.send_split_text(message, lyrics)
            else:
                return await message.reply_text("Failed to get lyrics.")
        if name[0:3] == "del":
            await del_plist_msg(client=client, message=message, _=_)
        if name[0:3] == "inf":
            m = await message.reply_text("🔎 Fetching Info!")
            query = (str(name)).replace("info_", "", 1)
            query = f"https://www.youtube.com/watch?v={query}"
            results = VideosSearch(query, limit=1)
            for result in (await results.next())["result"]:
                title = result["title"]
                duration = result["duration"]
                views = result["viewCount"]["short"]
                thumbnail = result["thumbnails"][0]["url"].split("?")[0]
                channellink = result["channel"]["link"]
                channel = result["channel"]["name"]
                link = result["link"]
                published = result["publishedTime"]
            searched_text = f"""
🔍__**Video Track Information**__

❇️**Title:** {title}

⏳**Duration:** {duration} Mins
👀**Views:** `{views}`
⏰**Published Time:** {published}
🎥**Channel Name:** {channel}
📎**Channel Link:** [Visit From Here]({channellink})
🔗**Video Link:** [Link]({link})

⚡️ __Searched Powered By {config.MUSIC_BOT_NAME}__"""
            key = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text="🎥 Watch ", url=f"{link}"),
                        InlineKeyboardButton(text="🔄 Close", callback_data="close"),
                    ],
                ]
            )
            await m.delete()
            await app.send_photo(
                message.chat.id,
                photo=thumbnail,
                caption=searched_text,
                parse_mode="markdown",
                reply_markup=key,
            )
            if await is_on_off(config.LOG):
                sender_id = message.from_user.id
                sender_name = message.from_user.first_name
                return await app.send_message(
                    config.LOG_GROUP_ID,
                    f"{message.from_user.mention} 𝙝𝙖𝙨 𝙟𝙪𝙨𝙩 𝙨𝙩𝙖𝙧𝙩𝙚𝙙 𝙗𝙤𝙩 𝙩𝙤 𝙘𝙝𝙚𝙘𝙠 <code>VIDEO INFORMATION</code>\n\n**USER ID:** {sender_id}\n**USER NAME:** {sender_name}",
                )
    else:
        try:
            await app.resolve_peer(OWNER_ID[0])
            OWNER = OWNER_ID[0]
        except:
            OWNER = None
        out = private_panel(_, app.username, OWNER)
        if config.START_IMG_URL:
            try:
                await message.reply_photo(
                    photo=config.START_IMG_URL,
                    caption=_["start_2"].format(config.MUSIC_BOT_NAME),
                    reply_markup=InlineKeyboardMarkup(out),
                )
            except:
                await message.reply_text(
                    _["start_2"].format(config.MUSIC_BOT_NAME),
                    reply_markup=InlineKeyboardMarkup(out),
                )
        else:
            await message.reply_text(
                _["start_2"].format(config.MUSIC_BOT_NAME),
                reply_markup=InlineKeyboardMarkup(out),
            )
        if await is_on_off(config.LOG):
            sender_id = message.from_user.id
            sender_name = message.from_user.first_name
            return await app.send_message(
                config.LOG_GROUP_ID,
                f"{message.from_user.mention} 𝙝𝙖𝙨 𝙟𝙪𝙨𝙩 𝙨𝙩𝙖𝙧𝙩𝙚𝙙 𝙗𝙤𝙩.\n\n**USER ID:** {sender_id}\n**USER NAME:** {sender_name}",
            )


@app.on_message(
    filters.command(get_command("START_COMMAND"))
    & filters.group
    & ~filters.edited
    & ~BANNED_USERS
)
@LanguageStart
async def testbot(client, message: Message, _):
    out = start_pannel(_)
    return await message.reply_text(
        _["start_1"].format(message.chat.title, config.MUSIC_BOT_NAME),
        reply_markup=InlineKeyboardMarkup(out),
    )


welcome_group = 2
checked = []


@app.on_message(filters.new_chat_members, group=welcome_group)
async def welcome(client, message: Message):
    chat_id = message.chat.id
    if config.PRIVATE_BOT_MODE == str(True):
        if not await is_served_private_chat(message.chat.id):
            await message.reply_text(
                "**𝙋𝙧𝙞𝙫𝙖𝙩𝙚 𝙈𝙪𝙨𝙞𝙘 𝘽𝙤𝙩**\n\n𝙊𝙣𝙡𝙮 𝙛𝙤𝙧 𝙖𝙪𝙩𝙝𝙤𝙧𝙞𝙯𝙚𝙙 𝙘𝙝𝙖𝙩𝙨 𝙛𝙧𝙤𝙢 𝙩𝙝𝙚 𝙤𝙬𝙣𝙚𝙧. 𝘼𝙨𝙠 𝙢𝙮 𝙤𝙬𝙣𝙚𝙧 𝙩𝙤 𝙖𝙡𝙡𝙤𝙬 𝙮𝙤𝙪𝙧 𝙘𝙝𝙖𝙩 𝙛𝙞𝙧𝙨𝙩."
            )
            return await app.leave_chat(message.chat.id)
    else:
        await add_served_chat(chat_id)
    for member in message.new_chat_members:
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)
            if await is_banned_user(member.id):
                try:
                    await message.chat.ban_member(member.id)
                    await message.reply_text(
                        "𝙏𝙝𝙞𝙨 𝙪𝙨𝙚𝙧 𝙞𝙨 𝙜𝙡𝙤𝙗𝙖𝙡𝙡𝙮 𝙗𝙖𝙣𝙣𝙚𝙙 𝙖𝙣𝙙 𝙢𝙖𝙧𝙠𝙚𝙙 𝙖𝙨 𝙥𝙤𝙩𝙚𝙣𝙩𝙞𝙖𝙡 𝙨𝙘𝙖𝙢𝙢𝙚𝙧 𝙤𝙧 𝙨𝙥𝙖𝙢𝙢𝙚𝙧, 𝙏𝙝𝙪𝙨 𝙗𝙖𝙣𝙣𝙚𝙙."
                    )
                except:
                    pass
            if member.id == app.id:
                chat_type = message.chat.type
                if chat_type != "supergroup":
                    await message.reply_text(_["start_6"])
                    return await app.leave_chat(message.chat.id)
                if chat_id in await blacklisted_chats():
                    await message.reply_text(
                        _["start_7"].format(f"https://t.me/{app.username}?start=sudolist")
                    )
                    return await app.leave_chat(chat_id)
                if chat_id != config.LOG_GROUP_ID:
                    BOT_NAMES = [
                        "Pyrogrammers",
                    ]
                    if app.username in BOT_NAMES:
                        bots = await app.get_chat_members(message.chat.id, filter="bots")
                        for x in bots:
                            name = x.user.username
                            if name in BOT_NAMES:
                                if str(name) != str(app.username):
                                    await app.send_message(
                                        chat_id,
                                        text="**𝙀𝙝𝙨𝙖𝙖𝙨 𝙈𝙪𝙨𝙞𝙘 𝘽𝙤𝙩𝙨 𝘼𝙗𝙪𝙨𝙚 𝙋𝙧𝙤𝙩𝙚𝙘𝙩𝙞𝙤𝙣**\n\n𝙋𝙡𝙚𝙖𝙨𝙚 𝙢𝙖𝙞𝙣𝙩𝙖𝙞𝙣 𝙩𝙝𝙚 𝙙𝙞𝙜𝙣𝙞𝙩𝙮 𝙖𝙣𝙙 𝙪𝙨𝙖𝙜𝙚 𝙤𝙛 𝙀𝙝𝙨𝙖𝙖𝙨 𝘽𝙤𝙩𝙨, 𝘼𝙙𝙙 𝙤𝙣𝙡𝙮 𝙤𝙣𝙚 𝙀𝙝𝙨𝙖𝙖𝙨 𝙗𝙤𝙩 𝙞𝙣 𝙮𝙤𝙪𝙧 𝙘𝙝𝙖𝙩.\n\n𝙊𝙩𝙝𝙚𝙧 𝙀𝙝𝙨𝙖𝙖𝙨 𝘽𝙤𝙩𝙨 𝙥𝙧𝙚𝙨𝙚𝙣𝙩 𝙞𝙣𝙨𝙞𝙙𝙚 𝙮𝙤𝙪𝙧 𝙘𝙝𝙖𝙩 𝙬𝙞𝙡𝙡 𝙡𝙚𝙖𝙫𝙚 𝙣𝙤𝙬....",
                                    )
                                    try:
                                        from YukkiMusic import userbot

                                        ub = userbot.one
                                        await ub.send_message(
                                            config.LOG_GROUP_ID,
                                            f"/leaveallbotnowbropleasexxd {message.chat.id}",
                                        )
                                        break
                                    except Exception as e:
                                        print(e)

                userbot = await get_assistant(message.chat.id)
                out = start_pannel(_)
                await message.reply_text(
                    _["start_3"].format(
                        config.MUSIC_BOT_NAME,
                        userbot.username,
                        userbot.id,
                    ),
                    reply_markup=InlineKeyboardMarkup(out),
                )
            if member.id in config.OWNER_ID:
                return await message.reply_text(
                    _["start_4"].format(config.MUSIC_BOT_NAME, member.mention)
                )
            if member.id in SUDOERS:
                return await message.reply_text(
                    _["start_5"].format(config.MUSIC_BOT_NAME, member.mention)
                )
            return
        except:
            return


@app.on_message(filters.command("leaveallbotnowbropleasexxd"))
async def leaveallbot(_, message):
    if message.chat.id != config.LOG_GROUP_ID:
        return await message.reply_text("Lol BRO!")
    user_id = message.from_user.id
    userbot = await get_assistant(message.chat.id)
    if user_id == userbot.id:
        return
    chat = message.text.split(None, 2)[1]
    try:
        await userbot.leave_chat(chat)
    except:
        pass
    try:
        await app.leave_chat(chat)
    except Exception as e:
        return
    return await message.delete()
