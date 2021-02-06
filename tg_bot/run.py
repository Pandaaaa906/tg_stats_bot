from loguru import logger
from telethon import events
from telethon.utils import get_display_name

from docker_stats.plugin import container_stats
from general_stats.handlers import report_here
from general_stats.tasks import refresh_stats
from settings import client
from utils import start_up_msg

logger.add("logs/tg_bot.log", rotation="1 week")


@client.on(events.NewMessage)
@logger.catch
async def catch_every_thing(event):
    sender = await event.get_sender()
    sender_name = get_display_name(sender)
    logger.info(f"{sender_name} say:{event.raw_text}")


@client.on(events.NewMessage(pattern=r'^/check'))
@logger.catch
async def check_user_id(event):
    message = event.message
    source_msg = message
    if message.is_reply:
        source_msg = await message.get_reply_message()
    sender = await source_msg.get_sender()
    await message.reply(f"Id: <a href='tg://user?id={sender.id}'>{sender.id}</a>\n"
                        f"User Name: <b>{sender.username}</b>\n"
                        f"Display Name: <b>{get_display_name(sender)}</b>",
                        parse_mode='html')


@client.on(events.NewMessage(pattern=r'^/chat_id'))
@logger.catch
async def check_chat_id(event):
    chat = event.chat
    await event.reply(
        f'chat_id: {chat.id}\n'
        f'chat_title: {chat.title}'
    )


if __name__ == '__main__':
    logger.info("Starting Connection")
    with client:
        logger.info("Connection Established")

        # docker plugin
        client.add_event_handler(container_stats)

        # general stats plugin
        client.add_event_handler(report_here)
        client.loop.create_task(refresh_stats(client))

        client.loop.run_until_complete(start_up_msg(client))
        client.run_until_disconnected()
