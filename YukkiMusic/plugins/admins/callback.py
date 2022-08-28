import asyncio
import random

from pykeyboard import InlineKeyboard
from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from config import (AUTO_DOWNLOADS_CLEAR, BANNED_USERS, SOUNCLOUD_IMG_URL, STREAM_IMG_URL,
                    TELEGRAM_AUDIO_URL, TELEGRAM_VIDEO_URL, adminlist, confirmer,
                    votemode)
from strings import get_string
from YukkiMusic import YouTube, app
from YukkiMusic.core.call import Yukki
from YukkiMusic.misc import SUDOERS, db
from YukkiMusic.utils.database import (get_active_chats, get_lang, is_active_chat,
                                       is_music_playing, is_muted, is_nonadmin_chat,
                                       music_off, music_on, mute_off, mute_on, set_loop)
from YukkiMusic.utils.database.memorydatabase import get_upvote_count
from YukkiMusic.utils.decorators.language import languageCB
from YukkiMusic.utils.formatters import seconds_to_min
from YukkiMusic.utils.inline.play import (panel_markup_1, panel_markup_2, panel_markup_3,
                                          panel_markup_4, panel_markup_5, stream_markup,
                                          stream_markup_timer, telegram_markup,
                                          telegram_markup_timer)
from YukkiMusic.utils.stream.autoclear import auto_clean
from YukkiMusic.utils.thumbnails import gen_thumb

checker = {}
main = {}
upvoters = {}


