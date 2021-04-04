from loguru import logger
from telethon.utils import get_display_name


async def start_up_msg(cli):
    me = await cli.get_me()
    logger.info(f"Logged in as: {get_display_name(me)}")
