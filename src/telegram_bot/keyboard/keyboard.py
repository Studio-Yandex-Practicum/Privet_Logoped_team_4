from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Помощь')],
                                     [KeyboardButton(text='Опрос')],
                                     [KeyboardButton(text='Настройка уведомлений')]],
                           resize_keyboard=True,
                           input_field_placeholder='Выберите пункт меню...')