@app.on_callback_query(filters.regex("PanelMarkup") & ~BANNED_USERS)
@app.on_callback_query(filters.regex("SpeedAdmin") & ~BANNED_USERS)
@app.on_callback_query(filters.regex("SeekAdmin") & ~BANNED_USERS)
@app.on_callback_query(filters.regex("LetsGoBACK") & ~BANNED_USERS)
@languageCB
async def markup_panel(client, CallbackQuery: CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    videoid, chat_id = callback_request.split("|")
    chat_id = CallbackQuery.message.chat.id
    if "PanelMarkup" in CallbackQuery.data:
        buttons = panel_markup_1(_, videoid, chat_id)
    elif "SeekAdmin" in CallbackQuery.data:
        buttons = panel_markup_4(_, videoid, chat_id)
    elif "LetsGoBACK" in CallbackQuery.data:
        buttons = panel_markup_3(_, videoid, chat_id)
    else:
        buttons = panel_markup_5(_, videoid, chat_id)
    try:
        await CallbackQuery.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except:
        return
    if chat_id not in checker:
        checker[chat_id] = {}
    checker[chat_id][CallbackQuery.message.message_id] = False


@app.on_callback_query(filters.regex("MainMarkup") & ~BANNED_USERS)
@languageCB
async def del_back_playlist(client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    videoid, chat_id = callback_request.split("|")
    if videoid == str(None):
        buttons = telegram_markup(_, chat_id)
    else:
        buttons = stream_markup(_, videoid, chat_id)
    chat_id = CallbackQuery.message.chat.id
    try:
        await CallbackQuery.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except:
        return
    if chat_id not in checker:
        checker[chat_id] = {}
    checker[chat_id][CallbackQuery.message.message_id] = True


@app.on_callback_query(filters.regex("Pages") & ~BANNED_USERS)
@languageCB
async def del_back_playlist(client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    state, pages, videoid, chat = callback_request.split("|")
    chat_id = int(chat)
    pages = int(pages)
    if state == "Forw":
        if pages == 0:
            buttons = panel_markup_2(_, videoid, chat_id)
        if pages == 2:
            buttons = panel_markup_1(_, videoid, chat_id)
        if pages == 1:
            buttons = panel_markup_3(_, videoid, chat_id)
    if state == "Back":
        if pages == 2:
            buttons = panel_markup_2(_, videoid, chat_id)
        if pages == 1:
            buttons = panel_markup_1(_, videoid, chat_id)
        if pages == 0:
            buttons = panel_markup_3(_, videoid, chat_id)
    try:
        await CallbackQuery.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except:
        return


downvote = {}
downvoters = {}


@app.on_callback_query(filters.regex("ADMIN") & ~BANNED_USERS)
@languageCB
async def del_back_playlist(client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    command, chat = callback_request.split("|")
    if "_" in str(chat):
        bet = chat.split("_")
        chat = bet[0]
        counter = bet[1]
    chat_id = int(chat)
    if not await is_active_chat(chat_id):
        return await CallbackQuery.answer(_["general_6"], show_alert=True)
    mention = CallbackQuery.from_user.mention
    if command == "UpVote":
        if chat_id not in votemode:
            votemode[chat_id] = {}
        if chat_id not in upvoters:
            upvoters[chat_id] = {}

        voters = (upvoters[chat_id]).get(CallbackQuery.message.message_id)
        if not voters:
            upvoters[chat_id][CallbackQuery.message.message_id] = []

        vote = (votemode[chat_id]).get(CallbackQuery.message.message_id)
        if not vote:
            votemode[chat_id][CallbackQuery.message.message_id] = 0

        if (
            CallbackQuery.from_user.id
            in upvoters[chat_id][CallbackQuery.message.message_id]
        ):
            (upvoters[chat_id][CallbackQuery.message.message_id]).remove(
                CallbackQuery.from_user.id
            )
            votemode[chat_id][CallbackQuery.message.message_id] -= 1
        else:
            (upvoters[chat_id][CallbackQuery.message.message_id]).append(
                CallbackQuery.from_user.id
            )
            votemode[chat_id][CallbackQuery.message.message_id] += 1
        upvote = await get_upvote_count(chat_id)
        get_upvotes = int(votemode[chat_id][CallbackQuery.message.message_id])
        if get_upvotes >= upvote:
            votemode[chat_id][CallbackQuery.message.message_id] = upvote
            try:
                exists = confirmer[chat_id][CallbackQuery.message.message_id]
                current = db[chat_id][0]
            except:
                return await CallbackQuery.edit_message_text(f"Failed to perform action.")
            try:
                if current["vidid"] != exists["vidid"]:
                    return await CallbackQuery.edit_message.text(
                        "𝙎𝙤𝙧𝙧𝙮, 𝘽𝙪𝙩 𝙩𝙝𝙞𝙨 𝙫𝙤𝙩𝙞𝙣𝙜 𝙝𝙖𝙨 𝙚𝙣𝙙𝙚𝙙 𝙖𝙨 𝙩𝙧𝙖𝙘𝙠 𝙛𝙤𝙧 𝙬𝙝𝙞𝙘𝙝 𝙫𝙤𝙞𝙣𝙜 𝙬𝙖𝙨 𝙜𝙤𝙞𝙣𝙜 𝙤𝙣 𝙞𝙨 𝙛𝙞𝙣𝙞𝙨𝙝𝙚𝙙."
                    )
                if current["file"] != exists["file"]:
                    return await CallbackQuery.edit_message.text(
                        "𝙎𝙤𝙧𝙧𝙮, 𝘽𝙪𝙩 𝙩𝙝𝙞𝙨 𝙫𝙤𝙩𝙞𝙣𝙜 𝙝𝙖𝙨 𝙚𝙣𝙙𝙚𝙙 𝙖𝙨 𝙩𝙧𝙖𝙘𝙠 𝙛𝙤𝙧 𝙬𝙝𝙞𝙘𝙝 𝙫𝙤𝙩𝙞𝙣𝙜 𝙬𝙖𝙨 𝙜𝙤𝙞𝙣𝙜 𝙤𝙣 𝙞𝙨 𝙛𝙞𝙣𝙞𝙨𝙝𝙚𝙙."
                    )
            except:
                return await CallbackQuery.edit_message_text(
                    f"𝙁𝙖𝙞𝙡𝙚𝙙 𝙩𝙤 𝙥𝙚𝙧𝙛𝙤𝙧𝙢 𝙖𝙘𝙩𝙞𝙤𝙣 𝙖𝙨 𝙢𝙪𝙨𝙞𝙘 𝙛𝙤𝙧 𝙬𝙝𝙞𝙘𝙝 𝙫𝙤𝙩𝙞𝙣𝙜 𝙬𝙖𝙨 𝙝𝙖𝙥𝙥𝙚𝙣𝙞𝙣𝙜 𝙞𝙨 𝙚𝙞𝙩𝙝𝙚𝙧 𝙛𝙞𝙣𝙞𝙨𝙝𝙚𝙙 𝙤𝙧 𝙨𝙩𝙤𝙥𝙥𝙚𝙙."
                )
            try:
                await CallbackQuery.edit_message_text(
                    f"𝙂𝙤𝙩 **{upvote}**𝙐𝙥𝙫𝙤𝙩𝙚𝙨 𝙨𝙪𝙘𝙘𝙚𝙨𝙨𝙛𝙪𝙡𝙡𝙮."
                )
            except:
                pass
            command = counter
            mention = "**𝙐𝙥𝙫𝙤𝙩𝙚𝙨**"
        else:
            if (
                CallbackQuery.from_user.id
                in upvoters[chat_id][CallbackQuery.message.message_id]
            ):
                await CallbackQuery.answer("Added Upvote.", show_alert=True)
            else:
                await CallbackQuery.answer("Removed Upvote.", show_alert=True)
            upl = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text=f"👍 {get_upvotes}",
                            callback_data=f"ADMIN  UpVote|{chat_id}_{counter}",
                        )
                    ]
                ]
            )
            await CallbackQuery.answer("Upvoted", show_alert=True)
            return await CallbackQuery.edit_message_reply_markup(reply_markup=upl)
    else:
        is_non_admin = await is_nonadmin_chat(CallbackQuery.message.chat.id)
        if not is_non_admin:
            if CallbackQuery.from_user.id not in SUDOERS:
                admins = adminlist.get(CallbackQuery.message.chat.id)
                if not admins:
                    return await CallbackQuery.answer(_["admin_18"], show_alert=True)
                else:
                    if CallbackQuery.from_user.id not in admins:
                        return await CallbackQuery.answer(_["admin_19"], show_alert=True)
    if command == "Pause":
        if not await is_music_playing(chat_id):
            return await CallbackQuery.answer(_["admin_1"], show_alert=True)
        await CallbackQuery.answer()
        await music_off(chat_id)
        await Yukki.pause_stream(chat_id)
        await CallbackQuery.message.reply_text(_["admin_2"].format(mention))
    elif command == "Resume":
        if await is_music_playing(chat_id):
            return await CallbackQuery.answer(_["admin_3"], show_alert=True)
        await CallbackQuery.answer()
        await music_on(chat_id)
        await Yukki.resume_stream(chat_id)
        await CallbackQuery.message.reply_text(_["admin_4"].format(mention))
    elif command == "Stop" or command == "End":
        await CallbackQuery.answer()
        await Yukki.stop_stream(chat_id)
        await set_loop(chat_id, 0)
        await CallbackQuery.message.reply_text(_["admin_9"].format(mention))
    elif command == "Mute":
        if await is_muted(chat_id):
            return await CallbackQuery.answer(_["admin_5"], show_alert=True)
        await CallbackQuery.answer()
        await mute_on(chat_id)
        await Yukki.mute_stream(chat_id)
        await CallbackQuery.message.reply_text(_["admin_6"].format(mention))
    elif command == "Unmute":
        if not await is_muted(chat_id):
            return await CallbackQuery.answer(_["admin_7"], show_alert=True)
        await CallbackQuery.answer()
        await mute_off(chat_id)
        await Yukki.unmute_stream(chat_id)
        await CallbackQuery.message.reply_text(_["admin_8"].format(mention))
    elif command == "Loop":
        await CallbackQuery.answer()
        await set_loop(chat_id, 3)
        await CallbackQuery.message.reply_text(_["admin_25"].format(mention, 3))
    elif command == "Shuffle":
        check = db.get(chat_id)
        if not check:
            return await CallbackQuery.answer(_["admin_21"], show_alert=True)
        total = len(check)
        if total <= 2:
            return await CallbackQuery.answer(
                f"𝘼𝙩𝙡𝙚𝙖𝙨𝙩 2 𝙩𝙧𝙖𝙘𝙠𝙨 𝙣𝙚𝙚𝙙𝙚𝙙 𝙞𝙣 𝙦𝙪𝙚𝙪𝙚 𝙩𝙤 𝙨𝙝𝙪𝙛𝙛𝙡𝙚 𝙗𝙚𝙩𝙬𝙚𝙚𝙣 𝙩𝙝𝙚𝙢.\n\n{total - 1} 𝙩𝙧𝙖𝙘𝙠 𝙥𝙧𝙚𝙨𝙚𝙣𝙩.",
                show_alert=True,
            )
        try:
            popped = check.pop(0)
        except:
            return await CallbackQuery.answer(_["admin_22"], show_alert=True)
        check = db.get(chat_id)
        if not check:
            check.insert(0, popped)
            return await CallbackQuery.answer(_["admin_22"], show_alert=True)
        await CallbackQuery.answer()
        random.shuffle(check)
        check.insert(0, popped)
        await CallbackQuery.message.reply_text(_["admin_23"].format(mention))
    elif command == "Skip" or command == "Replay" or command == "Jump":
        check = db.get(chat_id)
        if command == "Skip":
            txt = f"Skipped by {mention}"
            popped = None
            try:
                popped = check.pop(0)
                if popped:
                    if AUTO_DOWNLOADS_CLEAR == str(True):
                        await auto_clean(popped)
                if not check:
                    await CallbackQuery.edit_message_text(f"Skipped by {mention}")
                    await CallbackQuery.message.reply_text(_["admin_10"].format(mention))
                    try:
                        return await Yukki.stop_stream(chat_id)
                    except:
                        return
            except:
                try:
                    await CallbackQuery.edit_message_text(f"Skipped by {mention}")
                    await CallbackQuery.message.reply_text(_["admin_10"].format(mention))
                    return await Yukki.stop_stream(chat_id)
                except:
                    return
        elif command == "Jump":
            txt = f"Jumped to specific track by {mention}"
            try:
                check.pop(0)
                if not check:
                    return await CallbackQuery.answer("Failed to Jump", show_alert=True)
            except:
                return await CallbackQuery.answer("Failed to Jump", show_alert=True)
            try:
                counter = int(int(counter) - 1)
                popped = check.pop(counter)
                if not popped:
                    return await CallbackQuery.answer("Failed to Jump", show_alert=True)
                check.insert(0, popped)
            except:
                return await CallbackQuery.answer("Failed to Jump", show_alert=True)
        else:
            txt = f"Replayed by {mention}"
        await CallbackQuery.answer()
        queued = check[0]["file"]
        title = (check[0]["title"]).title()
        user = check[0]["by"]
        streamtype = check[0]["streamtype"]
        videoid = check[0]["vidid"]
        status = True if str(streamtype) == "video" else None
        db[chat_id][0]["played"] = 0
        exis = (check[0]).get("old_dur")
        if exis:
            db[chat_id][0]["dur"] = exis
            db[chat_id][0]["seconds"] = check[0]["old_second"]
            db[chat_id][0]["speed_path"] = None
            db[chat_id][0]["speed"] = 1.0
        if "live_" in queued:
            n, link = await YouTube.video(videoid, True)
            if n == 0:
                return await CallbackQuery.message.reply_text(_["admin_11"].format(title))
            try:
                image = await YouTube.thumbnail(videoid, True)
            except:
                image = None
            try:
                await Yukki.skip_stream(chat_id, link, video=status, image=image)
            except Exception:
                return await CallbackQuery.message.reply_text(_["call_9"])
            button = telegram_markup(_, chat_id)
            img = await gen_thumb(videoid)
            run = await CallbackQuery.message.reply_photo(
                photo=img,
                caption=_["stream_1"].format(
                    user,
                    f"https://t.me/{app.username}?start=info_{videoid}",
                ),
                reply_markup=InlineKeyboardMarkup(button),
            )
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "tg"
            await CallbackQuery.edit_message_text(txt)
        elif "vid_" in queued:
            mystic = await CallbackQuery.message.reply_text(
                _["call_10"], disable_web_page_preview=True
            )
            try:
                file_path, direct = await YouTube.download(
                    videoid,
                    mystic,
                    videoid=True,
                    video=status,
                )
            except:
                return await mystic.edit_text(_["call_9"])
            try:
                image = await YouTube.thumbnail(videoid, True)
            except:
                image = None
            try:
                await Yukki.skip_stream(chat_id, file_path, video=status, image=image)
            except Exception:
                return await mystic.edit_text(_["call_9"])
            button = stream_markup(_, videoid, chat_id)
            img = await gen_thumb(videoid)
            run = await CallbackQuery.message.reply_photo(
                photo=img,
                caption=_["stream_1"].format(
                    user,
                    f"https://t.me/{app.username}?start=info_{videoid}",
                ),
                reply_markup=InlineKeyboardMarkup(button),
            )
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "stream"
            await CallbackQuery.edit_message_text(txt)
            await mystic.delete()
        elif "index_" in queued:
            try:
                await Yukki.skip_stream(chat_id, videoid, video=status)
            except Exception:
                return await CallbackQuery.message.reply_text(_["call_9"])
            button = telegram_markup(_, chat_id)
            run = await CallbackQuery.message.reply_photo(
                photo=STREAM_IMG_URL,
                caption=_["stream_2"].format(user),
                reply_markup=InlineKeyboardMarkup(button),
            )
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "tg"
            await CallbackQuery.edit_message_text(txt)
        else:
            if videoid == "telegram":
                image = None
            elif videoid == "soundcloud":
                image = None
            else:
                try:
                    image = await YouTube.thumbnail(videoid, True)
                except:
                    image = None
            try:
                await Yukki.skip_stream(chat_id, queued, video=status, image=image)
            except Exception:
                return await CallbackQuery.message.reply_text(_["call_9"])
            if videoid == "telegram":
                button = telegram_markup(_, chat_id)
                run = await CallbackQuery.message.reply_photo(
                    photo=TELEGRAM_AUDIO_URL
                    if str(streamtype) == "audio"
                    else TELEGRAM_VIDEO_URL,
                    caption=_["stream_3"].format(title, check[0]["dur"], user),
                    reply_markup=InlineKeyboardMarkup(button),
                )
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "tg"
            elif videoid == "soundcloud":
                button = telegram_markup(_, chat_id)
                run = await CallbackQuery.message.reply_photo(
                    photo=SOUNCLOUD_IMG_URL
                    if str(streamtype) == "audio"
                    else TELEGRAM_VIDEO_URL,
                    caption=_["stream_3"].format(title, check[0]["dur"], user),
                    reply_markup=InlineKeyboardMarkup(button),
                )
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "tg"
            else:
                button = stream_markup(_, videoid, chat_id)
                img = await gen_thumb(videoid)
                run = await CallbackQuery.message.reply_photo(
                    photo=img,
                    caption=_["stream_1"].format(
                        user,
                        f"https://t.me/{app.username}?start=info_{videoid}",
                    ),
                    reply_markup=InlineKeyboardMarkup(button),
                )
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "stream"
            await CallbackQuery.edit_message_text(txt)
    else:
        playing = db.get(chat_id)
        if not playing:
            return await CallbackQuery.answer(_["queue_2"], show_alert=True)
        duration_seconds = int(playing[0]["seconds"])
        if duration_seconds == 0:
            return await CallbackQuery.answer(_["admin_30"], show_alert=True)
        file_path = playing[0]["file"]
        duration_played = int(playing[0]["played"])
        if int(command) in [1, 2]:
            duration_to_skip = 10
        else:
            duration_to_skip = 30
        duration = playing[0]["dur"]
        if int(command) in [1, 3]:
            if (duration_played - duration_to_skip) <= 10:
                bet = seconds_to_min(duration_played)
                return await CallbackQuery.answer(
                    f"𝘽𝙤𝙩 𝙞𝙨 𝙣𝙤𝙩 𝙖𝙗𝙡𝙚 𝙩𝙤 𝙨𝙚𝙚𝙠 𝙙𝙪𝙚 𝙩𝙤 𝙩𝙤𝙩𝙖𝙡 𝙙𝙪𝙧𝙖𝙩𝙞𝙤𝙣 𝙝𝙖𝙨 𝙗𝙚𝙚𝙣 𝙚𝙭𝙘𝙚𝙚𝙙𝙚𝙙.\n\n𝘾𝙪𝙧𝙧𝙚𝙣𝙩𝙡𝙮 𝙥𝙡𝙖𝙮𝙚𝙙** {bet}** 𝙢𝙞𝙣𝙨 𝙤𝙪𝙩 𝙤𝙛 **{duration}** 𝙢𝙞𝙣𝙨",
                    show_alert=True,
                )
            to_seek = duration_played - duration_to_skip + 1
        else:
            if (duration_seconds - (duration_played + duration_to_skip)) <= 10:
                bet = seconds_to_min(duration_played)
                return await CallbackQuery.answer(
                    f"𝘽𝙤𝙩 𝙞𝙨 𝙣𝙤𝙩 𝙖𝙗𝙡𝙚 𝙩𝙤 𝙨𝙚𝙚𝙠 𝙙𝙪𝙚 𝙩𝙤 𝙩𝙤𝙩𝙖𝙡 𝙙𝙪𝙧𝙖𝙩𝙞𝙤𝙣 𝙝𝙖𝙨 𝙗𝙚𝙚𝙣 𝙚𝙭𝙘𝙚𝙚𝙙𝙚𝙙.\n\n𝘾𝙪𝙧𝙧𝙚𝙣𝙩𝙡𝙮 𝙥𝙡𝙖𝙮𝙚𝙙** {bet}** 𝙢𝙞𝙣𝙨 𝙤𝙪𝙩 𝙤𝙛 **{duration}** 𝙢𝙞𝙣𝙨",
                    show_alert=True,
                )
            to_seek = duration_played + duration_to_skip + 1
        await CallbackQuery.answer()
        mystic = await CallbackQuery.message.reply_text(_["admin_32"])
        if "vid_" in file_path:
            n, file_path = await YouTube.video(playing[0]["vidid"], True)
            if n == 0:
                return await mystic.edit_text(_["admin_30"])
        check = (playing[0]).get("speed_path")
        if check:
            file_path = check
        if "index_" in file_path:
            file_path = playing[0]["vidid"]
        try:
            await Yukki.seek_stream(
                chat_id,
                file_path,
                seconds_to_min(to_seek),
                duration,
                playing[0]["streamtype"],
            )
        except:
            return await mystic.edit_text(_["admin_34"])
        if int(command) in [1, 3]:
            db[chat_id][0]["played"] -= duration_to_skip
        else:
            db[chat_id][0]["played"] += duration_to_skip
        string = _["admin_33"].format(seconds_to_min(to_seek))
        await mystic.edit_text(f"{string}\n\nChanges done by: {mention}")


