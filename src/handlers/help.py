from loguru import logger
from telebot.types import Message

from src.loader import bot


@bot.message_handler(commands=['help'])
def on_help(msg: Message) -> None:
    """Обработчик команды `/help`"""
    sender = msg.from_user
    log_text = f'Пользователь {sender.username}({sender.id}) прислал команду "/help"'
    logger.info(log_text)

    chat_id = msg.chat.id
    text = 'Просто набери одну из команд, а дальше я тебя сориентирую.\n' \
           'Команды:\n' \
           '    &#128073; /start – начать работу с ботом;\n' \
           '    &#128073; /help – посмотреть эту подсказку;\n' \
           '    &#128073; /lowprice – найти самые дешевые отели в городе;\n' \
           '    &#128073; /highprice – найти самые дорогие отели в городе;\n' \
           '    &#128073; /bestdeal – найти отели по заданной цене и отдаленности от центра города;\n' \
           '    &#128073; /history – посмотреть историю поиска.'

    bot.send_message(chat_id, text)
