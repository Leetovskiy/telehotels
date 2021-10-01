from functools import wraps
from time import sleep
from typing import Callable


def sleep_before_call(func: Callable, sleep_time) -> Callable:
    """
    Вызвать sleep перед выполнением функции

    :param func: Декорируемая функция
    :param sleep_time: Время для ожидания в секундах
    :return: Декорированная функция
    """

    @wraps(func)
    def decorated(*args, **kwargs):
        sleep(sleep_time)
        result = func(*args, **kwargs)
        return result

    return decorated
