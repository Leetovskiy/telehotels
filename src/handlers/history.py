from loguru import logger
from telebot.types import Message

from src.loader import bot
from src.loader import users


@bot.message_handler(commands=['history'])
def on_history(msg: Message) -> None:
    """Обработчик команды `/history`"""
    sender = msg.from_user
    chat_id = msg.chat.id
    log_text = f'Пользователь {sender.username}({sender.id}) прислал команду "/history"'
    logger.info(log_text)

    try:
        history = users[chat_id].history
    except KeyError:
        history = []

    if len(history) == 0:
        text = 'История пока что пуста.\n' \
               'Хороший повод попробовать одну из моих команд: /help'
        bot.send_message(chat_id, text)
        return

    history_string = ';\n'.join(map(str, history))
    text = f'История запросов:\n' \
           f'{history_string}'
    bot.send_message(chat_id, text)
