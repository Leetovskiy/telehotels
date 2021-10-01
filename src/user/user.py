from typing import List

from .query import UserQuery


class User:
    """
    Класс пользователя бота

    Attributes:
        chat_id -- идентификатор чата пользователя
        history -- список пользовательских запросов отелей
    """

    def __init__(self, chat_id: int) -> None:
        self.chat_id = chat_id
        self.history = []

    @property
    def chat_id(self) -> int:
        return self._chat_id

    @chat_id.setter
    def chat_id(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError('chat_id must be an integer')

        self._chat_id = value

    @property
    def history(self) -> List[dict]:
        return self._history

    @history.setter
    def history(self, value: list) -> None:
        if not isinstance(value, list):
            raise TypeError('value must be a list')

        self._history = value

    def append_to_history(self, query: UserQuery) -> None:
        if not isinstance(query, UserQuery):
            raise TypeError('query must be an UserQuery instance')

        self._history.append(query)
