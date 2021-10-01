from typing import Optional

ALLOWED_NAMES = ('lowprice', 'highprice', 'bestdeal')


class UserQuery:
    """
    Класс пользовательского запроса отеля

    Attributes:
        name -- имя пользовательского запроса (lowprice, highprice или bestdeal)
        city -- город поиска
        results_count -- количество результатов для вывода
        photos_count -- количество фото для вывода
        price_range -- диапазон цен для поиска (если требуется)
        distance_range -- диапазон отдаленности от центра для поиска (если требуется)
    """

    def __init__(self,
                 name: str,
                 city: str,
                 results_count: int,
                 photos_count: int,
                 price_range: Optional[str] = None,
                 distance_range: Optional[str] = None) -> None:
        self.name = name
        self.city = city
        self.results_count = results_count
        self.photos_count = photos_count
        if price_range:
            self.price_range = price_range
        if distance_range:
            self.distance_range = distance_range

    def __str__(self) -> str:
        string = f'Запрос {self.name}: {self.city}; кол-во – {self.results_count}; фото – {self.photos_count}'
        return string

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError('name must be a string')

        if value not in ALLOWED_NAMES:
            raise ValueError('name must be one of the allowed values')

        self._name = value

    @property
    def city(self) -> str:
        return self._city

    @city.setter
    def city(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError('city must be a string')

        self._city = value

    @property
    def results_count(self) -> int:
        return self._results_count

    @results_count.setter
    def results_count(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError('results_count must be an integer')

        self._results_count = value

    @property
    def photos_count(self) -> int:
        return self._photos_count

    @photos_count.setter
    def photos_count(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError('photos_count must be an integer')

        self._photos_count = value

    @property
    def price_range(self) -> str:
        return self._price_range

    @price_range.setter
    def price_range(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError('price_range must be a string')

        self._price_range = value

    @property
    def distance_range(self) -> str:
        return self._distance_range

    @distance_range.setter
    def distance_range(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError('distance_range must be a string')

        self._distance_range = value
