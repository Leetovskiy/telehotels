from sys import argv

from aiohttp import web
from telebot import TeleBot
from telebot.types import Update

from data import config
from src.botrequests import HotelsRequester
from src.utils import db_api

bot = TeleBot(token=config.BOT_TOKEN, parse_mode='HTML')

requester = HotelsRequester(api_key=config.API_KEY)

database = db_api.Database(database_path=config.DATABASE_PATH)
database.create_users_table()
database.create_history_table()


if '--webhook' in argv[1:]:
    async def webhook_handle(request):
        request_body_dict = await request.json()
        update = Update.de_json(request_body_dict)
        bot.process_new_updates([update])
        return web.Response()

    app = web.Application()
    app.router.add_post(f'/{config.URL_SECRET}', webhook_handle)
