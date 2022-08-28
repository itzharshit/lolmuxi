#
# Copyright (C) 2021-2022 by TeamYukki@Github, < https://github.com/TeamYukki >.
#
# This file is part of < https://github.com/TeamYukki/YukkiMusicBot > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/TeamYukki/YukkiMusicBot/blob/master/LICENSE >
#
# All rights reserved.

import asyncio
from datetime import datetime

import config
from YukkiMusic import app
from YukkiMusic.core.call import Yukki, autoend, automuted
from YukkiMusic.utils.database import get_client, is_active_chat, is_autoend


async def auto_leave():
    if str(True) in config.AUTO_LEAVING_ASSISTANT:
        while not await asyncio.sleep(10000):
            from YukkiMusic.core.userbot import assistants

            for num in assistants:
                client = await get_client(num)
                left = 0
                try:
                    async for i in client.iter_dialogs():
                        chat_type = i.chat.type
                        if chat_type in [
                            "supergroup",
                            "group",
                            "channel",
                        ]:
                            chat_id = i.chat.id
                            if (
                                chat_id != config.LOG_GROUP_ID
                                and chat_id != -1001190342892
                                and chat_id != -1001733534088
                                and chat_id != -1001443281821
                            ):
                                if left == 20:
                                    continue
                                if not await is_active_chat(chat_id):
                                    try:
                                        await client.leave_chat(chat_id)
                                        left += 1
                                    except:
                                        continue
                except:
                    pass


asyncio.create_task(auto_leave())


async def auto_end():
    while not await asyncio.sleep(5):
        for chat_id in automuted:
            timer = automuted.get(chat_id)
            if not timer:
                continue
            if datetime.now() > timer:
                if not await is_active_chat(chat_id):
                    automuted[chat_id] = {}
                    continue
                automuted[chat_id] = {}
                try:
                    await Yukki.stop_stream(chat_id)
                except:
                    continue
                try:
                    await app.send_message(
                        chat_id,
                        "𝘽𝙤𝙩 𝙝𝙖𝙨 𝙡𝙚𝙛𝙩 𝙫𝙤𝙞𝙘𝙚 𝙘𝙝𝙖𝙩 𝙖𝙨 𝙞𝙩 𝙬𝙖𝙨 𝙢𝙪𝙩𝙚𝙙 𝙛𝙤𝙧 𝙢𝙤𝙧𝙚 𝙩𝙝𝙖𝙣 3 𝙢𝙞𝙣𝙨 𝙞𝙣 𝙫𝙤𝙞𝙘𝙚 𝙘𝙝𝙖𝙩. 𝙋𝙡𝙚𝙖𝙨𝙚 𝙧𝙚𝙨𝙥𝙚𝙘𝙩 𝙩𝙝𝙚 𝙗𝙤𝙩 𝙖𝙣𝙙 𝙙𝙤𝙣'𝙩 𝙖𝙗𝙪𝙨𝙚 𝙞𝙩 𝙗𝙮 𝙥𝙡𝙖𝙮𝙞𝙣𝙜 𝙢𝙪𝙨𝙞𝙘 𝙤𝙣 𝙢𝙪𝙩𝙚.",
                    )
                except:
                    continue
        ender = await is_autoend()
        if not ender:
            continue
        for chat_id in autoend:
            timer = autoend.get(chat_id)
            if not timer:
                continue
            if datetime.now() > timer:
                if not await is_active_chat(chat_id):
                    autoend[chat_id] = {}
                    continue
                autoend[chat_id] = {}
                try:
                    await Yukki.stop_stream(chat_id)
                except:
                    continue
                try:
                    await app.send_message(
                        chat_id,
                        "𝘽𝙤𝙩 𝙝𝙖𝙨 𝙡𝙚𝙛𝙩 𝙫𝙤𝙞𝙘𝙚 𝙘𝙝𝙖𝙩 𝙙𝙪𝙚 𝙩𝙤 𝙞𝙣𝙖𝙘𝙩𝙞𝙫𝙞𝙩𝙮 𝙩𝙤 𝙖𝙫𝙤𝙞𝙙 𝙤𝙫𝙚𝙧𝙡𝙤𝙖𝙙 𝙤𝙣 𝙨𝙚𝙧𝙫𝙚𝙧𝙨. 𝙉𝙤-𝙤𝙣𝙚 𝙬𝙖𝙨 𝙡𝙞𝙨𝙩𝙚𝙣𝙞𝙣𝙜 𝙩𝙤 𝙩𝙝𝙚 𝙗𝙤𝙩 𝙤𝙣 𝙫𝙤𝙞𝙘𝙚 𝙘𝙝𝙖𝙩.",
                    )
                except:
                    continue


asyncio.create_task(auto_end())
