import sqlite3
from typing import Optional, List, Any


class Database:
    """
    Интерфейс взаимодействия с базой данных

    Args:
        database_path (str): относительный путь к файлу базы данных
    """

    def __init__(self, database_path: str = 'main.db'):
        """Конструктор класса"""
        self.database_path: str = database_path

    @property
    def __connection(self) -> sqlite3.Connection:
        """
        Открыть и вернуть соединение с базой данных SQLite

        Returns:
            Объект Connection
        """
        return sqlite3.connect(self.database_path)

    def execute(self,
                sql_command: str,
                parameters: Optional[tuple] = None,
                is_commit: bool = False,
                fetchone: Optional[bool] = False,
                fetchall: Optional[bool] = False) -> Optional[List[Any]]:
        """
        Выполнить SQL-команду

        Args:
            sql_command: строка SQL-команды
            parameters: параметры для подстановки в команду
            is_commit: зафиксировать ли изменения в БД
            fetchone: вернуть один результат выполнения команды
            fetchall: вернуть все результаты выполнения команды
        """
        connection = self.__connection
        cursor = connection.cursor()
        data = None

        if parameters:
            cursor.execute(sql_command, parameters)
        else:
            cursor.execute(sql_command)

        if is_commit:
            connection.commit()

        if fetchone:
            data = cursor.fetchone()
        elif fetchall:
            data = cursor.fetchall()
        connection.close()

        return data

    def __select_from(self, table_name: str, parameters: Optional[dict] = None) -> List[Any]:
        """
        Получить выборку из таблицы по заданным параметрам

        Args:
            table_name: имя целевой таблицы в БД
            parameters: параметры выборки в виде списка кортежей
        """
        if not parameters:
            sql = f'SELECT * FROM {table_name}'
        else:
            sql = f'SELECT * FROM {table_name} WHERE'
            sql = ' '.join((sql, reformat_parameters(parameters)))

        results = self.execute(sql, fetchall=True)
        return results

    def create_users_table(self) -> None:
        """Создать таблицу пользователей"""
        sql = 'CREATE TABLE IF NOT EXISTS users (' \
              'id int NOT NULL PRIMARY KEY,' \
              'username varchar(255) NOT NULL' \
              ')'
        self.execute(sql, is_commit=True)

    def add_user(self, user_id: int, username: str) -> None:
        """Добавить пользователя в таблицу users"""
        sql = 'INSERT or REPLACE INTO users (id, username) ' \
              'VALUES (?, ?)'
        parameters = (user_id, username)
        self.execute(sql_command=sql, parameters=parameters, is_commit=True)

    def select_from_users(self, **parameters) -> List[dict]:
        """
        Получить выборку из таблицы users по заданным параметрам

        Args:
            parameters: параметры для подстановки в SQL-команду

        Returns:
            Список элементов в виде словарей
        """
        data = self.__select_from(table_name='users', parameters=parameters)
        data = [{'id': elem[0], 'username': elem[1]}
                for elem in data]
        return data

    def create_history_table(self) -> None:
        """Создать таблицу истории поисковых запросов"""
        sql = 'CREATE TABLE IF NOT EXISTS history (' \
              'id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,' \
              'user_id int NOT NULL,' \
              'command varchar(255) NOT NULL,' \
              'city varchar(255) NOT NULL' \
              ')'
        self.execute(sql, is_commit=True)

    def add_to_history(self, user_id: int, command: str, city: str) -> None:
        """
        Добавить элемент в историю поисковых запросов

        Args:
            user_id: id Telegram-пользователя, который выполнил запрос
            command: поисковая команда, выполненная пользователем
            city: город поискового запроса
        """
        valid_commands = ('lowprice', 'highprice', 'bestdeal')
        if command not in valid_commands:
            raise ValueError('invalid value')
        if not (isinstance(user_id, int) and isinstance(command, str) and isinstance(city, str)):
            raise TypeError('one or more parameters has invalid type')

        sql = 'INSERT INTO history (user_id, command, city)' \
              'VALUES (?, ?, ?)'
        parameters = (user_id, command, city)
        self.execute(sql_command=sql, parameters=parameters, is_commit=True)

    def select_from_history(self, **parameters) -> List[dict]:
        """
        Получить выборку из таблицы history по заданным параметрам

        Args:
            parameters: параметры для выборки в виде словаря

        Returns:
            Список элементов в виде словарей
        """
        data = self.__select_from(table_name='history', parameters=parameters)
        data = [{'id': elem[0], 'user_id': elem[1], 'command': elem[2], 'city': elem[3]}
                for elem in data]

        return data


def reformat_parameters(parameters: dict) -> str:
    """
    Переформатировать параметры из словаря в строку

    Пример преобразования:
    {'id': 1, 'city': 'Москва'} --> 'id="1" AND city="Москва"'

    Args:
        parameters: параметры для преобразования в виде словаря

    Returns:
        Строка для подстановки в SQL-команду
    """
    if not isinstance(parameters, dict):
        raise TypeError('parameter has an invalid type, dict expected')

    str_params = (f'{param}="{value}"' for param, value in parameters.items())
    result = ' AND '.join(str_params)
    return result
