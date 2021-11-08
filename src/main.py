from aiohttp import web

import src.handlers
from data.config import WEBHOOK_URL
from src.loader import bot, app

if __name__ == '__main__':
    bot.delete_webhook()
    bot.set_webhook(url=WEBHOOK_URL)

    web.run_app(
        app,
        host='0.0.0.0',
        port=8443
    )
