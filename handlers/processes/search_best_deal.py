import re
from typing import Dict, Union

import requests
from loguru import logger
from telebot.types import Message

import utils
from loader import bot, requester

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
        bot.register_next_step_handler(error_message, ask_city_step)
        return

    try:
        destination_id = requester.search_destination(reply)
    except (requests.ConnectionError, requests.Timeout) as e:
        text = 'Ошибка: неудачная попытка соединения во время поиска города.\n' \
               'Попробуй еще раз'
        error_message = bot.send_message(chat_id, text)
        bot.register_next_step_handler(error_message, ask_city_step)
        logger.error(f'Ошибка при запросе destinationId: {e}')
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
    """
    Запросить диапазон цен у пользователя

    :param msg: обрабатываемое сообщение
    :param params: параметры запроса
    """

    chat_id = msg.chat.id
    reply = msg.text

    user = msg.from_user
    logger.info(f'Запрос диапазона цен ({user.username} – {user.id}), ответ: {reply}')

    if not re.fullmatch(r'^\d+-\d+$', reply):
        text = 'Ошибка: некорректный ввод диапазона цен.\n' \
               'Диапазон должен быть в формате: "мин-макс".\n' \
               'Например: 300-1200'
        error_message = bot.send_message(chat_id, text)
        bot.register_next_step_handler(error_message, ask_price_range_step, params)
        return

    min_price, max_price = map(int, re.findall(r'\d+', reply))
    if not (0 < min_price < max_price):
        text = 'Ошибка: некорректный ввод диапазона цен.\n' \
               'Минимальная цена должна быть меньше максимальной, ' \
               'цены должны быть больше нуля'
        error_message = bot.send_message(chat_id, text)
        bot.register_next_step_handler(error_message, ask_price_range_step, params)
        return

    params['min_price'] = min_price
    params['max_price'] = max_price

    text = 'Введи диапазон отдаленности (км) отеля от центра в формате: мин_макс.\n' \
           'Например: 0.5-2.0'
    sent_message = bot.send_message(chat_id, text)
    bot.register_next_step_handler(sent_message, ask_distance_range_step, params)


def ask_distance_range_step(msg: Message, params: REQ_PARAMS_TYPE) -> None:
    """
    Запросить диапазон отдаленности отеля от центра

    :param msg: обрабатываемое сообщение
    :param params: параметры запроса
    """

    chat_id = msg.chat.id
    reply = msg.text

    user = msg.from_user
    logger.info(f'Запрос диапазона расстояния от центра ({user.username} – {user.id}), ответ: {reply}')

    if not re.fullmatch(r'^\d+\.*\d*-\d+\.*\d*$', reply):
        text = 'Ошибка: некорректный ввод.\n' \
               'Диапазон должен быть в формате: мин-макс.\n' \
               'Например: 0.5-3.0'
        error_message = bot.send_message(chat_id, text)
        bot.register_next_step_handler(error_message, ask_distance_range_step, params)
        return

    min_dist, max_dist = map(float, re.findall(r'\d+\.*\d*', reply))
    if not (0 < min_dist < max_dist):
        text = 'Ошибка: некорректный ввод диапазона.\n' \
               'Минимальное значение должно быть меньше максимального,' \
               'все значения должны быть больше нуля'
        error_message = bot.send_message(chat_id, text)
        bot.register_next_step_handler(error_message, ask_price_range_step, params)
        return

    params['min_dist'] = min_dist
    params['max_dist'] = max_dist

    text = 'Я могу вывести до 5-ти отелей. Сколько ты хочешь увидеть?'
    sent_message = bot.send_message(chat_id, text)
    bot.register_next_step_handler(sent_message, ask_count_step, params)


def ask_count_step(msg: Message, params: REQ_PARAMS_TYPE) -> None:
    pass