@app.on_callback_query(filters.regex("JumpAdmin") & ~BANNED_USERS)
@languageCB
async def jump_panel(client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    videoid, chat_id = callback_request.split("|")
    chat_id = int(chat_id)
    check = db.get(chat_id)
    if not check:
        return await CallbackQuery.answer(_["queue_2"], show_alert=True)
    count = len(check)
    if count == 1:
        return await CallbackQuery.answer(
            "𝙉𝙤 𝙩𝙧𝙖𝙘𝙠𝙨 𝙖𝙙𝙙𝙚𝙙 𝙞𝙣 𝙦𝙪𝙚𝙪𝙚 𝙩𝙤 𝙅𝙪𝙢𝙥", show_alert=True
        )
    await CallbackQuery.answer(
        "𝘾𝙡𝙞𝙘𝙠 𝙤𝙣 𝙩𝙝𝙚 𝙏𝙞𝙩𝙡𝙚 𝙗𝙪𝙩𝙩𝙤𝙣𝙨 𝙩𝙤 𝙬𝙝𝙞𝙘𝙝 𝙮𝙤𝙪 𝙬𝙖𝙣𝙩 𝙩𝙤 𝙟𝙪𝙢𝙥.\n\n𝘽𝙤𝙩 𝙬𝙞𝙡𝙡 𝙟𝙪𝙢𝙥 𝙩𝙤 𝙩𝙝𝙖𝙩 𝙢𝙪𝙨𝙞𝙘 𝙬𝙞𝙩𝙝𝙤𝙪𝙩 𝙙𝙞𝙨𝙩𝙪𝙧𝙗𝙞𝙣𝙜 𝙦𝙪𝙚𝙪𝙚.",
        show_alert=True,
    )
    if count >= 7:
        count = 6
    keyboard = InlineKeyboard(row_width=1)
    for x in range(count):
        if x == 0:
            continue
        keyboard.row(
            InlineKeyboardButton(
                text=check[x]["title"],
                callback_data=f"ADMIN Jump|{chat_id}_{x}",
            )
        )
    count = len(check)
    if count >= 7:
        keyboard.row(
            InlineKeyboardButton(
                text="◀️",
                callback_data=f"RevengeSeeker Back|1|{videoid}|{chat_id}",
            ),
            InlineKeyboardButton(
                text="🔙 Back",
                callback_data=f"LetsGoBACK {videoid}|{chat_id}",
            ),
            InlineKeyboardButton(
                text="▶️",
                callback_data=f"RevengeSeeker Forw|1|{videoid}|{chat_id}",
            ),
        )
    else:
        keyboard.row(
            InlineKeyboardButton(
                text="🔙 Back",
                callback_data=f"LetsGoBACK {videoid}|{chat_id}",
            ),
        )

    try:
        await CallbackQuery.edit_message_reply_markup(reply_markup=keyboard)
    except:
        return


@app.on_callback_query(filters.regex("RevengeSeeker") & ~BANNED_USERS)
@languageCB
async def jump_panel(client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    mode, page, videoid, chat_id = callback_request.split("|")
    chat_id = int(chat_id)
    page = int(page)
    check = db.get(chat_id)
    if not check:
        return await CallbackQuery.answer(_["queue_2"], show_alert=True)
    count = len(check)
    trial = count - 1
    if count == 1:
        buttons = panel_markup_3(_, videoid, chat_id)
        try:
            await CallbackQuery.edit_message_reply_markup(
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        except:
            return
        return await CallbackQuery.answer(
            "No tracks added in queue to Jump", show_alert=True
        )
    table = []
    for x in range(int((trial // 5) + 1)):
        table.append(x * 5)
    if trial in table:
        poss = int(trial // 5)
    else:
        poss = int((trial // 5) + 1)
    await CallbackQuery.answer()
    if mode == "Forw":
        if poss == page:
            page = 1
        else:
            page = page + 1
    else:
        if page == 1:
            page = poss
        else:
            page = page - 1
    counter = (page * 5) - 5
    keyboard = InlineKeyboard(row_width=1)
    for x in range(5):
        counter += 1
        try:
            keyboard.row(
                InlineKeyboardButton(
                    text=check[counter]["title"],
                    callback_data=f"ADMIN Jump|{chat_id}_{counter}",
                )
            )
        except:
            pass
    keyboard.row(
        InlineKeyboardButton(
            text="◀️",
            callback_data=f"RevengeSeeker Back|{page}|{videoid}|{chat_id}",
        ),
        InlineKeyboardButton(
            text="🔙 Back",
            callback_data=f"LetsGoBACK {videoid}|{chat_id}",
        ),
        InlineKeyboardButton(
            text="▶️",
            callback_data=f"RevengeSeeker Forw|{page}|{videoid}|{chat_id}",
        ),
    )
    try:
        await CallbackQuery.edit_message_reply_markup(reply_markup=keyboard)
    except:
        return


async def markup_timer():
    while not await asyncio.sleep(4):
        active_chats = await get_active_chats()
        for chat_id in active_chats:
            try:
                if not await is_music_playing(chat_id):
                    continue
                playing = db.get(chat_id)
                if not playing:
                    continue
                duration_seconds = int(playing[0]["seconds"])
                if duration_seconds == 0:
                    continue
                try:
                    mystic = playing[0]["mystic"]
                    markup = playing[0]["markup"]
                except:
                    continue
                try:
                    check = checker[chat_id][mystic.message_id]
                    if check is False:
                        continue
                except:
                    pass
                try:
                    language = await get_lang(chat_id)
                    _ = get_string(language)
                except:
                    _ = get_string("en")
                try:
                    buttons = (
                        stream_markup_timer(
                            _,
                            playing[0]["vidid"],
                            chat_id,
                            seconds_to_min(playing[0]["played"]),
                            playing[0]["dur"],
                        )
                        if markup == "stream"
                        else telegram_markup_timer(
                            _,
                            chat_id,
                            seconds_to_min(playing[0]["played"]),
                            playing[0]["dur"],
                        )
                    )
                    await mystic.edit_reply_markup(
                        reply_markup=InlineKeyboardMarkup(buttons)
                    )
                except:
                    continue
            except:
                continue


asyncio.create_task(markup_timer())
