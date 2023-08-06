import asyncio
import db
import json
from eprint import eprint


messageq = asyncio.Queue()


async def processMessageQueue():
    while True:
        message = await messageq.get()
        await handle_message(message)


async def handle_message(message):
    user = str(message.from_user.id)
    topic = message.message_thread_id
    if topic is None:
        topic = -1
    topic = str(topic)
    stats = json.loads(await db.r.get("stats"))
    if user not in stats.keys():
        stats[user] = {}
        stats[user][topic] = 1
    elif topic not in stats[user]:
        stats[user][topic] = 1
    else:
        stats[user][topic] += 1
    await db.r.set("stats", json.dumps(stats))


async def get_topic_stats(topic):
    topic = str(topic)
    stats = json.loads(await db.r.get("stats"))
    top_users = []
    total_messages = 0
    for user in stats.keys():
        if not topic in stats[user].keys():
            continue
        total_messages += stats[user][topic]
        top_users.append([int(user), stats[user][topic]])
    top_users.sort(key=lambda i: i[1], reverse=True)
    top_users = top_users[:5]
    return total_messages, top_users


async def get_user_stats(user):
    try:
        user = str(user)
        stats = json.loads(await db.r.get("stats"))
        top_topics = []
        total_messages = 0
        if not user in stats.keys():
            return total_messages, top_topics
        for topic in stats[user].keys():
            total_messages += stats[user][topic]
            top_topics.append([int(topic), stats[user][topic]])
        top_topics.sort(key=lambda i: i[1], reverse=True)
        top_topics = top_topics[:5]
        return total_messages, top_topics
    except Exception as e:
        eprint(e)


async def get_overall_stats():
    stats = json.loads(await db.r.get("stats"))
    topics = {}
    users = []
    for user in stats.keys():
        tot = 0
        for topic in stats[user].keys():
            tot += stats[user][topic]
            if not topic in topics.keys():
                topics[topic] = stats[user][topic]
            else:
                topics[topic] += stats[user][topic]
        users.append([int(user), tot])
    users.sort(key=lambda i: i[1], reverse=True)
    users = users[:10]
    tmp = []
    for topic in topics.keys():
        tmp.append([int(topic), topics[topic]])
    topics = tmp
    topics.sort(key=lambda i: i[1], reverse=True)
    return users, topics
