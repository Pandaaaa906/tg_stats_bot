import asyncio
import shelve

from loguru import logger
from telethon import events, TelegramClient
from telethon.errors import MessageIdInvalidError
from telethon.utils import get_display_name

from settings import client, bot_owner
from utils import start_up_msg, get_stats, white_list_user_only

logger.add("logs/tg_bot.log", rotation="1 week")
cache = shelve.open('db/cache')


@logger.catch
async def refresh_stats(cli: TelegramClient, gap=3):
    last_chat_id, last_msg_id = None, None
    while True:
        await asyncio.sleep(gap)
        chat_id, msg_id = cache.get('chat_id'), cache.get('msg_id')
        if chat_id is None:
            continue
        chat = await cli.get_input_entity(chat_id)
        if last_msg_id and last_msg_id != msg_id:
            last_chat = await cli.get_input_entity(last_chat_id)
            await client.delete_messages(last_chat, last_msg_id)
        last_msg_id, last_chat_id = msg_id, chat_id
        if msg_id is None:
            continue
        try:
            await client.edit_message(chat, msg_id, get_stats())
        except MessageIdInvalidError:
            cache['chat_id'], cache['msg_id'] = None, None
            cache.sync()
            logger.debug('Message gone')
            continue
        except MessageNotModifiedError:
            continue


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


@client.on(events.NewMessage(pattern=r'^/report_here$'))
@logger.catch
@white_list_user_only({bot_owner, })
async def report_here(event):
    msg = await event.reply("Waiting for worker")
    cache['chat_id'], cache['msg_id'] = event.chat_id, msg.id
    cache.sync()


if __name__ == '__main__':
    logger.info("Starting Connection")
    with client:
        logger.info("Connection Established")
        client.loop.run_until_complete(start_up_msg(client))
        client.loop.create_task(refresh_stats(client))
        client.run_until_disconnected()
