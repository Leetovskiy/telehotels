from sys import argv

from aiohttp import web
from loguru import logger

import src.handlers
from src.loader import bot

if __name__ == '__main__':
    bot.delete_webhook()

    if '--webhook' in argv[1:]:
        from data.config import WEBHOOK_URL
        from src.loader import app

        logger.info('Запуск бота (Webhook-метод)')
        bot.set_webhook(url=WEBHOOK_URL)
        web.run_app(
            app,
            host='0.0.0.0',
            port=8443
        )
    else:
        logger.info('Запуск бота (Polling-метод)')
        bot.infinity_polling(interval=5)
