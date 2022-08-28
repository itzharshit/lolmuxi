#
# Copyright (C) 2021-2022 by TeamYukki@Github, < https://github.com/TeamYukki >.
#
# This file is part of < https://github.com/TeamYukki/YukkiMusicBot > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/TeamYukki/YukkiMusicBot/blob/master/LICENSE >
#
# All rights reserved.

from pyrogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                            InlineQueryResultPhoto)
from youtubesearchpython.__future__ import VideosSearch

from config import BANNED_USERS, MUSIC_BOT_NAME
from YukkiMusic import app
from YukkiMusic.utils.inlinequery import answer


@app.on_inline_query(~BANNED_USERS)
async def inline_query_handler(client, query):
    text = query.query.strip().lower()
    answers = []
    if text.strip() == "":
        try:
            await client.answer_inline_query(query.id, results=answer, cache_time=10)
        except:
            return
    else:
        a = VideosSearch(text, limit=20)
        result = (await a.next()).get("result")
        for x in range(15):
            title = (result[x]["title"]).title()
            duration = result[x]["duration"]
            views = result[x]["viewCount"]["short"]
            thumbnail = result[x]["thumbnails"][0]["url"].split("?")[0]
            channellink = result[x]["channel"]["link"]
            channel = result[x]["channel"]["name"]
            link = result[x]["link"]
            published = result[x]["publishedTime"]
            description = f"{views} | {duration} Mins | {channel}  | {published}"
            buttons = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="🎥 𝙒𝙖𝙩𝙘𝙝 𝙤𝙣 𝙔𝙤𝙪𝙩𝙪𝙗𝙚",
                            url=link,
                        )
                    ],
                ]
            )
            searched_text = f"""
❇️**Title:** [{title}]({link})

⏳**Duration:** {duration} Mins
👀**Views:** `{views}`
⏰**Published Time:** {published}
🎥**Channel Name:** {channel}
📎**Channel Link:** [𝙑𝙞𝙨𝙞𝙩 𝙁𝙧𝙤𝙢 𝙃𝙚𝙧𝙚]({channellink})

𝙍𝙚𝙥𝙡𝙮 𝙬𝙞𝙩𝙝 /play 𝙤𝙣 𝙩𝙝𝙞𝙨 𝙨𝙚𝙖𝙧𝙘𝙝𝙚𝙙 𝙢𝙚𝙨𝙨𝙖𝙜𝙚 𝙩𝙤 𝙨𝙩𝙧𝙚𝙖𝙢 𝙞𝙩 𝙤𝙣 𝙫𝙤𝙞𝙘𝙚 𝙘𝙝𝙖𝙩.

⚡️ ** 𝙄𝙣𝙡𝙞𝙣𝙚 𝙎𝙚𝙖𝙧𝙘𝙝 𝘽𝙮 {MUSIC_BOT_NAME} **"""
            answers.append(
                InlineQueryResultPhoto(
                    photo_url=thumbnail,
                    title=title,
                    thumb_url=thumbnail,
                    description=description,
                    caption=searched_text,
                    reply_markup=buttons,
                )
            )
        try:
            return await client.answer_inline_query(query.id, results=answers)
        except:
            return
