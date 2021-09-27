from loader import bot
from telebot.types import Message
from loguru import logger
from .processes import bestdeal_ask_city_step


@bot.message_handler(commands=['bestdeal'])
def on_bestdeal(msg: Message) -> None:
    """Обработчик команды `/bestdeal`"""
    sender = msg.from_user
    log_text = f'Пользователь {sender.username}({sender.id}) прислал команду "/bestdeal"'
    logger.info(log_text)

    chat_id = msg.chat.id

    text = 'Отправь мне имя города, в котором я буду искать отель для тебя.\n' \
           'Ты можешь писать на русском или английском языке.\n' \
           'Например: <code>Москва</code> или <code>Moscow</code>'
    sent_message = bot.send_message(chat_id, text)

    bot.register_next_step_handler(sent_message, bestdeal_ask_city_step)
