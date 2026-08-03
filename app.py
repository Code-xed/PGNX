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
    url = await get_gamefactory_url(message)

    if not url:
        await message.reply(
            "Reply to a GameFactory chess message."
        )
        return

    await message.reply(url)

async def main():
    await app.start()

    me = await app.get_me()
    print(f"Logged in as {me.first_name} (@{me.username})")

    # Later:
    # await browser.start()

    await idle()

    # Later:
    # await browser.stop()

    await app.stop()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
