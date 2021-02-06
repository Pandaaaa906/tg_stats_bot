from os import getenv

import docker
from loguru import logger
from telethon import events

from settings import bot_owner
from telethon_utils.decorators import white_list_user_only

DOCKER_URL = getenv('DOCKER_URL', 'unix:///var/run/docker.sock')


@events.register(events.NewMessage(pattern=r'^/container_stats$'))
@white_list_user_only({bot_owner, })  # TODO too mix up
async def container_stats(event: events.NewMessage):
    logger.debug(f'Reporting containers stats')
    d = docker.APIClient(DOCKER_URL)
    containers = d.containers(all=True)
    total_containers = len(containers)
    running_containers = sum((1 for container in containers if container.get('State') == 'running'))

    containers = sorted(containers, key=lambda x: 0 if x['State'] == 'running' else 1)
    logger.debug(containers)
    text = '\n'.join(
        f'{";".join(container.get("Names", []))}:\n'
        f'    {container.get("State")}, {container.get("Status")}.'
        for container in containers)
    text = f'```{text}\n' \
           f'Total: {total_containers}\n' \
           f'Running: {running_containers}```'
    await event.reply(text)
