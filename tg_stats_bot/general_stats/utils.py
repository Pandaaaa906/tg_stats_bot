from datetime import datetime
import shelve

import psutil

cache = shelve.open('db/cache')

alternative = (
    (1024 ** 5, 'PB'),
    (1024 ** 4, 'TB'),
    (1024 ** 3, 'GB'),
    (1024 ** 2, 'MB'),
    (1024 ** 1, 'KB'),
    (1024 ** 0, ('byte', 'bytes')),
)


def size(nbytes, system=alternative):
    for factor, suffix in system:
        if nbytes >= factor:
            break
    amount = nbytes / factor
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
