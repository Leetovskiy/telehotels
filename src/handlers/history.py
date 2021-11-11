from loguru import logger
from telebot.types import Message

from src.loader import bot, database


@bot.message_handler(commands=['history'])
def on_history(msg: Message) -> None:
    """Обработчик команды `/history`"""
    sender = msg.from_user
    chat_id = msg.chat.id
    log_text = f'Пользователь {sender.username}({sender.id}) прислал команду "/history"'
    logger.info(log_text)

    history = database.select_from_history(user_id=sender.id)

    if len(history) == 0:
        text = 'История пока что пуста ;(\n' \
               'Хороший повод попробовать одну из моих команд: /help'
        bot.send_message(chat_id, text)
        return

    history_strings = (f'  • /{elem["command"]} – {elem["city"]}' for elem in history)

    text = '\n'.join(('История запросов: ', *history_strings))
    bot.send_message(chat_id, text)
