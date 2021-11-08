from aiohttp import web
from telebot import TeleBot
from telebot.types import Update

from data import config
from src.botrequests import HotelsRequester
from src.utils import sleep_before_call

bot = TeleBot(token=config.BOT_TOKEN, parse_mode='HTML')
# Задержка перед отправкой сообщения, чтобы не достичь лимита от Telegram
bot.send_message = sleep_before_call(func=bot.send_message, sleep_time=3)
bot.send_media_group = sleep_before_call(func=bot.send_media_group, sleep_time=3)

requester = HotelsRequester(api_key=config.API_KEY)
users = {}


async def webhook_handle(request):
    request_body_dict = await request.json()
    update = Update.de_json(request_body_dict)
    bot.process_new_updates([update])
    return web.Response()


app = web.Application()
app.router.add_post(f'/{config.URL_SECRET}', webhook_handle)
