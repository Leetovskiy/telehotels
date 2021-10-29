from sqlite3 import OperationalError

from loguru import logger
from telebot.types import Message

from src.loader import bot, database


@bot.message_handler(commands=['start'])
def on_start(msg: Message) -> None:
    """Обработчик команды `/start`"""
    sender = msg.from_user
    log_text = f'Пользователь {sender.username}({sender.id}) прислал команду "/start"'
    logger.info(log_text)

    chat_id = msg.chat.id
    text = 'Привет! Я TeleHotels Bot и могу помочь тебе подобрать отель на Hotels.com\n' \
           'Чтобы ознакомиться с тем, что я умею используй команду /help'
    bot.send_message(chat_id, text)

    try:
        database.add_user(user_id=sender.id, username=sender.username)
    except OperationalError as e:
        log_text = f'Не удалось добавить пользователя в БД: {e}'
        logger.error(log_text)
