from loguru import logger
from requests import ConnectionError, Timeout

import src.handlers
from src.loader import bot

if __name__ == '__main__':
    try:
        bot.polling(non_stop=True, interval=1)
    except (ConnectionError, Timeout) as e:
        logger.error(f'Ошибка соединения во время поллинга: {e}')
    finally:
        bot.close()
