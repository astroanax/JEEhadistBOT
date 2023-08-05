from aiogoogle import Aiogoogle
import os
import json
import asyncio
import sys
import random
import db
import datetime
from eprint import eprint
from PyPDF2 import PdfWriter, PdfReader


async def download_file(file_id, path):
    async with Aiogoogle(api_key=os.environ["GOOGLE_API_KEY"]) as aiogoogle:
        drive_v3 = await aiogoogle.discover("drive", "v3")
        await aiogoogle.as_api_key(
            drive_v3.files.get(fileId=file_id, download_file=path, alt="media"),
        )


async def get_dpp():
    try:
        topics = json.loads(await db.r.get("topics"))
        t = []
        for topic in topics:
            t += [topic] * topics[topic]["weight"]
        topic = random.choice(t)
        pages = random.choice(topics[topic]["dpps"])
        fname = topic + "-" + str(datetime.datetime.now().date()) + ".pdf"
        dpp = [topic, pages, fname]
        eprint("chosen dpp: ", topic, pages)
        link = topics[topic]["link"]
        await download_file(link[33:], "downloaded.pdf")
        split_pdf(pages, fname)
        return dpp
    except Exception as e:
        eprint(e)
        return None


def split_pdf(pages, fname):
    reader = PdfReader("downloaded.pdf")
    writer = PdfWriter()
    for i in range(pages[0], pages[1] + 1):
        writer.add_page(reader.pages[i - 1])
    with open(fname, "wb") as fp:
        writer.write(fp)


if __name__ == "__main__":
    asyncio.run(get_dpp())
