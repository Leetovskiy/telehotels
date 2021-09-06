from datetime import date, timedelta
from typing import Optional, Dict, List, Any

import requests
from loguru import logger

from utils.locale_from_string import locale_from_string
from .exceptions import UndefinedLocale


class HotelsRequester:
    """
    Класс для работы с запросами в Hotels API
    """

    def __init__(self, api_key: str):
        self.__api_key = api_key

    def request_by_price(self,
                         sort_order: str,
                         city: str,
                         count: int, ) -> List[Dict[str, Any]]:
        """
        Запросить отели города с сортировкой по цене

        Возвращает результаты поиска, содержащие информацию об отелях в
        виде списка словарей

        :param sort_order: задает в каком порядке произойдет сортировка:
            'low' – от меньшего к большему;
            'high' – от большего к меньшему.
        :param city: город, в котором будет произведен поиск
        :param count: максимальное количество отелей, которые нужно
            получить
        :except ValueError: выбрасывается, если переданы некорректные
            значения параметров
        """

        if sort_order not in ('low', 'high'):
            raise ValueError('invalid value, "low" or "high" is expected')

        sort_order = 'PRICE' if sort_order == 'low' else 'HIGH_PRICE'
        destination_id = self.__search_destination(city_name=city)
        check_in = date.today()
        check_out = check_in + timedelta(days=1)

        url = "https://hotels4.p.rapidapi.com/properties/list"
        querystring = {"destinationId": destination_id,
                       "sortOrder": sort_order,
                       "pageSize": count,
                       "checkIn": check_in.strftime('%Y-%m-%d'),
                       "checkOut": check_out.strftime('%Y-%m-%d'),
                       "pageNumber": "1",
                       "adults1": "1",
                       "locale": "ru_RU",
                       "currency": "RUB"}
        headers = {
            'x-rapidapi-host': "hotels4.p.rapidapi.com",
            'x-rapidapi-key': self.__api_key
        }

        try:
            response = requests.get(url, headers=headers, params=querystring).json()
        except requests.RequestException as e:
            logger.error(f'Ошибка при отправке запроса: {e}')
            raise
        return response['data']['body']['searchResults']['results']

    def request_photos(self, hotel_id: int) -> List[str]:
        """
        Запросить фотографии отеля

        :param hotel_id: идентификатор отеля
        :return: список ссылок на изображения
        """

        url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
        querystring = {"id": hotel_id}
        headers = {
            'x-rapidapi-host': "hotels4.p.rapidapi.com",
            'x-rapidapi-key': self.__api_key
        }
        try:
            response = requests.get(url, headers=headers, params=querystring).json()
        except requests.RequestException as e:
            logger.error(f'Ошибка во время запроса фотографий: {e}')
            raise

        result = []
        for image in response['hotelImages']:
            image_link = image['baseUrl'].replace('{size}', 'w')
            result.append(image_link)
        for image in response['roomImages']:
            image_link = image['images'][0]['baseUrl'].replace('{size}', 'w')
            result.append(image_link)

        return result

    def __search_destination(self, city_name: str) -> Optional[str]:
        """
        Поиск местоположения в Hotels API по названию города

        :param city_name: название города в свободном формате
        :return: destinationId или None, если местоположение не было
            найдено
        :except UndefinedLocale: выбрасывается, если не удалось
            определить локаль строки с наименованием города
        """

        locale = locale_from_string(city_name)
        if not locale:
            raise UndefinedLocale('failed to determine locale')

        url = "https://hotels4.p.rapidapi.com/locations/search"
        querystring = {"query": city_name, "locale": locale}
        headers = {
            'x-rapidapi-host': "hotels4.p.rapidapi.com",
            'x-rapidapi-key': self.__api_key
        }

        try:
            response = requests.get(url, headers=headers, params=querystring).json()
        except Exception as e:
            logger.error(f'Ошибка во время запроса destination_id: {e}')
            raise
        try:
            return response['suggestions'][0]['entities'][0]['destinationId']
        except (KeyError, IndexError):
            return None
