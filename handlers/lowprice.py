from loguru import logger
from telebot.types import Message

from loader import bot
from .processes import ask_city_step


@bot.message_handler(commands=['lowprice'])
def on_lowprice(msg: Message) -> None:
    """Обработчик команды `/lowprice`"""
    sender = msg.from_user
    log_text = f'Пользователь {sender.username}({sender.id}) прислал команду "/lowprice"'
    logger.info(log_text)

    chat_id = msg.chat.id

    text = 'Отправь мне имя города, в котором я буду искать отель для тебя.\n' \
           'Ты можешь писать на русском или английском языке.\n' \
           'Например: <code>Москва</code> или <code>Moscow</code>'
    sent_message = bot.send_message(chat_id, text)

    params = {'sort_order': 'low'}
    bot.register_next_step_handler(sent_message, ask_city_step, params)
