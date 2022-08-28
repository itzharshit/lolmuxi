#
# Copyright (C) 2021-2022 by TeamYukki@Github, < https://github.com/TeamYukki >.
#
# This file is part of < https://github.com/TeamYukki/YukkiMusicBot > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/TeamYukki/YukkiMusicBot/blob/master/LICENSE >
#
# All rights reserved.

from pyrogram import filters

import config
from strings import get_command
from YukkiMusic import app
from YukkiMusic.misc import SUDOERS
from YukkiMusic.utils.database import autoend_off, autoend_on
from YukkiMusic.utils.decorators.language import language

# Commands
AUTOEND_COMMAND = get_command("AUTOEND_COMMAND")


@app.on_message(filters.command(AUTOEND_COMMAND) & SUDOERS)
async def auto_end_stream(client, message):
    usage = "**Usage:**\n\n/autoend [enable|disable]"
    if len(message.command) != 2:
        return await message.reply_text(usage)
    state = message.text.split(None, 1)[1].strip()
    state = state.lower()
    if state == "enable":
        await autoend_on()
        await message.reply_text(
            "𝘼𝙪𝙩𝙤 𝙀𝙣𝙙 𝙎𝙩𝙧𝙚𝙖𝙢 𝙀𝙣𝙖𝙗𝙡𝙚𝙙.\n\n𝘽𝙤𝙩 𝙬𝙞𝙡𝙡 𝙡𝙚𝙖𝙫𝙚 𝙫𝙤𝙞𝙘𝙚 𝙘𝙝𝙖𝙩 𝙖𝙪𝙩𝙤𝙢𝙖𝙩𝙞𝙘𝙖𝙡𝙡𝙮 𝙖𝙛𝙩𝙚𝙧 3 𝙢𝙞𝙣𝙨 𝙞𝙛 𝙣𝙤 𝙤𝙣𝙚 𝙞𝙨 𝙡𝙞𝙨𝙩𝙚𝙣𝙞𝙣𝙜 𝙬𝙞𝙩𝙝 𝙖 𝙬𝙖𝙧𝙣𝙞𝙣𝙜 𝙢𝙚𝙨𝙨𝙖𝙜𝙚.."
        )
    elif state == "disable":
        await autoend_off()
        await message.reply_text("𝘼𝙪𝙩𝙤 𝙀𝙣𝙙 𝙎𝙩𝙧𝙚𝙖𝙢 𝘿𝙞𝙨𝙖𝙗𝙡𝙚𝙙.")
    else:
        await message.reply_text(usage)
