import asyncio
from asyncio import Event

from loguru import logger
from telethon import events
from telethon.errors import MessageIdInvalidError
from telethon.tl.custom import Button
from telethon.utils import get_display_name

from settings import client, bot_owner
from utils import start_up_msg, get_stats, white_list_user_only

logger.add("/logs/tg_bot.log", rotation="1 week")


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

exit_flag: bool = False
ready_start = Event()
ready_start.set()


@client.on(events.NewMessage(pattern=r'^/report_here'))
@logger.catch
@white_list_user_only({bot_owner, })
async def report_here(event):
    global exit_flag
    exit_flag = True
    msg = await event.reply(get_stats())
    await ready_start.wait()
    exit_flag = False
    ready_start.clear()
    while not exit_flag:
        await asyncio.sleep(3)
        try:
            await msg.edit(get_stats())
        except MessageIdInvalidError:
            logger.debug('Message gone')
            return
    else:
        await msg.delete()
        ready_start.set()


@client.on(events.NewMessage(pattern='^/btn'))
@logger.catch
async def send_btn(event):
    logger.debug('ready to send btn')
    await event.reply('Pick one from this grid', buttons=[
        [Button.inline('Left'), Button.inline('Middle'), Button.inline('Right')],
    ])


@client.on(events.CallbackQuery)
@logger.catch
async def callback(event):
    await event.edit('Thank you for clicking {}!'.format(event.data))


if __name__ == '__main__':
    logger.info("Starting Connection")
    with client:
        logger.info("Connection Established")
        client.loop.run_until_complete(start_up_msg(client))
        client.run_until_disconnected()
