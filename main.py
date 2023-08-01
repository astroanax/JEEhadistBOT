from telebot.async_telebot import AsyncTeleBot
from ypt import get_data
from eprint import eprint
import server
from updates import jee_reminder
import prettytable as pt
import base64
import pytz
import asyncio
import datetime
import json
import os
import sys
import db

TOKEN = os.environ["TOKEN"]
# chat ids
CHAT_ID = -1001845692082
PL_TID = 8336
OF_TID = 3471
NTC_ID = 11695
ADMIN_ID = 1761484268
LOG_CHAT_ID = -1001765656153

# slowdown vars
SLOWDOWN = False
UPDATE_SLOWDOWN = False
INTERVAL = 30
data = {}
data["pl_data"] = {}
data["sl_data"] = {}

ypt_cache = [None, None]
remind_jee_users = [5624616056, 6165497652]  # Devansh @devansh1261  # $....

bot = AsyncTeleBot(TOKEN)


@bot.message_handler(
    func=lambda message: True,
    content_types=[
        "audio",
        "photo",
        "voice",
        "video",
        "document",
        "text",
        "location",
        "contact",
        "sticker",
    ],
)
async def main_process(message):
    eprint(
        "message received, thread id",
        message.message_thread_id,
        " from user ",
        message.from_user.id,
        " to chat ",
        message.chat.id,
    )
    if (
        message.chat.id == LOG_CHAT_ID
        and message.text is not None
        and message.message_thread_id is not None
    ):
        user_id = await db.get_userid(message.message_thread_id)
        await bot.send_message(chat_id=user_id, text=message.text)
    if message.chat.id == message.from_user.id and message.text is not None:
        try:
            tid = await db.get_thread_id(message.from_user)
            try:
                sent = await bot.send_message(
                    chat_id=LOG_CHAT_ID, message_thread_id=tid, text=message.text
                )
            except Exception as e:
                tid = await db.create_topic_log(message.from_user)
                sent = await bot.send_message(
                    chat_id=LOG_CHAT_ID, message_thread_id=tid, text=message.text
                )
        except Exception as e:
            eprint(e)
    if message.chat.id == ADMIN_ID and message.text == "/jeereminder":
        try:
            await send_jee_reminder(cid=ADMIN_ID)
        except Exception as e:
            await bot.reply_to(message, "unknown error!")
            eprint(e)
    elif message.chat.id == ADMIN_ID and message.text == "/id":
        try:
            user_id = message.reply_to_message.forward_from.id
            await bot.reply_to(message, str(user_id))
        except Exception as e:
            await bot.reply_to(message, "unknown error!")
            eprint(e)
    if (
        (
            (
                message.chat.id == CHAT_ID
                and (
                    message.message_thread_id == None
                    or message.message_thread_id == OF_TID
                )
            )
            or message.chat.id == message.from_user.id
        )
        and message.text is not None
        and message.text.strip().startswith("/b64decode")
    ):
        payload = message.text.strip().split()[1]
        reply = base64.b64decode(payload)
        await bot.reply_to(message, reply.decode("utf-8"))
    elif message.chat.id == ADMIN_ID and message.text is not None:
        if message.text.startswith("/sendmsg "):
            try:
                to = message.text.split()[1]
                if not to.startswith("@"):
                    to = int(to)
                msg = ""
                for i in message.text.split()[2:]:
                    msg += i + " "
                await bot.send_message(text=msg, chat_id=to)
                to_chat = await bot.get_chat(to)
                if to_chat.username is None:
                    name = to_chat.title
                else:
                    name = to_chat.username
                await bot.reply_to(message, "message sent to " + name)
            except Exception as e:
                eprint(e)
                await bot.reply_to(message, "unknown error!")
        elif message.text.startswith("/getchatid "):
            try:
                target = message.text.split()[1]
                if not target.startswith("@"):
                    raise Exception("not a username")
                target_chat = await bot.get_chat(target)
                await bot.reply_to(message, target_chat.id)
            except Exception as e:
                eprint(e)
                await bot.reply_to(message, "unknown error!")

    if (
        (
            (
                message.chat.id == CHAT_ID
                and (
                    message.message_thread_id is None
                    or message.message_thread_id == OF_TID
                )
            )
            or message.chat.id == ADMIN_ID
        )
        and message.text is not None
        and message.text == "/show ypt-lb"
    ):
        global ypt_timeout
        if ypt_cache[0] is None or datetime.datetime.today() - ypt_cache[
            0
        ] > datetime.timedelta(0, 10, 0):
            try:
                ypt_data = get_data()
                table = pt.PrettyTable(["Name", "Time"])
                table.align["Name"] = "l"
                response = "    ⚡ YPT Leaderboard 🔥\n\n"
                for key in ypt_data:
                    if ypt_data[key] > datetime.timedelta(hours=10):
                        table.add_row([key + "⚡🔥", ypt_data[key]])
                    elif ypt_data[key] > datetime.timedelta(hours=7):
                        table.add_row([key + "⚡", ypt_data[key]])
                    elif ypt_data[key] > datetime.timedelta(hours=3):
                        table.add_row([key + "🔥", ypt_data[key]])
                    else:
                        table.add_row([key, ypt_data[key]])
                response += "<pre>" + str(table) + "</pre>"
                ypt_cache[0] = datetime.datetime.today()
                ypt_cache[1] = response
                await bot.reply_to(message, response, parse_mode="html")
            except Exception as e:
                eprint(e)
                await bot.reply_to(message, "unknown error!")
        else:
            try:
                await bot.reply_to(message, ypt_cache[1], parse_mode="html")
            except Exception as e:
                eprint(e)
                await bot.reply_to(message, "unknown error!")
    elif message.message_thread_id == PL_TID:
        eprint("message receieved from ", message.from_user.id)
        pl_data = data["pl_data"]
        try:
            old_date = datetime.datetime.fromtimestamp(
                pl_data[str(message.from_user.id)] + (23 * 59 * 59)
            ).date()
            new_date = datetime.datetime.fromtimestamp(message.date).date()
            if new_date < old_date:
                eprint("deleting message")
                reply = await bot.reply_to(
                    message,
                    "You have already set a target for today; edit your current target to change it",
                )
                await asyncio.sleep(5)
                await bot.delete_message(
                    chat_id=message.chat.id, message_id=message.message_id
                )
                await bot.delete_message(
                    chat_id=reply.chat.id, message_id=reply.message_id
                )
            else:
                pl_data[str(message.from_user.id)] = message.date
                data["pl_data"] = pl_data
        except KeyError:
            pl_data[str(message.from_user.id)] = message.date
            data["pl_data"] = pl_data

    elif message.message_thread_id == OF_TID:
        sl_data = data["sl_data"]
        time = datetime.datetime.fromtimestamp(message.date).time()
        global SLOWDOWN
        global UPDATE_SLOWDOWN
        global INTERVAL
        if SLOWDOWN and message.from_user.id != ADMIN_ID:
            try:
                if message.date < sl_data[message.from_user.id] + (60 * INTERVAL):
                    await bot.delete_message(
                        chat_id=message.chat.id, message_id=message.message_id
                    )
                else:
                    sl_data[message.from_user.id] = message.date
                    data["sl_data"] = sl_data
            except KeyError:
                sl_data[message.from_user.id] = message.date
                data["sl_data"] = sl_data
        elif message.from_user.id == ADMIN_ID and message.text is not None:
            if message.text == "enable slowdown":
                SLOWDOWN = True
                await bot.send_message(
                    text="❄SLOWDOWN❄ enabled",
                    message_thread_id=OF_TID,
                    chat_id=message.chat.id,
                )
            elif message.text == "disable slowdown":
                SLOWDOWN = False
                await bot.send_message(
                    text="❄SLOWDOWN❄ disabled",
                    message_thread_id=OF_TID,
                    chat_id=message.chat.id,
                )
            elif message.text == "enable slowdown-update":
                UPDATE_SLOWDOWN = True
                await bot.send_message(
                    text="❄SLOWDOWN❄ update enabled",
                    message_thread_id=OF_TID,
                    chat_id=message.chat.id,
                )
            elif message.text == "disable slowdown-update":
                UPDATE_SLOWDOWN = False
                await bot.send_message(
                    text="❄SLOWDOWN❄ update disabled",
                    message_thread_id=OF_TID,
                    chat_id=message.chat.id,
                )
            elif "set slow-interval" == message.text[:17]:
                try:
                    global interval
                    INTERVAL = int(message.text.split()[2])
                    await bot.send_message(
                        text="slow-interval set to " + str(INTERVAL),
                        message_thread_id=OF_TID,
                        chat_id=message.chat.id,
                    )
                except:
                    pass
            elif message.text == "show slow-interval":
                await bot.send_message(
                    text="slow-interval set to " + str(INTERVAL),
                    message_thread_id=OF_TID,
                    chat_id=message.chat.id,
                )


