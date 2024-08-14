from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from sqlalchemy.future import select

from .state import NotificationStates, Level
from db.models import TGUser, async_session
import keyboard.keyboard as kb


router = Router()

@router.message(F.text == 'Получать напоминания')
async def notifications(message: Message, state: FSMContext):
    await state.set_state(NotificationStates.notification)
    async with async_session() as session:
            async with session.begin():
                result = await session.execute(select(TGUser).where(TGUser.user_id == message.from_user.id))
                user = result.scalars().first()
                if user.notification_access == False:
                     reply_markup = kb.notifications_off
                else:
                     reply_markup = kb.notifications
    await message.answer('Вы нажали меню "Получать напоминания"\n',
                         reply_markup=reply_markup)

@router.message(F.text == 'Включить уведомления')
async def schedule_daily_notification(message: Message, state: FSMContext):
    await message.answer('Выберите интервал уведомлений:',
                         reply_markup=kb.notifications)

@router.message(F.text == 'Каждый день')
async def schedule_daily_notification(message: Message, state: FSMContext): 
    await state.set_state(NotificationStates.every_day)
    await message.answer('Укажите время в часах, пример: 9, 10, 11')

@router.message(F.text == 'Через день')
async def schedule_every_other_day_notification(message: Message, state: FSMContext):
    await state.set_state(NotificationStates.other_day)
    await message.answer('Укажите время в часах, пример: 9, 10, 11')

@router.message(F.text == 'Выбор пользователя')
async def schedule_user_choice_day_notification(message: Message, state: FSMContext):
    await state.set_state(NotificationStates.day_week_choice)
    await message.answer('Выберите день недели:',
                         reply_markup=kb.days_of_the_week)

@router.message(F.text == 'Выключить уведомления')
async def schedule_stop_notification(message: Message, state: FSMContext):
    async with async_session() as session:
            async with session.begin():
                result = await session.execute(select(TGUser).where(TGUser.user_id == message.chat.id))
                user = result.scalars().first()
                user.notification_access = False
    await message.answer('Уведомления отключены')

@router.message(StateFilter(NotificationStates.day_week_choice))
async def schedule_user_choice_time_notification(message: Message, state: FSMContext):
    current_state = message.text
    async with async_session() as session:
            async with session.begin():
                result = await session.execute(select(TGUser).where(TGUser.user_id == message.chat.id))
                user = result.scalars().first()
                user.notification_day = current_state
    await state.set_state(NotificationStates.user_choice)
    await message.answer('Укажите время в часах, пример: 9, 10, 11')

@router.message(F.text == 'Назад')
async def back_message(message: Message, state: FSMContext):
    """Обработка выбора кнопки 'Назад'."""
    current_state = await state.get_state()
    if current_state == Level.faq or current_state is None:
        key_reply = kb.parent
        await state.set_state(Level.parent)
    if (current_state == Level.parent or
        current_state == Level.therapist or
        current_state == Level.role_chose or
        current_state == NotificationStates.notification or
        current_state == NotificationStates.day_week_choice):
        key_reply = kb.main
        await state.set_state(Level.main)
    if (current_state == NotificationStates.every_day or
        current_state == NotificationStates.other_day or
        current_state == NotificationStates.user_choice or
        current_state == NotificationStates.stop_notification):
        key_reply = kb.notifications
        await state.set_state(NotificationStates.notification)
    await message.answer(
        'Вы нажали меню "Назад"', reply_markup=key_reply
    )

@router.message(StateFilter(NotificationStates.user_choice,
                            NotificationStates.every_day,
                            NotificationStates.other_day))
async def set_notification_time(message: Message, state: FSMContext):
    chat_id = message.chat.id
    time = message.text
    current_state = await state.get_state()
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(TGUser).where(TGUser.user_id == chat_id))
            user = result.scalars().first()
            if time.isdigit():
                time = int(time)
                user.notificate_at = time
                user.notification_interval = current_state[19:]
                user.notification_access = True
                await message.answer(f'Уведомление обновлено на {time} часов.')
            else:
                await message.answer('Указан неправильный формат времени. Пожалуйста, введите число.')
    await state.set_state(NotificationStates.notification)
    