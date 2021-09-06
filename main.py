import requests
from loguru import logger

import handlers
from loader import bot

if __name__ == '__main__':
    try:
        bot.polling(non_stop=True, interval=1)
    except (requests.ConnectionError, requests.Timeout) as e:
        logger.error(f'Ошибка соединения во время поллинга: {e}')
    finally:
        bot.close()