async def update_slowdown():
    global SLOWDOWN
    while True:
        t = datetime.datetime.now(pytz.timezone("Asia/Kolkata")).time()
        if UPDATE_SLOWDOWN:
            if t > datetime.time(9, 00, 0) and t < datetime.time(5, 30, 0):
                if not SLOWDOWN:
                    SLOWDOWN = True
                    eprint("slowdown enabled")
                    await bot.send_message(
                        text="❄SLOWDOWN❄ enabled",
                        message_thread_id=OF_TID,
                        chat_id=CHAT_ID,
                    )
            elif SLOWDOWN:
                SLOWDOWN = False
                eprint("slowdown disabled")
                await bot.send_message(
                    text="❄SLOWDOWN❄ disabled",
                    message_thread_id=OF_TID,
                    chat_id=CHAT_ID,
                )
        await asyncio.sleep(10 * 60)


async def send_jee_reminder(cid, tid=None):
    jee_main, jee_adv, quote = jee_reminder()
    message = "*⏰ DAILY REMINDER*\n\n"
    message += "⏳" + str(jee_main) + " days left for JEE Main\n"
    message += "⏳" + str(jee_adv) + " days left for JEE Advanced\n\n"
    message += "_”" + quote.split("\n")[0] + "_”\n"
    message += "‎     ~ " + quote.split("\n")[1]
    await bot.send_message(
        text=message, chat_id=cid, message_thread_id=tid, parse_mode="markdown"
    )


async def main():
    asyncio.create_task(update_slowdown())
    asyncio.create_task(server.run())
    await bot.polling()


if __name__ == "__main__":
    asyncio.run(main())
