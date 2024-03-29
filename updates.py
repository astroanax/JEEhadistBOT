from bs4 import BeautifulSoup as bs
import asyncio
import pickle
import sys
import requests
import datetime
import pytz
import db

JEE_ADV = datetime.datetime(2024, 5, 26, tzinfo=pytz.timezone("Asia/Kolkata"))
JEE_MAIN = datetime.datetime(2024, 1, 27, tzinfo=pytz.timezone("Asia/Kolkata"))


def jee_reminder():
    jee_adv = (JEE_ADV - datetime.datetime.now(pytz.timezone("Asia/Kolkata"))).days
    jee_main = (JEE_MAIN - datetime.datetime.now(pytz.timezone("Asia/Kolkata"))).days
    r = requests.get("https://www.insightoftheday.com/")
    soup = bs(r.text, features="lxml")
    quote = (
        soup.find_all("div", {"class": "quote"})[1]
        .find("img")["alt"]
        .lstrip(" motivational quote: ")
        .replace("</p><p>", "\n")
    ).replace("\xa0 \xa0", "\n")
    return jee_main, jee_adv, quote


async def get_csab_updates():
    rq = requests.get("https://csab.nic.in/notices/")
    soup = bs(rq.text, "html.parser")
    container = soup.find("div", {"class": "data-table-container"})
    links = container.find_all("a")
    del links[2::3]
    del links[1::2]
    new_notices = links[:]
    try:
        news = pickle.loads(await db.r.get("news"))
    except:
        news = {"csab":[], "jeemain":[], "josaa":[], "jeeadv":[]}
        await db.r.set("news", pickle.dumps(news))
    old_notices = news["csab"]
    news["csab"] = new_notices
    sys.setrecursionlimit(2**16)
    await db.r.set("news", pickle.dumps(news))
    sys.setrecursionlimit(1000)
    return list(set(new_notices) - set(old_notices))


async def get_josaa_updates():
    rq = requests.get("https://josaa.nic.in/notices/")
    soup = bs(rq.text, "html.parser")
    container = soup.find("div", {"class": "data-table-container"})
    links = container.find_all("a")
    del links[2::3]
    del links[1::2]
    new_notices = links[:]
    try:
        news = pickle.loads(await db.r.get("news"))
    except:
        news = {"csab":[], "jeemain":[], "josaa":[], "jeeadv":[]}
        await db.r.set("news", pickle.dumps(news))
    old_notices = news["josaa"]
    news["josaa"] = new_notices
    sys.setrecursionlimit(2**16)
    await db.r.set("news", pickle.dumps(news))
    sys.setrecursionlimit(1000)
    return list(set(new_notices) - set(old_notices))


async def get_jeemain_updates():
    rq = requests.get("https://jeemain.nta.ac.in/")
    soup = bs(rq.text, "html.parser")
    container = soup.find("div", {"class": "news-eve-scroll"})
    links = container.find_all("a")
    for link in links:
        for img in link("img"):
            img.decompose()
    new_notices = links[:]
    try:
        news = pickle.loads(await db.r.get("news"))
    except:
        news = {"csab":[], "jeemain":[], "josaa":[], "jeeadv":[]}
        await db.r.set("news", pickle.dumps(news))
    old_notices = news["jeemain"]
    news["jeemain"] = new_notices
    sys.setrecursionlimit(2**16)
    await db.r.set("news", pickle.dumps(news))
    sys.setrecursionlimit(1000)
    return list(set(new_notices) - set(old_notices))

async def get_jeeadv_updates():
    rq = requests.get("https://jeeadv.ac.in/")
    soup = bs(rq.text, "html.parser")
    container = soup.find("div", {"class": "col"})
    boxes = container.find_all("div", recursive=False)
    new_notices = boxes[:]
    try:
        news = pickle.loads(await db.r.get("news"))
    except:
        news = {"csab":[], "jeemain":[], "josaa":[], "jeeadv":[]}
        await db.r.set("news", pickle.dumps(news))
    old_notices = news["jeeadv"]
    news["jeeadv"] = new_notices
    sys.setrecursionlimit(2**16)
    await db.r.set("news", pickle.dumps(news))
    sys.setrecursionlimit(1000)
    return list(set(new_notices) - set(old_notices))

async def main():
    pass


if __name__ == "__main__":
    asyncio.run(main())
