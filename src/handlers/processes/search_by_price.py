from typing import Dict, Union, List

import requests
from loguru import logger
from telebot.apihelper import ApiException
from telebot.types import Message, InputMediaPhoto

from src import utils
from src.handlers.processes.search_best_deal import build_messages
from src.loader import bot, requester, database

REQ_PARAMS_TYPE = Dict[str, Union[str, int]]
BUILT_MESSAGES_TYPE = List[Dict[str, Union[str, List[InputMediaPhoto]]]]


def ask_city_step(msg: Message, params: REQ_PARAMS_TYPE) -> None:
    """
    Запросить город поиска у пользователя

    Args:
        msg: обрабатываемое сообщение
        params: параметры запроса
    """
    chat_id = msg.chat.id
    reply = msg.text

    user = msg.from_user
    logger.info(f'Запрос города ({user.username} – {user.id}), ответ: {reply}')

    if utils.locale_from_string(reply) is None:
        text = 'Некорректный ввод: не получилось определить язык сообщения.\n' \
               'Попробуй еще раз'
        error_message = bot.send_message(chat_id, text)
        bot.register_next_step_handler(error_message, ask_city_step, params)
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
    params['destination_id'] = destination_id
    params['city'] = reply

    text = 'Я могу вывести до 5-ти отелей. Сколько ты хочешь увидеть?'
    sent_message = bot.send_message(chat_id, text)
    bot.register_next_step_handler(sent_message, ask_count_step, params)


def ask_count_step(msg: Message, params: REQ_PARAMS_TYPE) -> None:
    """
    Запросить количество отелей для поиска

    Args:
        msg: обрабатываемое сообщение
        params: параметры запроса
    """
    chat_id = msg.chat.id
    reply = msg.text

    user = msg.from_user
    logger.info(f'Запрос количества отелей ({user.username} – {user.id}), ответ: {reply}')

    try:
        params['results_count'] = int(reply)
    except ValueError:
        text = 'Некорректный ввод: требуется число.'
        error_message = bot.send_message(chat_id, text)
        bot.register_next_step_handler(error_message, ask_count_step, params)
        return
    if not 0 < params['results_count'] <= 5:
        text = 'Некорректный ввод: число должно быть в диапазоне от 1 до 5 включительно.'
        error_message = bot.send_message(chat_id, text)
        bot.register_next_step_handler(error_message, ask_count_step, params)
        return

    text = 'Из фотографий я могу показать 10 штук. Сколько ты хочешь увидеть?\n' \
           'Если фото не нужны, то просто отправь <code>0</code>'
    sent_message = bot.send_message(chat_id, text)
    bot.register_next_step_handler(sent_message, ask_photos_step, params)


def ask_photos_step(msg: Message, params: REQ_PARAMS_TYPE) -> None:
    """
    Запросить количество фото

    Args:
        msg: обрабатываемое сообщение
        params: параметры запроса
    """
    chat_id = msg.chat.id
    reply = msg.text

    user = msg.from_user
    logger.info(f'Запрос количества фото ({user.username} – {user.id}), ответ: {reply}')

    try:
        params['photos_count'] = int(reply)
    except ValueError:
        text = 'Некорректный ввод: требуется число.'
        error_message = bot.send_message(chat_id, text)
        bot.register_next_step_handler(error_message, ask_photos_step, params)
        return
    if not 0 <= params['photos_count'] <= 10:
        text = 'Некорректный ввод: число должно быть в диапазоне от 0 до 10 включительно.'
        error_message = bot.send_message(chat_id, text)
        bot.register_next_step_handler(error_message, ask_count_step, params)
        return

    show_hotels(params, chat_id)


def show_hotels(req_params: REQ_PARAMS_TYPE, chat_id: int) -> None:
    """
    Показать результаты поиска пользователю

    Args:
        req_params: параметры запроса
        chat_id: идентификатор чата
    """

    status_message = bot.send_message(chat_id, 'Поиск…')
    try:
        logger.info('Отправка поискового запроса отеля')
        search_results = requester.request_by_price(sort_order=req_params['sort_order'],
                                                    destination_id=req_params['destination_id'],
                                                    count=req_params['results_count'])
    except (requests.ConnectionError, requests.Timeout) as e:
        logger.error(f'Ошибка при поисковом запросе отелей: {e}')
        bot.send_message(chat_id, 'Произошла ошибка при соединении с Hotels.com\n'
                                  'Попробуй еще раз.')
        return
    else:
        bot.delete_message(chat_id, status_message.id)
        logger.info('Запрос успешно выполнен')

    if not search_results:
        text = f'По твоему запросу ничего не найдено.\n' \
               f'Попробуй указать другие параметры поиска: /bestdeal'
        bot.send_message(chat_id, text)
        return

    messages = build_messages(search_results, req_params['photos_count'])

    for message in messages:
        try:
            if message['photos'] is not None:
                bot.send_media_group(chat_id=chat_id, media=message['photos'])
            bot.send_message(chat_id=chat_id, text=message['text'], disable_web_page_preview=True)
        except ApiException as e:
            bot.send_message(chat_id, 'Ошибка при отправке сообщения…')
            logger.error(f'Не удалось отправить сообщение (chat: {chat_id}): {e}')
        else:
            logger.info(f'Сообщение с результатами поиска успешно отправлено (chat: {chat_id})')

    command = f'{req_params["sort_order"]}price'
    database.add_to_history(user_id=chat_id, command=command, city=req_params['city'])
