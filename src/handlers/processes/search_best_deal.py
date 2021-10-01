import re
from typing import Dict, Union, List

import requests
from loguru import logger
from telebot.apihelper import ApiException
from telebot.types import Message, InputMediaPhoto

from src import utils
from src.loader import bot, requester, users
from src.user import User, UserQuery

REQ_PARAMS_TYPE = Dict[str, Union[str, int]]
BUILT_MESSAGES_TYPE = List[Dict[str, Union[str, List[InputMediaPhoto]]]]


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
    params['city'] = reply

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
    if not (0 <= min_price < max_price):
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
    if not (0 <= min_dist < max_dist):
        text = 'Ошибка: некорректный ввод диапазона.\n' \
               'Минимальное значение должно быть меньше максимального, ' \
               'значение не может быть отрицательным'
        error_message = bot.send_message(chat_id, text)
        bot.register_next_step_handler(error_message, ask_price_range_step, params)
        return

    params['min_dist'] = min_dist
    params['max_dist'] = max_dist

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
        logger.info(f'Отправка поискового запроса отеля для {chat_id}')
        search_results = requester.request_bestdeal(destination_id=req_params['destination_id'],
                                                    count=req_params['results_count'],
                                                    min_price=req_params['min_price'],
                                                    max_price=req_params['max_price'])
    except (ConnectionError, TimeoutError) as e:
        logger.error(f'Ошибка при поисковом запросе отелей: {e}')
        bot.send_message(chat_id, 'Произошла ошибка при соединении с Hotels.com\n'
                                  'Попробуй еще раз.')
        return
    else:
        logger.info(f'Запрос для {chat_id} успешно выполнен')
    finally:
        bot.delete_message(chat_id, status_message.id)

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

    user_query = UserQuery(
        name='bestdeal',
        city=req_params['city'],
        results_count=req_params['results_count'],
        photos_count=req_params['photos_count'],
        price_range=f'{req_params["min_price"]}-{req_params["max_price"]}',
        distance_range=f'{req_params["min_dist"]}-{req_params["min_dist"]}'
    )
    if chat_id not in users:
        users[chat_id] = User(chat_id)
    users[chat_id].append_to_history(user_query)


def build_messages(response: dict,
                   photos_count: int) -> BUILT_MESSAGES_TYPE:
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
