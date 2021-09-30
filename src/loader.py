from telebot import TeleBot

from botrequests import HotelsRequester
from data import config

bot = TeleBot(token=config.BOT_TOKEN, parse_mode='HTML')
requester = HotelsRequester(api_key=config.API_KEY)
