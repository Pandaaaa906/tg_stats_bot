from os import path, getenv

import socks
from telethon import TelegramClient

BASE_DIR = path.dirname(path.abspath(__file__))

APP_NAME = getenv('APP_NAME', "TG_BOT")
PROXY_HOST = getenv('PROXY_HOST')
PROXY_PORT = int(getenv('PROXY_PORT'))

api_id = getenv('api_id')
api_hash = getenv('api_hash')
bot_token = getenv('bot_token')
phone = getenv('phone')
bot_owner = getenv('bot_owner')

proxy = None
if PROXY_HOST:
    proxy = (socks.SOCKS5, PROXY_HOST, PROXY_PORT)

client = TelegramClient(path.join(BASE_DIR, 'session', APP_NAME),
                        api_id=api_id,
                        api_hash=api_hash,
                        proxy=proxy,
                        flood_sleep_threshold=20)\
    .start(bot_token=bot_token)

