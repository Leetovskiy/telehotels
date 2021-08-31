import handlers
from loader import bot

if __name__ == '__main__':
    bot.polling(non_stop=True, interval=1)
