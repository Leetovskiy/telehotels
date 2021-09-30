import re
from typing import Optional


def locale_from_string(string: str) -> Optional[str]:
    """
    Определить локаль текста строки

    :param string: определяемая строка
    :return: "ru_RU" для русского языка; "en_US" для английского языка;
        None, если не удалось определить локаль
    """

    ru_pattern = re.compile(r'[а-я]')
    en_pattern = re.compile(r'[a-z]')
    string = string.lower()

    if ru_pattern.search(string):
        return 'ru_RU'
    if en_pattern.search(string):
        return 'en_US'
    return None
