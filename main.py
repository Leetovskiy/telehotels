import os

from dotenv import load as dotenv_load
from telebot import TeleBot

dotenv_load()
BOT_TOKEN = os.getenv('TG_BOT_TOKEN')

bot = TeleBot(token=BOT_TOKEN)


@bot.message_handler(commands=['hello-world'])
def _greeting_cmd(msg) -> None:
    """Обработчик команды `/hello-world`"""
    user_id = msg.from_user.id
    answer = 'Привет-привет!'
    bot.send_message(user_id, answer)


@bot.message_handler(regexp=r'^привет$')
def _hello_message(msg) -> None:
    """Обработчик сообщений с вхождением 'привет'"""
    user_id = msg.from_user.id
    answer = 'Как мило! И тебе привет!'
    bot.send_message(user_id, answer)


@bot.message_handler(func=lambda x: True)
def _any_message_handler(msg) -> None:
    """Обработчик любых сообщений"""
    user_id = msg.from_user.id
    answer = 'Я тебя не понимаю. Лучше скажи "привет" или набери команду "/hello-world"'
    bot.send_message(user_id, answer)


bot.polling(non_stop=True)
