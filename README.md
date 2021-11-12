# <p align="center">TeleHotels Bot</p>

<p align="center">
  Реализация Telegram-бота для поиска отелей, использующий API
  сервиса <a href="https://hotels.com/">Hotels.com</a> <br>
  Implementation of Telegram-bot for hotel search using
  <a href="https://hotels.com/">Hotels.com</a> API
</p>

<p align="right">
<i>Проект был создан в образовательных целях.</i> <br>
<i>The project was created for educational purposes.</i>
</p>

---
## Содержание / Contents

**На русском:**
1. [Установка и запуск](#Установка-и-запуск)
2. [Запуск с Webhook и Ngrok](#Запуск-с-Webhook-и-Ngrok)

**In English:**
1. [Installing and launch](#Installing-and-launch)
2. [Using Webhook through Ngrok](#Using-Webhook-through-Ngrok)

---

## Установка и запуск

- Клонируйте репозиторий:
```shell
git clone https://github.com/Leetovskiy/telehotels.git
```

- Установите зависимости из файла `Pipfile.lock` с помощью `pipenv`
([инструкции по установке pipenv](https://github.com/pypa/pipenv#installation)):
```shell
pipenv install
```

- Переименуйте файл `.env.example` в `.env` и задайте в нем следующие переменные:
  - `TG_BOT_TOKEN` – токен Telegram-бота;
  - `RAPID_API_KEY` – ключ для доступа к [Rapid API](https://rapidapi.com/);
  - `DATABASE_PATH` (необ.) – относительный путь к файлу базы данных SQLite
  (по умолчанию равен текущей директории).

- Запустите файл `main.py` из виртуального окружения Pipenv:
```shell
pipenv run python main.py
```


## Запуск с Webhook и Ngrok

По умолчанию бот использует polling-метод для получения обновлений с серверов 
Telegram. Так как polling создаёт лишнюю нагрузку на сеть, рекомендуется 
использовать Webhook. Ниже приведена инструкция для запуска бота в режиме
Webhook на локальном устройстве с помощью [Ngrok](https://ngrok.com/).

- Запустите Ngrok-туннель на порт 8443:
```shell
./ngrok http 8443
```

- Скопируйте имя хоста (без `https://`) из строки "Forwarding" и
поместите его в переменную `WEBHOOK_HOST` файла `.env`

- Запустите бота с параметром `--webhook`:
```shell
pipenv run python main.py --webhook
```

---

## Installing and launch

- Clone repository anywhere you want:
```shell
git clone https://github.com/Leetovskiy/telehotels.git
```

- Install requirements from `Pipfile.lock` via `pipenv`
([Pipenv installation instruction](https://github.com/pypa/pipenv#installation))
```shell
pipenv install
```

- Rename `.env.example` to `.env` and specify these variables:
  - `TG_BOT_TOKEN` – Telegram-bot token;
  - `RAPID_API_KEY` – [Rapid API](https://rapidapi.com/) access key;
  - `DATABASE_PATH` (optional) – relative path to SQLite database.

- Run `main.py` via Pipenv virtual environment:
```shell
pipenv run python main.py
```


## Using Webhook through Ngrok

By default, the bot uses the polling method to get updates from the  Telegram
servers. Since polling creates unnecessary load on the network, it is
recommended to use Webhook. Here are the instructions for running the bot in
Webhook mode on your local device using [Ngrok](https://ngrok.com/).

- Run Ngrok and set up tunnel to 8443 port:
```shell
./ngrok http 8443
```

- Copy the hostname (exclude `https://` part) from "Forwarding" row and put this 
to `WEBHOOK_HOST` variable in the `.env` file

- Run the bot with the `webhook` parameter:
```shell
pipenv run python main.py --webhook
```