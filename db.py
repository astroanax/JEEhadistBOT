import redis.asyncio as redis
import main
from telebot.util import user_link
import os
from eprint import eprint

r = redis.Redis(
    host=os.environ["REDIS_HOST"],
    port=int(os.environ["REDIS_PORT"]),
    password=os.environ["REDIS_PASS"],
)


async def get_thread_id(user):
    t_id = await r.get(user.id)
    if t_id is None:
        t_id = await create_topic_log(user)
    return int(t_id)


async def create_topic_log(user):
    user_id = user.id
    chat = await main.bot.get_chat(user_id)
    t_name = chat.username
    f_name = chat.first_name
    l_name = chat.last_name
    if t_name is None:
        t_name = ""
    if f_name is None:
        f_name = ""
    if l_name is None:
        l_name = ""
    t_name += " - " + f_name + " " + l_name
    t_name = t_name[:100] + " - " + str(user_id)
    topic = await main.bot.create_forum_topic(chat_id=main.LOG_CHAT_ID, name=t_name)
    text = user_link(user=user, include_id=True)
    await main.bot.send_message(
        chat_id=main.LOG_CHAT_ID,
        message_thread_id=topic.message_thread_id,
        text=text,
        parse_mode="html",
    )
    await r.set(user_id, topic.message_thread_id)
    await r.set("T" + str(topic.message_thread_id), user_id)
    eprint("created topic log for ", user_id, " , thread id ", topic.message_thread_id)
    return topic.message_thread_id


async def get_userid(tid):
    user_id = int(await r.get("T" + str(tid)))
    return user_id
