from typing import Dict, Union, Optional, List

import requests
from loguru import logger
from telebot.types import Message, InputMediaPhoto

import utils
from loader import bot
from loader import requester

REQ_PARAMS_TYPE = Dict[str, Union[str, int]]
BUILT_MESSAGES_TYPE = List[Dict[str, Union[str, List[InputMediaPhoto]]]]


def ask_city_step(msg: Message, params: REQ_PARAMS_TYPE) -> None:
    """
    Запросить город поиска у пользователя

    :param msg: обрабатываемое сообщение
    :param params: параметры, которые будут переданы в функцию запроса
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

    text = 'Я могу вывести до 5-ти отелей. Сколько ты хочешь увидеть?'
    sent_message = bot.send_message(chat_id, text)
    bot.register_next_step_handler(sent_message, ask_count_step, params)


def ask_count_step(msg: Message, params: REQ_PARAMS_TYPE) -> None:
    """
    Запросить количество отелей для поиска

    :param msg: обрабатываемое сообщение
    :param params: параметры, которые будут переданы в функцию запроса
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

    :param msg: обрабатываемое сообщение
    :param params: параметры для поискового запроса
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

    :param req_params: параметры запроса
    :param chat_id: идентификатор чата
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
    messages = build_messages(search_results, req_params['photos_count'])

    for message in messages:
        try:
            status_message = bot.send_message(chat_id, 'Ожидайте…')
            if message['photos'] is not None:
                bot.send_media_group(chat_id=chat_id, media=message['photos'])
            bot.send_message(chat_id=chat_id, text=message['text'], disable_web_page_preview=True)
            bot.delete_message(chat_id, status_message.id)
        except requests.RequestException as e:
            bot.send_message(chat_id, 'Ошибка при отправке сообщения…')
            logger.error(f'Не удалось отправить сообщение (chat: {chat_id})')
        else:
            logger.info(f'Сообщение с результатами поиска успешно отправлено (chat: {chat_id})')


def build_messages(response: dict,
                   photos_count: Optional[int]) -> BUILT_MESSAGES_TYPE:
    """
    Собрать сообщения из результатов запроса поиска отелей

    Принимает ответ запроса поиска отелей и количество фото (если
    требуется), формирует из них список словарей с текстом и
    списком InputMediaPhoto для отправки.

    :param response: результат запроса к API
    :param photos_count: количество фото, прикрепляемых к сообщению,
        если требуется
    :return: список словарей, содержащих текст сообщения и список
        InputMediaPhoto, если фото требуются
    """

    messages = []
    for elem in response:
        name = elem['name']
        address = ', '.join((elem['address']['streetAddress'],
                             elem['address']['locality'],
                             elem['address']['countryName']))
        price = elem['ratePlan']['price']['current']
        for landmark in elem['landmarks']:
            if landmark['label'] in ('Центр города', 'City center'):
                center_remoteness = landmark['distance']
                break
        else:
            center_remoteness = 'не найдено'
        link = f'https://ru.hotels.com/ho{elem["id"]}'

        message_text = '\n'.join((
            f'<b>{name}</b>',
            f'🏢 <b>Адрес:</b> {address}',
            f'🎯 <b>От центра города:</b> {center_remoteness}',
            f'💲 <b>Цена:</b> {price}/сутки',
            f'🔗 <a href="{link}">Больше информации на сайте</a>'
        ))

        photos = None
        if photos_count:
            try:
                logger.info('Отправка запроса фотографий')
                photo_results = requester.request_photos(elem['id'])
            except (requests.ConnectionError, requests.Timeout) as e:
                logger.error(f'Ошибка при запросе фотографий: {e}')
                continue
            else:
                logger.info('Запрос успешно выполнен')

            if len(photo_results) > photos_count:
                photo_results = photo_results[:photos_count]

            photos = [InputMediaPhoto(media=link, caption=name)
                      for link in photo_results]

        messages.append({'text': message_text, 'photos': photos})
    return messages
