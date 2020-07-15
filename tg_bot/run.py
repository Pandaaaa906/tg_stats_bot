from loguru import logger
from telethon import events
from telethon.tl.custom import Button
from telethon.utils import get_display_name

from settings import client
from utils import start_up_msg

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


@client.on(events.NewMessage(pattern='^/btn'))
@logger.catch
async def send_btn(event):
    message = event.message
    logger.debug('ready to send btn')
    await event.reply('Pick one from this grid', buttons=[
        [Button.inline('Left'), Button.inline('Middle'), Button.inline('Right')],
        # [Button.url('Check this site!', 'https://lonamiwebs.github.io')],
        # [Button.text('Thanks!', resize=True, single_use=True)],
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
