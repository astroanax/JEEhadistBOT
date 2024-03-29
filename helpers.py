from telethon.sync import TelegramClient
from telethon.tl.functions.users import GetFullUserRequest
import os
import sys
import asyncio
from eprint import eprint

api_id = int(os.environ["TG_API_ID"])
api_hash = os.environ["TG_API_HASH"]
bot_token = os.environ["TG_BOT_TOKEN"]


async def resolve_username(username):
    try:
        os.remove("bot.session")
    except:
        pass
    bot = await TelegramClient("bot", api_id, api_hash).start(bot_token=bot_token)
    try:
        result = await bot(GetFullUserRequest(id=username))
        return int(result.full_user.id)
    except ValueError:
        eprint("no user found with ", username)
        return None


def resolve_topic(topic):
    if type(topic) == int:
        topics = {
            -1: "General",
            11695: "Notices",
            3471: "Offtopic",
            8336: "Daily Target",
            7788: "Daily Progress",
            2: "Doubts - Physics",
            11693: "Doubts - Chemistry",
            11694: "Doubts - Math",
            3385: "Material",
            3389: "Motivation",
            15099: "Daily DPP Discussion",
        }
        try:
            result = topics[topic]
            return result
        except KeyError:
            #eprint("unknown topic", topic)
            return "unknown topic"
    elif type(topic) == str:
        topics = {
            "general": -1,
            "notices": 11695,
            "offtopic": 3471,
            "daily-target": 8336,
            "daily-progress": 7788,
            "daily-dpp-discussion": 15099,
            "doubts-physics": 2,
            "doubts-chemistry": 11693,
            "doubts-math": 11694,
            "doubts": [2, 11693, 11694],
            "material": 3385,
            "motivation": 3389,
        }
        try:
            result = topics[topic]
            return result
        except KeyError:
            return None


async def main():
    print(await resolve_username(sys.argv[1]))


if __name__ == "__main__":
    asyncio.run(main())
