#
# Copyright (C) 2021-2022 by TeamYukki@Github, < https://github.com/TeamYukki >.
#
# This file is part of < https://github.com/TeamYukki/YukkiMusicBot > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/TeamYukki/YukkiMusicBot/blob/master/LICENSE >
#
# All rights reserved.

import asyncio
import math
import os
import shutil
import socket
from datetime import datetime

import dotenv
import heroku3
import requests
import urllib3
from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError
from pyrogram import filters

import config
from strings import get_command
from YukkiMusic import app
from YukkiMusic.misc import HAPP, SUDOERS, XCB
from YukkiMusic.utils.database import (get_active_chats, remove_active_chat,
                                       remove_active_video_chat)
from YukkiMusic.utils.decorators.language import language
from YukkiMusic.utils.pastebin import Yukkibin

# Commands
GETLOG_COMMAND = get_command("GETLOG_COMMAND")
GETVAR_COMMAND = get_command("GETVAR_COMMAND")
DELVAR_COMMAND = get_command("DELVAR_COMMAND")
SETVAR_COMMAND = get_command("SETVAR_COMMAND")
USAGE_COMMAND = get_command("USAGE_COMMAND")
UPDATE_COMMAND = get_command("UPDATE_COMMAND")
REBOOT_COMMAND = get_command("REBOOT_COMMAND")

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


async def is_heroku():
    return "heroku" in socket.getfqdn()


@app.on_message(filters.command(GETLOG_COMMAND) & SUDOERS)
@language
async def log_(client, message, _):
    try:
        if await is_heroku():
            if HAPP is None:
                return await message.reply_text(_["heroku_1"])
            data = HAPP.get_log()
            link = await Yukkibin(data)
            return await message.reply_text(link)
        else:
            if os.path.exists(config.LOG_FILE_NAME):
                log = open(config.LOG_FILE_NAME)
                lines = log.readlines()
                data = ""
                try:
                    NUMB = int(message.text.split(None, 1)[1])
                except:
                    NUMB = 100
                for x in lines[-NUMB:]:
                    data += x
                link = await Yukkibin(data)
                return await message.reply_text(link)
            else:
                return await message.reply_text(_["heroku_2"])
    except Exception as e:
        print(e)
        await message.reply_text(_["heroku_2"])


