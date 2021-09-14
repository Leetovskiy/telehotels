import requests
from telebot.types import Message
from loguru import logger
from loader import bot, requester
import utils
from typing import Dict, Union

REQ_PARAMS_TYPE = Dict[str, Union[str, int]]


def ask_city_step(msg: Message) -> None:
    """
    Запросить город поиска у пользователя

    :param msg: обрабатываемое сообщение
    """

    chat_id = msg.chat.id
    reply = msg.text

    user = msg.from_user
    logger.info(f'Запрос города ({user.username} – {user.id}), ответ: {reply}')

    if utils.locale_from_string(reply) is None:
        text = 'Некорректный ввод: не получилось определить язык сообщения.\n' \
               'Попробуй еще раз'
        error_message = bot.send_message(chat_id, text)
        bot.register_next_step_handler(error_message, ask_city_step,)
        return

    try:
        destination_id = requester.search_destination(reply)
    except (requests.ConnectionError, requests.Timeout) as e:
        text = 'Ошибка: неудачная попытка соединения во время поиска города.\n' \
               'Попробуй еще раз'
        error_message = bot.send_message(chat_id, text)
        bot.register_next_step_handler(error_message, ask_city_step)
        return

    if destination_id is None:
        text = 'Некорректный ввод: не удалось найти город по твоему запросу.\n' \
               'Попробуй набрать что-то другое'
        error_message = bot.send_message(chat_id, text)
        bot.register_next_step_handler(error_message, ask_city_step)
        return
    params = dict()
    params['destination_id'] = destination_id

    text = 'Введи желаемый ценовой диапазон поиска в формате "мин_цена-макс_цена".\n' \
           'Например: <code>700-1500</code>\n' \
           '(Имеется ввиду цена за одного человека в сутки)'
    sent_message = bot.send_message(chat_id, text)
    bot.register_next_step_handler(sent_message, ask_price_range_step, params)


def ask_price_range_step(msg: Message, params: REQ_PARAMS_TYPE) -> None:
    pass
