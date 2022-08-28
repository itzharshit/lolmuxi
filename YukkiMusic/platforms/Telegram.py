#
# Copyright (C) 2021-2022 by TeamYukki@Github, < https://github.com/TeamYukki >.
#
# This file is part of < https://github.com/TeamYukki/YukkiMusicBot > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/TeamYukki/YukkiMusicBot/blob/master/LICENSE >
#
# All rights reserved.

import asyncio
import os
import time
from datetime import datetime, timedelta
from typing import Union

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Voice

import config
from config import MUSIC_BOT_NAME, lyrical
from YukkiMusic import app

from ..utils.formatters import (check_duration, convert_bytes, get_readable_time,
                                seconds_to_min)

downloader = {}
loop = asyncio.get_event_loop()


class TeleAPI:
    def __init__(self):
        self.chars_limit = 4096
        self.sleep = config.TELEGRAM_DOWNLOAD_EDIT_SLEEP

    async def send_split_text(self, message, string):
        n = self.chars_limit
        out = [(string[i : i + n]) for i in range(0, len(string), n)]
        j = 0
        for x in out:
            if j <= 2:
                j += 1
                await message.reply_text(x)
        return True

    async def get_link(self, message):
        if message.chat.username:
            link = f"https://t.me/{message.chat.username}/{message.reply_to_message.message_id}"
        else:
            xf = str((message.chat.id))[4:]
            link = f"https://t.me/c/{xf}/{message.reply_to_message.message_id}"
        return link

    async def get_filename(self, file, audio: Union[bool, str] = None):
        try:
            file_name = file.file_name
            if file_name is None:
                file_name = "Telegram Audio File" if audio else "Telegram Video File"

        except:
            file_name = "Telegram Audio File" if audio else "Telegram Video File"
        return file_name

    async def get_duration(self, file):
        try:
            dur = seconds_to_min(file.duration)
        except:
            dur = "Unknown"
        return dur

    async def get_duration(self, filex, file_path):
        try:
            dur = seconds_to_min(filex.duration)
        except:
            try:
                dur = await loop.run_in_executor(None, check_duration, file_path)
                dur = seconds_to_min(dur)
            except:
                return "Unknown"
        return dur

    async def get_filepath(
        self,
        audio: Union[bool, str] = None,
        video: Union[bool, str] = None,
    ):
        if audio:
            try:
                file_name = (
                    audio.file_unique_id
                    + "."
                    + (
                        (audio.file_name.split(".")[-1])
                        if (not isinstance(audio, Voice))
                        else "ogg"
                    )
                )
            except:
                file_name = audio.file_unique_id + "." + "ogg"
            file_name = os.path.join(os.path.realpath("downloads"), file_name)
        if video:
            try:
                file_name = video.file_unique_id + "." + (video.file_name.split(".")[-1])
            except:
                file_name = video.file_unique_id + "." + "mp4"
            file_name = os.path.join(os.path.realpath("downloads"), file_name)
        return file_name

    async def download(self, _, message, mystic, fname):
        lower = [0, 8, 17, 38, 64, 77, 96]
        higher = [5, 10, 20, 40, 66, 80, 99]
        checker = [5, 10, 20, 40, 66, 80, 99]
        speed_counter = {}
        if os.path.exists(fname):
            return True

        async def down_load():
            async def progress(current, total):
                if current == total:
                    return
                current_time = time.time()
                start_time = speed_counter.get(message.message_id)
                check_time = current_time - start_time
                upl = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="🚦 Cancel Downloading",
                                callback_data="stop_downloading",
                            ),
                        ]
                    ]
                )
                percentage = current * 100 / total
                percentage = str(round(percentage, 2))
                speed = current / check_time
                eta = int((total - current) / speed)
                eta = get_readable_time(eta)
                if not eta:
                    eta = "0 sec"
                total_size = convert_bytes(total)
                completed_size = convert_bytes(current)
                speed = convert_bytes(speed)
                text = f"""
**{MUSIC_BOT_NAME} 𝙏𝙚𝙡𝙚𝙜𝙧𝙖𝙢 𝙢𝙚𝙙𝙞𝙖 𝙙𝙤𝙬𝙣𝙡𝙤𝙖𝙙𝙚𝙧**

**Total FileSize:** {total_size}
**Completed:** {completed_size} 
**Percentage:** {percentage[:5]}%

**Speed:** {speed}/s
**ETA:** {eta}"""
                percentage = int((percentage.split("."))[0])
                for counter in range(7):
                    low = int(lower[counter])
                    high = int(higher[counter])
                    check = int(checker[counter])
                    if low < percentage <= high:
                        if high == check:
                            try:
                                await mystic.edit_text(text, reply_markup=upl)
                                checker[counter] = 100
                            except:
                                pass

            speed_counter[message.message_id] = time.time()
            try:
                await app.download_media(
                    message.reply_to_message,
                    file_name=fname,
                    progress=progress,
                )
                try:
                    elapsed = get_readable_time(
                        int(int(time.time()) - int(speed_counter[message.message_id]))
                    )
                except:
                    elapsed = "0 seconds"
                await mystic.edit_text(
                    f"𝙎𝙪𝙘𝙘𝙚𝙨𝙨𝙛𝙪𝙡𝙡𝙮 𝘿𝙤𝙬𝙣𝙡𝙤𝙖𝙙𝙚𝙙.. 𝙋𝙧𝙤𝙘𝙚𝙨𝙨𝙞𝙣𝙜 𝙛𝙞𝙡𝙚 𝙣𝙤𝙬\n\n**𝙏𝙞𝙢𝙚 𝙀𝙡𝙖𝙥𝙨𝙚𝙙 : {elapsed}"
                )
            except:
                await mystic.edit_text(_["tg_2"])

        task = asyncio.create_task(down_load())
        lyrical[mystic.message_id] = task
        await task
        verify = lyrical.get(mystic.message_id)
        if not verify:
            return False
        lyrical.pop(mystic.message_id)
        return True
