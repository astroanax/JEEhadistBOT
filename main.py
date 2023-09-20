from telebot.async_telebot import AsyncTeleBot
from telebot.types import InputFile
from ypt import get_data
from eprint import eprint
import server
from updates import jee_reminder
import prettytable as pt
import base64
import pytz
import asyncio
import datetime
import os
import db
import stats
import json
from helpers import resolve_username, resolve_topic
from telebot.util import user_link
from getDpp import get_dpp


TOKEN = os.environ["TG_BOT_TOKEN"]
# chat ids
CHAT_ID = -1001845692082
DT_TID = 8336
OF_TID = 3471
NTC_ID = 11695
DPP_ID = 15093
ADMIN_ID = 1761484268
LOG_CHAT_ID = -1001765656153

# slowdown vars
SLOWDOWN = False
UPDATE_SLOWDOWN = False
INTERVAL = 30
data = {}
data["pl_data"] = {}
data["sl_data"] = {}

muted = []
ypt_cache = [None, None]
remind_jee_users = [1744289341, 6165497652]  # Devansh @devansh1261  # $....

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
    if message.chat.id == CHAT_ID:
        await stats.messageq.put(message)
    if message.chat.id == CHAT_ID and message.from_user.id in muted:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.id)
    if (
        message.chat.id == CHAT_ID
        and message.text is not None
        and message.text.startswith("/mute ")
    ):
        if len(message.text.strip().split()) > 1:
            if len(message.entities) > 1:
                if message.entities[1].type == "mention":
                    username = message.text.strip().split()[1]
                    user_id = await resolve_username(username[1:])
                    muted.append(user_id)
                    bot.reply_to(message, text='muted')
                elif message.entities[1].type == "text_mention":
                    user_id = message.entities[1].user.id
                    muted.append(user_id)
                    bot.reply_to(message, text='muted')
    if (
        message.chat.id == CHAT_ID
        and message.text is not None
        and message.text.startswith("/unmute ")
    ):
        if len(message.text.strip().split()) > 1:
            if len(message.entities) > 1:
                if message.entities[1].type == "mention":
                    username = message.text.strip().split()[1]
                    user_id = await resolve_username(username[1:])
                    try:
                        muted.remove(user_id)
                        bot.reply_to(message, text='unmuted')
                    except:
                        pass
                elif message.entities[1].type == "text_mention":
                    user_id = message.entities[1].user.id
                    try:
                        muted.remove(user_id)
                        bot.reply_to(message, text='unmuted')
                    except:
                        pass
    if (
        message.chat.id == CHAT_ID
        and (message.message_thread_id == None or message.message_thread_id == OF_TID)
        and message.text is not None
        and message.text.endswith("/s")
    ):
        await bot.send_chat_action(
            chat_id=message.chat.id,
            message_thread_id=message.message_thread_id,
            action="typing",
        )
        eprint("found sarcasm!")
        await bot.reply_to(message, "🤨")
    if (
        message.chat.id == LOG_CHAT_ID
        and message.text is not None
        and message.message_thread_id is not None
    ):
        user_id = await db.get_userid(message.message_thread_id)
        await bot.send_chat_action(action="typing", chat_id=user_id)
        await bot.send_message(chat_id=user_id, text=message.text)
    if message.chat.id == message.from_user.id and message.text is not None:
        try:
            tid = await db.get_thread_id(message.from_user)
            try:
                await bot.send_chat_action(
                    action="typing", chat_id=LOG_CHAT_ID, message_thread_id=tid
                )
                await bot.send_message(
                    chat_id=LOG_CHAT_ID, message_thread_id=tid, text=message.text
                )
            except Exception as e:
                eprint(e)
                tid = await db.create_topic_log(message.from_user)
                await bot.send_chat_action(
                    action="typing", chat_id=LOG_CHAT_ID, message_thread_id=tid
                )
                await bot.send_message(
                    chat_id=LOG_CHAT_ID, message_thread_id=tid, text=message.text
                )
        except Exception as e:
            eprint(e)
    if (
        message.chat.id == ADMIN_ID
        and message.text is not None
        and message.text.startswith("/get_user_name")
    ):
        await bot.send_chat_action(
            chat_id=message.chat.id,
            message_thread_id=message.message_thread_id,
            action="typing",
        )
        user_id = int(message.text.split()[1])
        print(user_id)
        user = (await bot.get_chat_member(chat_id=user_id, user_id=user_id)).user
        await bot.reply_to(
            message, str(user.username) + str(user.first_name) + str(user.last_name)
        )
    if (
        message.chat.id == ADMIN_ID
        and message.text is not None
        and message.text == "/jeereminder"
    ):
        try:
            await send_jee_reminder(cid=ADMIN_ID)
        except Exception as e:
            await bot.send_chat_action(
                chat_id=message.chat.id,
                message_thread_id=message.message_thread_id,
                action="typing",
            )
            eprint(e)
            await bot.reply_to(message, "unknown error!")
    elif message.chat.id == ADMIN_ID and message.text == "/id":
        try:
            await bot.send_chat_action(
                chat_id=message.chat.id,
                message_thread_id=message.message_thread_id,
                action="typing",
            )
            user_id = message.reply_to_message.forward_from.id
            await bot.reply_to(message, str(user_id))
        except Exception as e:
            await bot.send_chat_action(
                chat_id=message.chat.id,
                message_thread_id=message.message_thread_id,
                action="typing",
            )
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
        await bot.send_chat_action(
            chat_id=message.chat.id,
            message_thread_id=message.message_thread_id,
            action="typing",
        )
        payload = message.text.strip().split()[1]
        reply = base64.b64decode(payload)
        await bot.reply_to(message, reply.decode("utf-8"))
    elif message.chat.id == ADMIN_ID and message.text is not None:
        if message.text.startswith("/sendmsg "):
            try:
                await bot.send_chat_action(
                    chat_id=message.chat.id,
                    message_thread_id=message.message_thread_id,
                    action="typing",
                )
                to = message.text.split()[1]
                if not to.startswith("@"):
                    to = int(to)
                await bot.send_chat_action(action="typing", chat_id=to)
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
                await bot.send_chat_action(
                    chat_id=message.chat.id,
                    message_thread_id=message.message_thread_id,
                    action="typing",
                )
                await bot.reply_to(message, "unknown error!")
        elif message.text.startswith("/getchatid "):
            try:
                await bot.send_chat_action(
                    chat_id=message.chat.id,
                    message_thread_id=message.message_thread_id,
                    action="typing",
                )
                target = message.text.split()[1]
                if not target.startswith("@"):
                    raise Exception("not a username")
                target_chat = await bot.get_chat(target)
                await bot.reply_to(message, target_chat.id)
            except Exception as e:
                await bot.send_chat_action(
                    chat_id=message.chat.id,
                    message_thread_id=message.message_thread_id,
                    action="typing",
                )
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
        and message.text.startswith("/stats")
    ):
        if len(message.text.strip().split()) > 1:
            # stats for topic or user
            if len(message.entities) > 1:
                if message.entities[1].type == "mention":
                    try:
                        await bot.send_chat_action(
                            chat_id=message.chat.id,
                            message_thread_id=message.message_thread_id,
                            action="typing",
                        )
                        username = message.text.strip().split()[1]
                        user_id = await resolve_username(username[1:])
                        if user_id is None:
                            await bot.reply_to(message, "no such user found")
                        else:
                            total_messages, top_topics = await stats.get_user_stats(
                                user_id
                            )
                            text = "📊Statistics for user " + username + "\n"
                            text += (
                                "Total messages sent by this user: "
                                + str(total_messages)
                                + "\n"
                            )
                            text += "Top topics: \n"
                            for i, [topic, count] in enumerate(top_topics):
                                text += (
                                    str(i + 1)
                                    + ". "
                                    + resolve_topic(topic)
                                    + ": "
                                    + str(count)
                                    + "\n"
                                )
                            await bot.reply_to(message, text)
                    except Exception as e:
                        await bot.send_chat_action(
                            chat_id=message.chat.id,
                            message_thread_id=message.message_thread_id,
                            action="typing",
                        )
                        eprint(e)
                        await bot.reply_to(message, "unknown error!")
                elif message.entities[1].type == "text_mention":
                    await bot.send_chat_action(
                        chat_id=message.chat.id,
                        message_thread_id=message.message_thread_id,
                        action="typing",
                    )
                    user_id = message.entities[0].user.id
                    total_messages, top_topics = await stats.get_user_stats(user_id)
                    text = (
                        "📊Statistics for user "
                        + user_link(user=message.entities[0].user)
                        + "\n"
                    )
                    text += (
                        "Total messages sent by this user: "
                        + str(total_messages)
                        + "\n"
                    )
                    text += "Top topics: \n"
                    for i, [topic, count] in enumerate(top_topics):
                        text += (
                            str(i + 1)
                            + ". "
                            + resolve_topic(topic)
                            + ": "
                            + str(count)
                            + "\n"
                        )
                    await bot.reply_to(message, text)
                else:
                    await bot.send_chat_action(
                        chat_id=message.chat.id,
                        message_thread_id=message.message_thread_id,
                        action="typing",
                    )
                    await bot.reply_to(message, "usage: /stats [USERNAME|CHANNEL]")
            else:
                # stats for topic
                topic_name = message.text.strip().split()[1].lower()
                topic = resolve_topic(topic_name)
                if isinstance(topic, list):
                    await bot.send_chat_action(
                        chat_id=message.chat.id,
                        message_thread_id=message.message_thread_id,
                        action="typing",
                    )
                    total_messages = 0
                    top_users = []
                    for t in topic:
                        messages, users = await stats.get_topic_stats(t)
                        total_messages += messages
                        for u in users:
                            top_users.append(u)
                    temp = {}
                    for i in top_users:
                        if not i[0] in temp.keys():
                            temp[i[0]] = i[1]
                        else:
                            temp[i[0]] += i[1]
                    top_users = []
                    for user in temp:
                        top_users.append([user, temp[user]])
                    text = "📈Statistics for topic " + "Doubts" + "\n"
                    text += (
                        "Total messages sent in this topic: "
                        + str(total_messages)
                        + "\n"
                    )
                    top_users.sort(key=lambda i: i[1], reverse=True)
                    top_users = top_users[:5]
                    text += "Top users: \n"
                    for i, [user, count] in enumerate(top_users):
                        text += (
                            str(i + 1)
                            + ". "
                            + user_link(
                                (
                                    await bot.get_chat_member(
                                        chat_id=CHAT_ID, user_id=user
                                    )
                                ).user
                            )
                            + ": "
                            + str(count)
                            + "\n"
                        )
                    await bot.reply_to(message, text, parse_mode="html")
                elif topic is None:
                    await bot.send_chat_action(
                        chat_id=message.chat.id,
                        message_thread_id=message.message_thread_id,
                        action="typing",
                    )
                    await bot.reply_to(
                        message,
                        "topic "
                        + topic_name
                        + " not found\n"
                        + "usage: /stats [USERNAME|CHANNEL]",
                    )
                else:
                    await bot.send_chat_action(
                        chat_id=message.chat.id,
                        message_thread_id=message.message_thread_id,
                        action="typing",
                    )
                    total_messages, top_users = await stats.get_topic_stats(topic)
                    text = "📈Statistics for topic " + topic_name + "\n"
                    text += (
                        "Total messages sent in this topic: "
                        + str(total_messages)
                        + "\n"
                    )
                    text += "Top users: \n"
                    for i, [user, count] in enumerate(top_users):
                        text += (
                            str(i + 1)
                            + ". "
                            + user_link(
                                (
                                    await bot.get_chat_member(
                                        chat_id=CHAT_ID, user_id=user
                                    )
                                ).user
                            )
                            + ": "
                            + str(count)
                            + "\n"
                        )
                    await bot.reply_to(message, text, parse_mode="html")

        else:
            # overall stats
            await bot.send_chat_action(
                chat_id=message.chat.id,
                message_thread_id=message.message_thread_id,
                action="typing",
            )
            users, topics = await stats.get_overall_stats()
            text = "--📋STATISTICS FOR 95%ilers Droppers--\n\n"
            text += "Top users:👄\n"
            for i, [user, count] in enumerate(users):
                try:
                    username = user_link(
                        (await bot.get_chat_member(chat_id=CHAT_ID, user_id=user)).user
                    )
                except Exception as e:
                    eprint(e, "unknown user", user)
                    username = "unknown user"
                text += str(i + 1) + ". " + username + ": " + str(count) + "\n"
            text += "\n"
            text += "Topic-wise statistics:💬\n"
            for i, [topic, count] in enumerate(topics):
                topic_name = resolve_topic(topic)
                if topic_name == "unknown topic":
                    continue
                text += str(i + 1) + ". " + topic_name + ": " + str(count) + "\n"
            await bot.reply_to(message, text, parse_mode="html")
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
        await bot.send_chat_action(
            chat_id=message.chat.id,
            message_thread_id=message.message_thread_id,
            action="typing",
        )
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
    elif message.message_thread_id == DT_TID:
        eprint("message receieved from ", message.from_user.id)
        pl_data = data["pl_data"]
        try:
            old_date = datetime.datetime.fromtimestamp(
                pl_data[str(message.from_user.id)] + (23 * 59 * 59)
            ).date()
            new_date = datetime.datetime.fromtimestamp(message.date).date()
            if new_date < old_date:
                eprint("deleting message")
                await bot.send_chat_action(
                    chat_id=message.chat.id,
                    message_thread_id=message.message_thread_id,
                    action="typing",
                )
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
                await bot.send_chat_action(
                    action="typing", message_thread_id=OF_TID, chat_id=message.chat.id
                )
                SLOWDOWN = True
                await bot.send_message(
                    text="❄SLOWDOWN❄ enabled",
                    message_thread_id=OF_TID,
                    chat_id=message.chat.id,
                )
            elif message.text == "disable slowdown":
                await bot.send_chat_action(
                    action="typing", message_thread_id=OF_TID, chat_id=message.chat.id
                )
                SLOWDOWN = False
                await bot.send_message(
                    text="❄SLOWDOWN❄ disabled",
                    message_thread_id=OF_TID,
                    chat_id=message.chat.id,
                )
            elif message.text == "enable slowdown-update":
                await bot.send_chat_action(
                    action="typing", message_thread_id=OF_TID, chat_id=message.chat.id
                )
                UPDATE_SLOWDOWN = True
                await bot.send_message(
                    text="❄SLOWDOWN❄ update enabled",
                    message_thread_id=OF_TID,
                    chat_id=message.chat.id,
                )
            elif message.text == "disable slowdown-update":
                await bot.send_chat_action(
                    action="typing", message_thread_id=OF_TID, chat_id=message.chat.id
                )
                UPDATE_SLOWDOWN = False
                await bot.send_message(
                    text="❄SLOWDOWN❄ update disabled",
                    message_thread_id=OF_TID,
                    chat_id=message.chat.id,
                )
            elif "set slow-interval" == message.text[:17]:
                try:
                    await bot.send_chat_action(
                        action="typing",
                        message_thread_id=OF_TID,
                        chat_id=message.chat.id,
                    )
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
                await bot.send_chat_action(
                    action="typing", message_thread_id=OF_TID, chat_id=message.chat.id
                )
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
                    await bot.send_chat_action(
                        action="typing", message_thread_id=OF_TID, chat_id=CHAT_ID
                    )
                    SLOWDOWN = True
                    eprint("slowdown enabled")
                    await bot.send_message(
                        text="❄SLOWDOWN❄ enabled",
                        message_thread_id=OF_TID,
                        chat_id=CHAT_ID,
                    )
            elif SLOWDOWN:
                await bot.send_chat_action(
                    action="typing", message_thread_id=OF_TID, chat_id=CHAT_ID
                )
                SLOWDOWN = False
                eprint("slowdown disabled")
                await bot.send_message(
                    text="❄SLOWDOWN❄ disabled",
                    message_thread_id=OF_TID,
                    chat_id=CHAT_ID,
                )
        await asyncio.sleep(10 * 60)


