import os
import sys

from keyboards.keyboards import (admin_keyboard, admin_promocodes_keyboard,
                                 cancel_keyboard)
from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert
from vkbottle import CtxStorage

parent_folder_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../..')
)
sys.path.append(parent_folder_path)
from db.models import PromoCode, async_session  # noqa

ctx_storage = CtxStorage()


async def get_promocode(bot, message, AdminStates):
    if message.text.lower() == 'отмена':
        await message.answer(
            'Отмена добавления промокода.', keyboard=admin_promocodes_keyboard
        )
        await bot.state_dispenser.set(
                    message.peer_id, AdminStates.PROMOCODES_STATE)
    else:
        await message.answer(
            'Введите путь к файлу:', keyboard=cancel_keyboard
        )
        await bot.state_dispenser.set(
                    message.peer_id, AdminStates.WAITING_PROMOCODE_FILEPATH)
        ctx_storage.set('promocode', message.text)


async def add_promocode(bot, message, AdminStates):
    if message.text.lower() == 'отмена':
        await message.answer(
            'Отмена добавления промокода.', keyboard=admin_promocodes_keyboard
        )
        await bot.state_dispenser.set(
                    message.peer_id, AdminStates.PROMOCODES_STATE)
    else:
        promocode = ctx_storage.get('promocode')
        file_path = message.text
        try:
            async with async_session() as session:
                new_promocode = insert(PromoCode).values(
                    promocode=promocode, file_path=file_path
                )
                await session.execute(new_promocode)
                await session.commit()
        except Exception:
            await message.answer('Попробуйте еще раз.')
        else:
            await message.answer(
                f'Промокод {promocode} успешно добавлен.',
                keyboard=admin_promocodes_keyboard
            )
        finally:
            await bot.state_dispenser.set(
                        message.peer_id, AdminStates.PROMOCODES_STATE)


async def delete_promocode_handler(bot, message, AdminStates):
    if message.text.lower() == 'отмена':
        await message.answer(
            'Отмена удаления промокода.', keyboard=admin_promocodes_keyboard
        )
        await bot.state_dispenser.set(
                    message.peer_id, AdminStates.PROMOCODES_STATE)
    else:
        try:
            promocode_id = int(message.text)
        except ValueError:
            await message.answer(
                'Введены некорректные данные. Пожалуйста, повторите попытку.',
                keyboard=admin_promocodes_keyboard
            )
            await bot.state_dispenser.set(
                        message.peer_id, AdminStates.PROMOCODES_STATE)
        else:
            try:
                async with async_session() as session:
                    delete_promocode = delete(PromoCode).where(
                        PromoCode.promocode_id == promocode_id
                    )
                    await session.execute(delete_promocode)
                    await session.commit()
            except Exception:
                await message.answer('Попробуйте еще раз.')
            else:
                await message.answer(
                    'Промокод успешно удален.',
                    keyboard=admin_promocodes_keyboard
                )
        finally:
            await bot.state_dispenser.set(
                        message.peer_id, AdminStates.PROMOCODES_STATE)


async def admin_promocodes_handler(bot, message, AdminStates):
    if message.text.lower() == 'добавить новый промокод':
        await message.answer('Введите промокод:', keyboard=cancel_keyboard)
        await bot.state_dispenser.set(
                message.peer_id, AdminStates.WAITING_PROMOCODE)
    elif message.text.lower() == 'удалить промокод':
        await message.answer('Введите id промокода:', keyboard=cancel_keyboard)
        await bot.state_dispenser.set(
                message.peer_id, AdminStates.DELETE_PROMOCODE)
    elif message.text.lower() == 'загрузить файл':
        await message.answer(
            'Прикрепите файл для загрузки.', keyboard=cancel_keyboard
        )
        await bot.state_dispenser.set(
                message.peer_id, AdminStates.UPLOAD_PROMOCODE_FILE)
    elif message.text.lower() == 'назад':
        await message.answer('Вы выбрали Назад.',
                             keyboard=admin_keyboard)
        await bot.state_dispenser.set(
                message.peer_id, AdminStates.ADMIN_STATE)
    else:
        await message.answer(
            'Пожалуйста, выберите одну из предложенных опций:',
            keyboard=admin_promocodes_keyboard)
