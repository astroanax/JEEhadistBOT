import asyncio
import kcet
import os
import main
import updates
from eprint import eprint


async def handle_client(reader, writer):
    response = "HTTP/1.1 200 OK\n\nJEEhadistBOT running"
    request = (await reader.read(255)).decode("utf8")
    if len(request.strip()) != 0 and "User-Agent: Render/1.0" not in request:
        if not request.startswith("GET / HTTP/1.1") and "Cf-Ray" not in request:
            eprint(request)
    if request.startswith("GET /sendJeeReminder?auth=@droppers95tards1"):
        eprint("sending jee reminder 1")
        await main.send_jee_reminder(main.CHAT_ID, main.NTC_ID)
        await main.send_jee_reminder(main.remind_jee_users[0])
    elif request.startswith("GET /sendJeeReminder?auth=@droppers95tards2"):
        eprint("sending jee reminder 2")
        await main.send_jee_reminder(main.remind_jee_users[1])

    elif request.startswith("GET /sendDailyDpp"):
        await main.send_dpp()

    elif request.startswith("GET /getNewsUpdates"):
        eprint("polling for news updates")
        # kcet_message = ""
        # kcet_updates = await kcet.get_kcet_updates()
        # eprint("kcet ", kcet_updates)
        # if len(kcet_updates) > 0:
        #    kcet_message += "KCET Updates📢\n"
        #    for link in kcet_updates:
        #        kcet_message += "▪️ " + str(link) + "\n"
        # if len(kcet_message) > 0:
        #    await main.bot.send_message(
        #        chat_id=main.ADMIN_ID, text=kcet_message, parse_mode="html"
        #    )

        message = ""
        csab = await updates.get_csab_updates()
        eprint("csab ", csab)
        if len(csab) > 0:
            message += "CSAB Updates📢\n"
            for link in csab:
                message += "▪️ " + str(link) + "\n"
            message += "\n"

        josaa = await updates.get_josaa_updates()
        eprint("josaa ", josaa)
        if len(josaa) > 0:
            message += "JoSAA Updates📢\n"
            for link in josaa:
                message += "▪️ " + str(link) + "\n"
            message += "\n"

        jeemain = await updates.get_jeemain_updates()
        eprint("jeemain ", jeemain)
        if len(jeemain) > 0:
            message += "JEE Main Updates📢\n"
            for link in jeemain:
                message += "▪️ " + str(link) + "\n"
            message += "\n"

        if len(message) > 0:
            await main.bot.send_chat_action(
                action="typing", chat_id=main.CHAT_ID, message_thread_id=main.NTC_ID
            )
            eprint("sending update")
            await main.bot.send_message(
                chat_id=main.CHAT_ID,
                message_thread_id=main.NTC_ID,
                text=message,
                parse_mode="html",
            )
    writer.write(response.encode("utf8"))
    await writer.drain()
    writer.close()


async def run():
    server = await asyncio.start_server(
        handle_client, "0.0.0.0", int(os.environ["PORT"])
    )
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(run())
