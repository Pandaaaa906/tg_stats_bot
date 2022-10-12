from loguru import logger
from telethon import events

from .utils import cache
from settings import bot_owner
from telethon_utils.decorators import white_list_user_only


@events.register(events.NewMessage(pattern=r'^/report_here'))
@logger.catch
@white_list_user_only({bot_owner, })
async def report_here(event):
    msg = await event.reply("Waiting for worker")
    cache['chat_id'], cache['msg_id'] = event.chat_id, msg.id
    cache.sync()
