from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Родитель')],
                                     [KeyboardButton(text='Логопед')]],
                           resize_keyboard=True,
                           input_field_placeholder='Выберите пункт меню...')


parent = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Отметить результат занятий'),
                                       KeyboardButton(text='Пройти диагностику'),
                                       KeyboardButton(text='Полезные видео')],
                                       [KeyboardButton(text='Частые вопросы'),
                                       KeyboardButton(text='Получать напоминания'),
                                       KeyboardButton(text='Связаться с логопедом')],
                                       [KeyboardButton(text='Назад')]],
                            resize_keyboard=True,
                            input_field_placeholder='Выберите пункт меню...')


faq = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Как заниматься?'),
                                    KeyboardButton(text='Не получается заниматься')],
                                    [KeyboardButton(text='Причины нарушения речи'),
                                    KeyboardButton(text='Купить для iOS')],
                                    [KeyboardButton(text='Назад')]],
                        resize_keyboard=True,
                        input_field_placeholder='Выберите пункт меню...')

therapist = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Отметить результат занятий'),
                                          KeyboardButton(text='Обучение'),
                                          KeyboardButton(text='Учреждениям')],
                                          [KeyboardButton(text='Методические рекомендации'),
                                          KeyboardButton(text='Купить для iOS'),
                                          KeyboardButton(text='Вывести на ПК')],
                                          [KeyboardButton(text='Частые вопросы'),
                                          KeyboardButton(text='Связаться с автором')],
                                          [KeyboardButton(text='Назад')]],
                                resize_keyboard=True,
                                input_field_placeholder='Выберите пункт меню...')
