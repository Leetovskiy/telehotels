from loguru import logger
from telebot.types import Message

from loader import bot


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
