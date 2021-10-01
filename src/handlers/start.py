from loguru import logger
from telebot.types import Message

from src.loader import bot
from src.loader import users
from src.user.user import User


@bot.message_handler(commands=['start'])
def on_start(msg: Message) -> None:
    """Обработчик команды `/start`"""
    sender = msg.from_user
    log_text = f'Пользователь {sender.username}({sender.id}) прислал команду "/start"'
    logger.info(log_text)

    chat_id = msg.chat.id
    text = 'Привет! Я TeleHotels Bot и могу помочь тебе подобрать отель на Hotels.com\n' \
           'Чтобы ознакомиться с тем, что я умею используй команду /help'

    if chat_id not in users:
        users[chat_id] = User(chat_id)

    bot.send_message(chat_id, text)
