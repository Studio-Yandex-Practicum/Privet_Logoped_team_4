# Описание

Привет, Логопед - чат-бот для увеличения количества продаж через помощь и информирование пользователей.

## Структура директорий проекта

- src - основная папка проекта
  - telegram_bot - папка бота в Телеграм
    - handlers
      - __init__.py - файл с главным роутером aiogram
      - ... - остальные роутеры
    - bot.py - главный файл бота
    - Dockerfile - файл с образом docker
    - requirements.txt - файл с требованиями к библиотекам
    - config.py - читатель конфигурации бота
  - manage.py - программа для управления проектом
  - vk_bot - папка бота в ВК
    - handlers
      - __init__.py - файл с главным роутером vkbottle
      - ... - остальные роутеры
    - bot.py - главный файл бота
    - Dockerfile - файл с образом docker
    - requirements.txt - файл с требованиями к библиотекам
    - config.py - читатель конфигурации бота
  - db - папка базы данных
    - constants.py - константы для базы данных
    - main.py - тест базы данных
    - models.py - модели для базы данных
    - config.py - читатель конфигурации бота
- .env - файл с переменными окружения
- README.md - файл с описанием проекта
- docker-compose.yaml - файл с конфигурацией docker-compose
- requirements.txt - файл с требованиями к библиотекам

## Запуск

1. `cd src/telegram_bot`
   `python -m venv venv`
   Создаём виртуальное окружение для Telegram бота
2. `cd ../vk_bot`
   `python -m venv venv`
   Создаём виртуальное окружение для VK бота
3. `cd ..`
   `cp services/* /etc/systemd/system`
   Копируем systemd-юниты в /etc/systemd/system
4. `sudo systemctl daemon-reload`
   Перезагружаем systemd-юниты
5. `sudo systemctl enable telegram-bot.service`
   Включаем Telegram бота
6. `sudo systemctl enable vk-bot.service`
   Включаем VK бота
7. `sudo systemctl enable docker-compose-db.service`
   Включаем юнит для базы данных
8. `sudo systemctl start telegram-bot.service`
   Запускаем Telegram бота
9. `sudo systemctl start vk-bot.service`
   Запускаем VK бота
10. `sudo systemctl start docker-compose-db.service`
   Запускаем юнит для базы данных

### Пример оформления .env файла

```env
DATABASE_URL = 'postgresql+asyncpg://<username>:<password>@<db_ip_address:127.0.0.1>:<db_port:5433>/hello_speech_therapist'
TG_TOKEN = 'tg_token'
VK_TOKEN = 'vk_token'
POSTGRES_USER = 'postgres'
POSTGRES_PASSWORD = 'root'
POSTGRES_DB = 'postgres'
```

## Договорённости именования веток, стиль кода и т.п

### Правила использования веток

Для каждой задачи создаётся отдельная ветка. После завершения задачи отправляется PR, после ревью ветка мёржится в ветку `dev` и потом удаляется.

### Нейминг веток

Название для ветки с добавлением новых функций будет начинаться на "feature" (пример: `feature/feature-1`)
Ветка с исправлением ошибок будет начинаться на "bug" (пример: `bug/bug-1`)

### Порядок принятия пул-реквестов

После отправки PR происходит ревью кода. Если ревью кода прошло успешно, то ветка сливается в `dev` и удаляется. Иначе, ветка остаётся и дорабатывается, пока ревью кода не пройдёт успешно.

### Коммиты

Все коммиты пишутся на русском языке.
