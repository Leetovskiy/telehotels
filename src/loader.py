from telebot import TeleBot

from data import config
from src.botrequests import HotelsRequester
from src.utils import db_api

bot = TeleBot(token=config.BOT_TOKEN, parse_mode='HTML')

requester = HotelsRequester(api_key=config.API_KEY)

database = db_api.Database(database_path=config.DATABASE_PATH)
database.create_users_table()
database.create_history_table()
