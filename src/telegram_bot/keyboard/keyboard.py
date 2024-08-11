from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

main = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Родитель')],
        [KeyboardButton(text='Логопед')]],
    resize_keyboard=True,
    input_field_placeholder='Выберите пункт меню...'
)

parent = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Отметить результат занятий'),
         KeyboardButton(text='Пройти диагностику'),
         KeyboardButton(text='Полезные видео')],
        [KeyboardButton(text='Частые вопросы'),
         KeyboardButton(text='Получать напоминания'),
         KeyboardButton(text='Связаться с логопедом')],
        [KeyboardButton(text='Изменить роль')]],
    resize_keyboard=True,
    input_field_placeholder='Выберите пункт меню...')

faq = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='Как заниматься?'),
               KeyboardButton(text='Не получается заниматься')],
              [KeyboardButton(text='Причины нарушения речи'),
               KeyboardButton(text='Купить для iOS')],
              [KeyboardButton(text='Назад')]],
    resize_keyboard=True,
    input_field_placeholder='Выберите пункт меню...')

therapist = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='Отметить результат занятий'),
               KeyboardButton(text='Обучение'),
               KeyboardButton(text='Учреждениям')],
              [KeyboardButton(text='Методические рекомендации'),
               KeyboardButton(text='Купить для iOS'),
               KeyboardButton(text='Вывести на ПК')],
              [KeyboardButton(text='Частые вопросы'),
               KeyboardButton(text='Связаться с автором')],
              [KeyboardButton(text='Изменить роль')]],
    resize_keyboard=True,
    input_field_placeholder='Выберите пункт меню...')

admin = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Материалы')],
        [KeyboardButton(text='Промокоды')],
        [KeyboardButton(text='Пользователи')]],
    resize_keyboard=True,
    input_field_placeholder='Выберите пункт меню...'
)

links = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Добавить ссылку')],
        [KeyboardButton(text='Удалить ссылку')],
        [KeyboardButton(text='Загрузить файл')],
        [KeyboardButton(text='Назад')]],
    resize_keyboard=True,
    input_field_placeholder='Выберите пункт меню...'
)

links_types = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Ссылка')],
        [KeyboardButton(text='Путь к файлу')],
        [KeyboardButton(text='Отмена')]],
    resize_keyboard=True,
    input_field_placeholder='Выберите пункт меню...'
)

links_to_role = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Родитель')],
        [KeyboardButton(text='Логопед')],
        [KeyboardButton(text='Общее')],
        [KeyboardButton(text='Отмена')]],
    resize_keyboard=True,
    input_field_placeholder='Выберите пункт меню...'
)

promocodes = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Добавить промокод')],
        [KeyboardButton(text='Удалить промокод')],
        [KeyboardButton(text='Загрузить файл')],
        [KeyboardButton(text='Назад')]],
    resize_keyboard=True,
    input_field_placeholder='Выберите пункт меню...'
)

users = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Заблокировать пользователя')],
        [KeyboardButton(text='Разблокировать пользователя')],
        [KeyboardButton(text='Назад')]],
    resize_keyboard=True,
    input_field_placeholder='Выберите пункт меню...'
)

cancel = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Отмена')]],
    resize_keyboard=True,
    input_field_placeholder='Выберите пункт меню...'
)