async def send_jee_reminder(cid, tid=None):
    await bot.send_chat_action(action="typing", message_thread_id=tid, chat_id=cid)
    jee_main, jee_adv, quote = jee_reminder()
    message = "*⏰ DAILY REMINDER*\n\n"
    message += "⏳" + str(jee_main) + " days left for JEE Main\n"
    message += "⏳" + str(jee_adv) + " days left for JEE Advanced\n\n"
    message += "_”" + quote.split("\n")[0] + "_”\n"
    message += "‎     ~ " + quote.split("\n")[1]
    await bot.send_message(
        text=message, chat_id=cid, message_thread_id=tid, parse_mode="markdown"
    )


async def send_dpp():
    await bot.send_chat_action(
        action="upload_document", chat_id=CHAT_ID, message_thread_id=DPP_ID
    )
    dpp = await get_dpp()
    if dpp is not None:
        topic = dpp[0]
        pages = dpp[1]
        fname = dpp[2]
        topic_names = {
            "Algebra": "Algebra",
            "Vector3DGeometry": "Vectors & 3D Geometry",
            "Mechanics-2": "Mechanics",
            "Magnetism": "Magnetism",
            "Trignometey": "Trigonometry",
            "WavesThermodynamics": "Waves & Thermodynamics",
            "CoordinateGeometry": "Coordinate Geometry",
            "Electrostatics": "Electrostatics",
            "Calculas": "Calculus",
            "PhysicalChemistry-2": "Physical Chemistry",
            "Physical-1": "Physical Chemistry",
            "OrganicChemistry-1": "Organic Chemistry",
            "InorganicChemistry-2": "Inorganic Chemistry",
            "Mechanics-1": "Mechanics",
            "InorganicChemistry-1": "Inorganic Chemistry",
            "Optics": "Optics & Modern Physics",
        }
        topic_name = topic_names[topic]
        jee_main, jee_adv, quote = jee_reminder()
        message = "*⏰ DAILY REMINDER*\n\n"
        message += "⏳" + str(jee_main) + " days left for JEE Main\n"
        message += "⏳" + str(jee_adv) + " days left for JEE Advanced\n\n"
        message += "_”" + quote.split("\n")[0] + "_”\n"
        message += "‎     ~ " + quote.split("\n")[1]
        await bot.send_document(
            CHAT_ID,
            InputFile(fname),
            caption="Daily DPP - Today's Topic: " + topic_name + "\n" + message,
            message_thread_id=DPP_ID,
        )
        eprint("sent dpp")
        os.remove(fname)
        os.remove("downloaded.pdf")
        topics = json.loads(await db.r.get("topics"))
        topics[topic]["dpps"].remove(pages)
        if len(topics[topic]["dpps"]) == 0:
            topics.pop(topic)
        await db.r.set("topics", json.dumps(topics))
    else:
        eprint("error sending dpp")


async def main():
    asyncio.create_task(update_slowdown())
    asyncio.create_task(stats.processMessageQueue())
    asyncio.create_task(server.run())
    await bot.polling()


if __name__ == "__main__":
    asyncio.run(main())
