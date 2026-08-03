from pyrogram.types import Message


async def get_gamefactory_url(message: Message) -> str | None:
    """
    Extract the GameFactory game URL from a replied message.
    """

    if not message.reply_to_message:
        return None

    reply = message.reply_to_message

    if not reply.reply_markup:
        return None

    keyboard = reply.reply_markup.inline_keyboard

    for row in keyboard:
        for button in row:
            if (
                getattr(button, "url", None)
                and "gamefactory.zone/chess" in button.url
            ):
                return button.url

    return None
