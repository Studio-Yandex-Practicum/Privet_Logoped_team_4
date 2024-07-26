from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

import keyboard.keyboard as kb

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Здравствуйте! '
                         'Вас приветствует бот "Привет, Логопед"',
                         reply_markup=kb.main)


@router.message(F.text == 'Помощь')
async def help_message(message: Message):
    await message.answer('Здравствуйте! Вы нажали меню "Помощь"')


@router.message(F.text == 'Опрос')
async def survey_message(message: Message):
    await message.reply('Здравствуйте! Вы нажали меню "Опрос"')


@router.message(F.text == 'Настройка уведомлений')
async def notifications(message: Message):
    await message.answer('Здравствуйте! Вы нажали меню "Настройка уведомлений"')