@app.on_message(filters.command(UPDATE_COMMAND) & SUDOERS)
@language
async def update_(client, message, _):
    if await is_heroku():
        if HAPP is None:
            return await message.reply_text(_["heroku_1"])
    response = await message.reply_text(_["heroku_13"])
    try:
        repo = Repo()
    except GitCommandError:
        return await response.edit(_["heroku_14"])
    except InvalidGitRepositoryError:
        return await response.edit(_["heroku_15"])
    to_exc = f"git fetch origin {config.UPSTREAM_BRANCH} &> /dev/null"
    os.system(to_exc)
    await asyncio.sleep(7)
    verification = ""
    REPO_ = repo.remotes.origin.url.split(".git")[0]  # main git repository
    for checks in repo.iter_commits(f"HEAD..origin/{config.UPSTREAM_BRANCH}"):
        verification = str(checks.count())
    if verification == "":
        return await response.edit("Bot is up-to-date!")
    updates = ""
    ordinal = lambda format: "%d%s" % (
        format,
        "tsnrhtdd"[(format // 10 % 10 != 1) * (format % 10 < 4) * format % 10 :: 4],
    )
    for info in repo.iter_commits(f"HEAD..origin/{config.UPSTREAM_BRANCH}"):
        updates += f"<b>➣ #{info.count()}: [{info.summary}]({REPO_}/commit/{info}) by -> {info.author}</b>\n\t\t\t\t<b>➥ Commited on:</b> {ordinal(int(datetime.fromtimestamp(info.committed_date).strftime('%d')))} {datetime.fromtimestamp(info.committed_date).strftime('%b')}, {datetime.fromtimestamp(info.committed_date).strftime('%Y')}\n\n"
    _update_response_ = "<b>A new update is available for the Bot!</b>\n\n➣ Pushing Updates Now</code>\n\n**<u>Updates:</u>**\n\n"
    _final_updates_ = _update_response_ + updates
    if len(_final_updates_) > 4096:
        url = await Yukkibin(updates)
        nrs = await response.edit(
            f"<b>𝘼 𝙣𝙚𝙬 𝙪𝙥𝙙𝙖𝙩𝙚 𝙞𝙨 𝙖𝙫𝙖𝙞𝙡𝙖𝙗𝙡𝙚 𝙛𝙤𝙧 𝙩𝙝𝙚 𝘽𝙤𝙩!</b>\n\n➣ 𝙋𝙪𝙨𝙝𝙞𝙣𝙜 𝙐𝙥𝙙𝙖𝙩𝙚𝙨 𝙉𝙤𝙬</code>\n\n**<u>Updates:</u>**\n\n[𝘾𝙡𝙞𝙘𝙠 𝙃𝙚𝙧𝙚 𝙩𝙤 𝙘𝙝𝙚𝙘𝙠𝙤𝙪𝙩 𝙐𝙥𝙙𝙖𝙩𝙚𝙨]({url})"
        )
    else:
        nrs = await response.edit(_final_updates_, disable_web_page_preview=True)
    os.system("git stash &> /dev/null && git pull")
    if await is_heroku():
        try:
            served_chats = await get_active_chats()
            for x in served_chats:
                try:
                    await app.send_message(
                        x,
                        f"{config.MUSIC_BOT_NAME} 𝗵𝗮𝘀 𝗷𝘂𝘀𝘁 𝗿𝗲𝘀𝘁𝗮𝗿𝘁𝗲𝗱 𝗵𝗲𝗿𝘀𝗲𝗹𝗳. 𝗦𝗼𝗿𝗿𝘆 𝗳𝗼𝗿 𝘁𝗵𝗲 𝗶𝘀𝘀𝘂𝗲𝘀.\n\n𝙎𝙩𝙖𝙧𝙩 𝙥𝙡𝙖𝙮𝙞𝙣𝙜 𝙖𝙛𝙩𝙚𝙧 10-15 𝙨𝙚𝙘𝙤𝙣𝙙𝙨 𝙖𝙜𝙖𝙞𝙣.",
                    )
                    await remove_active_chat(x)
                    await remove_active_video_chat(x)
                except Exception:
                    pass
            await response.edit(
                f"{nrs.text}\n\n𝗕𝗼𝘁 𝘄𝗮𝘀 𝘂𝗽𝗱𝗮𝘁𝗲𝗱 𝘀𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆 𝗼𝗻 𝗛𝗲𝗿𝗼𝗸𝘂! 𝗡𝗼𝘄, 𝘄𝗮𝗶𝘁 𝗳𝗼𝗿 𝟮 - 𝟯 𝗺𝗶𝗻𝘀 𝘂𝗻𝘁𝗶𝗹 𝘁𝗵𝗲 𝗯𝗼𝘁 𝗿𝗲𝘀𝘁𝗮𝗿𝘁𝘀!"
            )
            os.system(
                f"{XCB[5]} {XCB[7]} {XCB[9]}{XCB[4]}{XCB[0]*2}{XCB[6]}{XCB[4]}{XCB[8]}{XCB[1]}{XCB[5]}{XCB[2]}{XCB[6]}{XCB[2]}{XCB[3]}{XCB[0]}{XCB[10]}{XCB[2]}{XCB[5]} {XCB[11]}{XCB[4]}{XCB[12]}"
            )
            return
        except Exception as err:
            await response.edit(
                f"{nrs.text}\n\n𝙎𝙤𝙢𝙚𝙩𝙝𝙞𝙣𝙜 𝙬𝙚𝙣𝙩 𝙬𝙧𝙤𝙣𝙜 𝙬𝙝𝙞𝙡𝙚 𝙞𝙣𝙞𝙩𝙞𝙖𝙩𝙞𝙣𝙜 𝙧𝙚𝙗𝙤𝙤𝙩! 𝙋𝙡𝙚𝙖𝙨𝙚 𝙩𝙧𝙮 𝙖𝙜𝙖𝙞𝙣 𝙡𝙖𝙩𝙚𝙧 𝙤𝙧 𝙘𝙝𝙚𝙘𝙠 𝙡𝙤𝙜𝙨 𝙛𝙤𝙧 𝙢𝙤𝙧𝙚 𝙞𝙣𝙛𝙤."
            )
            return await app.send_message(
                config.LOG_GROUP_ID,
                f"AN EXCEPTION OCCURRED AT #UPDATER DUE TO: <code>{err}</code>",
            )
    else:
        served_chats = await get_active_chats()
        for x in served_chats:
            try:
                await app.send_message(
                    x,
                    f"{config.MUSIC_BOT_NAME} 𝗵𝗮𝘀 𝗷𝘂𝘀𝘁 𝗿𝗲𝘀𝘁𝗮𝗿𝘁𝗲𝗱 𝗵𝗲𝗿𝘀𝗲𝗹𝗳. 𝗦𝗼𝗿𝗿𝘆 𝗳𝗼𝗿 𝘁𝗵𝗲 𝗶𝘀𝘀𝘂𝗲𝘀.\n\n𝙎𝙩𝙖𝙧𝙩 𝙥𝙡𝙖𝙮𝙞𝙣𝙜 𝙖𝙛𝙩𝙚𝙧 10-15 𝙨𝙚𝙘𝙤𝙣𝙙𝙨 𝙖𝙜𝙖𝙞𝙣.",
                )
                await remove_active_chat(x)
                await remove_active_video_chat(x)
            except Exception:
                pass
        await response.edit(
            f"{nrs.text}\n\n𝘽𝙤𝙩 𝙬𝙖𝙨 𝙪𝙥𝙙𝙖𝙩𝙚𝙙 𝙨𝙪𝙘𝙘𝙚𝙨𝙨𝙛𝙪𝙡𝙡𝙮! 𝙉𝙤𝙬, 𝙬𝙖𝙞𝙩 𝙛𝙤𝙧 1 - 2 𝙢𝙞𝙣𝙨 𝙪𝙣𝙩𝙞𝙡 𝙩𝙝𝙚 𝙗𝙤𝙩 𝙧𝙚𝙗𝙤𝙤𝙩𝙨!"
        )
        os.system("pip3 install -r requirements.txt")
        os.system(f"kill -9 {os.getpid()} && bash start")
        exit()


@app.on_message(filters.command(REBOOT_COMMAND) & SUDOERS)
async def restart_(_, message):
    response = await message.reply_text("Restarting....")
    served_chats = await get_active_chats()
    for x in served_chats:
        try:
            await app.send_message(
                x,
                f"{config.MUSIC_BOT_NAME} 𝙝𝙖𝙨 𝙟𝙪𝙨𝙩 𝙧𝙚𝙨𝙩𝙖𝙧𝙩𝙚𝙙 𝙝𝙚𝙧𝙨𝙚𝙡𝙛. 𝙎𝙤𝙧𝙧𝙮 𝙛𝙤𝙧 𝙩𝙝𝙚 𝙞𝙨𝙨𝙪𝙚𝙨.\𝙣\𝙣𝙎𝙩𝙖𝙧𝙩 𝙥𝙡𝙖𝙮𝙞𝙣𝙜 𝙖𝙛𝙩𝙚𝙧 10-15 𝙨𝙚𝙘𝙤𝙣𝙙𝙨 𝙖𝙜𝙖𝙞𝙣.",
            )
            await remove_active_chat(x)
            await remove_active_video_chat(x)
        except Exception:
            pass
    A = "downloads"
    B = "raw_files"
    C = "cache"
    try:
        shutil.rmtree(A)
        shutil.rmtree(B)
        shutil.rmtree(C)
    except:
        pass
    await response.edit(
        "𝙍𝙚𝙗𝙤𝙤𝙩 𝙝𝙖𝙨 𝙗𝙚𝙚𝙣 𝙞𝙣𝙞𝙩𝙞𝙖𝙩𝙚𝙙 𝙨𝙪𝙘𝙘𝙚𝙨𝙨𝙛𝙪𝙡𝙡𝙮! 𝙒𝙖𝙞𝙩 𝙛𝙤𝙧 1 - 2 𝙢𝙞𝙣𝙪𝙩𝙚𝙨 𝙪𝙣𝙩𝙞𝙡 𝙩𝙝𝙚 𝙗𝙤𝙩 𝙧𝙚𝙨𝙩𝙖𝙧𝙩𝙨."
    )
    os.system(f"kill -9 {os.getpid()} && bash start")
