import os
from pyrogram import Client, idle, filters
from gamefactory import get_gamefactory_url

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION_STRING = os.environ["SESSION_STRING"]

app = Client(
    "backend",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING,
)


@app.on_message(filters.command("pgn"))
async def pgn_handler(client, message):
    from flyonce import sniff

    await sniff()

    await message.reply("Done. Check Fly logs.")

app.run()
