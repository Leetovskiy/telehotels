from datetime import date, timedelta
from typing import Optional, Dict, List, Any, Union

import requests
from loguru import logger

from src.utils.locale_from_string import locale_from_string
from .exceptions import UndefinedLocale


class HotelsRequester:
    """
    Класс для работы с запросами в Hotels API
    """

    def __init__(self, api_key: str):
        self.__api_key: str = api_key

    def make_request(self,
                     url: str,
                     params: Dict[str, Any]) -> requests.Response:
        """
        Отправить get-запрос к Hotels.com

        Args:
            url: целевой URL-адрес
            params: параметры запроса

        Returns:
            Объект Response
        """
        headers = {
            'x-rapidapi-host': 'hotels4.p.rapidapi.com',
            'x-rapidapi-key': self.__api_key
        }

        response = requests.get(url, headers=headers, params=params)
        return response

    def request_bestdeal(self,
                         destination_id: str,
                         count: int,
                         min_price: int,
                         max_price: int) -> List[Dict[str, Any]]:
        """
        Сделать запрос на ближайшие к центру отели в определенном диапазоне цен

        Args:
            destination_id: destinationId города
            count: количество отелей в результате
            min_price: мин. значение диапазона цены
            max_price: макс. значение диапазона цены

        Returns:
            Результат запроса в виде списка словарей
        """
        landmark_id = destination_id
        check_in = date.today()
        check_out = check_in + timedelta(days=1)

        url = 'https://hotels4.p.rapidapi.com/properties/list'
        query_params = {'destinationId': destination_id,
                        'pageNumber': '1',
                        'pageSize': count,
                        'checkIn': check_in,
                        'checkOut': check_out,
                        'adults1': '1',
                        'sortOrder': 'DISTANCE_FROM_LANDMARK',
                        'landmarkIds': landmark_id,
                        'priceMin': min_price,
                        'priceMax': max_price,
                        'locale': 'ru_RU',
                        'currency': 'RUB'}

        try:
            response = self.make_request(url, query_params).json()
        except (requests.ConnectionError, requests.Timeout) as e:
            logger.error(f'Ошибка при отправке запроса (bestdeal): {e}')
            raise
        return response['data']['body']['searchResults']['results']

    def request_by_price(self,
                         sort_order: str,
                         destination_id: str,
                         count: int, ) -> List[Dict[str, Any]]:
        """
        Запросить отели города с сортировкой по цене

        Args:
            sort_order: порядок сортировки. "low" – от меньшего к большему; "high" – от большего к меньшему
            destination_id: destinationId города
            count: количество отелей в результате

        Returns:
            Результат запроса в виде списка словарей

        Raises:
            ValueError: если в sort_order передано некорректное значение
        """
        if sort_order not in ('low', 'high'):
            raise ValueError('invalid value, "low" or "high" is expected')

        sort_order = 'PRICE' if sort_order == 'low' else 'PRICE_HIGHEST_FIRST'
        check_in = date.today()
        check_out = check_in + timedelta(days=1)

        url = 'https://hotels4.p.rapidapi.com/properties/list'
        query_params = {'destinationId': destination_id,
                        'sortOrder': sort_order,
                        'pageSize': count,
                        'checkIn': check_in.strftime('%Y-%m-%d'),
                        'checkOut': check_out.strftime('%Y-%m-%d'),
                        'pageNumber': '1',
                        'adults1': '1',
                        'locale': 'ru_RU',
                        'currency': 'RUB'}

        try:
            response = self.make_request(url, query_params).json()
        except requests.RequestException as e:
            logger.error(f'Ошибка при отправке запроса (by_price): {e}')
            raise
        return response['data']['body']['searchResults']['results']

    def request_photos(self, hotel_id: Union[str, int]) -> List[str]:
        """
        Запросить фотографии отеля

        Args:
            hotel_id: идентификатор отеля

        Returns:
            Результат запроса (список с ссылками на изображения)
        """
        url = 'https://hotels4.p.rapidapi.com/properties/get-hotel-photos'
        query_params = {'id': hotel_id}

        try:
            response = self.make_request(url, query_params).json()
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

    def search_destination(self, city_name: str) -> Optional[str]:
        """
        Поиск местоположения в Hotels API по названию города

        Args:
            :param city_name: название города в свободном формате

        Returns:
            destinationId (str) или None, если местоположение не было найдено

        Raises:
            UndefinedLocale: если не удалось определить локаль строки с наименованием города
        """
        locale = locale_from_string(city_name)
        if not locale:
            raise UndefinedLocale('failed to determine locale')

        url = 'https://hotels4.p.rapidapi.com/locations/v2/search'
        query_params = {'query': city_name, 'locale': locale}

        response = self.make_request(url, query_params).json()
        try:
            return response['suggestions'][0]['entities'][0]['destinationId']
        except (KeyError, IndexError):
            return None
