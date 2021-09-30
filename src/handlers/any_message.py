from loguru import logger
from telebot.types import Message

from src.loader import bot


@bot.message_handler(func=lambda x: True)
def on_any_message(msg: Message) -> None:
    """Обработчик любого непредвиденного сообщения"""
    sender = msg.from_user
    log_text = f'Пользователь {sender.username}({sender.id}) прислал сообщение: {msg.text}'
    logger.info(log_text)

    chat_id = msg.chat.id
    text = 'Я тебя не понимаю.\n' \
           'Лучше взгляни на то, что я умею: /help'

    bot.send_message(chat_id, text)
