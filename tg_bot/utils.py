from datetime import datetime
from functools import wraps

import psutil
from loguru import logger
from telethon.utils import get_display_name


async def start_up_msg(cli):
    me = await cli.get_me()
    logger.info(f"Logged in as: {get_display_name(me)}")


def white_list_user_only(username_whitelist: set):
    def outer_wrapper(func):
        @wraps(func)
        async def wrapper(event):
            sender = await event.get_sender()
            if sender.username not in username_whitelist:
                return
            ret = await func(event)
            return ret
        return wrapper
    return outer_wrapper


alternative = (
    (1024 ** 5, 'PB'),
    (1024 ** 4, 'TB'),
    (1024 ** 3, 'GB'),
    (1024 ** 2, 'MB'),
    (1024 ** 1, 'KB'),
    (1024 ** 0, ('byte', 'bytes')),
)


def size(bytes, system=alternative):
    for factor, suffix in system:
        if bytes >= factor:
            break
    amount = bytes/factor
    if isinstance(suffix, tuple):
        singular, multiple = suffix
        suffix = singular if amount == 1 else multiple
    return f'{amount:.1f} {suffix}'


def get_stats():
    cpu_percent = psutil.cpu_percent(percpu=True)
    temperatures = psutil.sensors_temperatures() if hasattr(psutil, 'sensors_temperatures') else {}
    acp_temp = temperatures.get("acpitz", [])
    memory = psutil.virtual_memory()
    cpu_str = "\n".join(f"CPU{i}: {n}%" for i, n in enumerate(cpu_percent))
    now = datetime.now().astimezone()
    return (
        '```\n'
        f'{cpu_str}\n'
        f'Memory: {size(memory.used, system=alternative)}/{size(memory.total, system=alternative)}\n'
        f'Temperatures: \n'
        f'{" ".join(f"{x.current:.1f}℃" for x in acp_temp) or "N/A"}\n\n'
        f'Last update: \n{now.strftime("%Y-%m-%d")}\n{now.strftime("%H:%M:%S.%f%Z")}'
        '```'
    )
