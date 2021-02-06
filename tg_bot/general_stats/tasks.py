import asyncio

from loguru import logger
from telethon import TelegramClient
from telethon.errors import MessageIdInvalidError, MessageNotModifiedError, MessageDeleteForbiddenError
from telethon.utils import get_display_name

from .utils import get_stats, cache


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
            try:
                await cli.delete_messages(last_chat, last_msg_id)
            except MessageDeleteForbiddenError as e:
                logger.info(f'{e}, chat:{get_display_name(last_chat)}, msg_id:{last_msg_id}')
        last_msg_id, last_chat_id = msg_id, chat_id
        if msg_id is None:
            continue
        try:
            await cli.edit_message(chat, msg_id, get_stats())
        except MessageIdInvalidError:
            cache['chat_id'], cache['msg_id'] = None, None
            cache.sync()
            logger.debug('Message gone')
            continue
        except MessageNotModifiedError:
            continue
