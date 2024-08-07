import os
import sys

import keyboard.keyboard as kb
from aiogram import F, Router, Bot
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from sqlalchemy import delete, select
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from pathlib import Path

from .state import AdminStates
from callbacks import PromocodeItemDeleteCallback, PromocodeDeleteCallback

parent_folder_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)
sys.path.append(parent_folder_path)

from db.models import PromoCode, async_session  # noqa

router = Router()


@router.callback_query(F.data == "add_promocode")
async def admin_add_promocode(query: CallbackQuery, state: FSMContext):
    """Обработка выбора кнопки 'Добавить промокод'."""
    await query.message.delete()
    await query.message.answer("Введите промокод:", reply_markup=kb.cancel)
    await state.set_state(AdminStates.waiting_promocode)


@router.message(StateFilter(AdminStates.waiting_promocode))
async def get_promocode(message: Message, state: FSMContext):
    """Обработка ввода промокода."""
    if message.text == "Отмена":
        await message.answer(
            "Отмена добавления промокода.", reply_markup=kb.promocodes
        )
        await state.clear()
    else:
        await state.update_data(waiting_promocode=message.text)
        await message.answer("Отправьте файл:", reply_markup=kb.cancel)
        await state.set_state(AdminStates.waiting_promocode_filepath)


@router.message(
    StateFilter(AdminStates.waiting_promocode_filepath), F.document
)
async def add_promocode(message: Message, state: FSMContext, bot: Bot):
    """Обработка отправки файла промокода и добавление записи в бд."""
    if message.text == "Отмена":
        await message.answer(
            "Отмена добавления промокода.", reply_markup=kb.promocodes
        )
        await state.set_state(AdminStates.promocodes)
    else:
        dest = (
            Path(__file__).parent.parent.parent.parent
            / "files"
            / (
                message.document.file_id
                + "."
                + message.document.file_name.split(".")[-1]
            )
        )
        await bot.download(
            message.document,
            destination=dest,
        )
        data = await state.get_data()
        promocode = data["waiting_promocode"]
        file_path = dest

        try:
            async with async_session() as session:
                new_promocode = insert(PromoCode).values(
                    promocode=promocode, file_path=str(file_path.absolute())
                )
                await session.execute(new_promocode)
                await session.commit()
        except Exception as e:
            print(e)
            await message.answer("Попробуйте еще раз.")
        else:
            await message.answer(
                f"Промокод {promocode} успешно добавлен.",
                reply_markup=kb.promocodes,
            )
        finally:
            await state.clear()


@router.message(StateFilter(AdminStates.waiting_promocode_filepath))
async def add_promocode_incorrect(
    message: Message, state: FSMContext, bot: Bot
):
    """Обработка неправильной отправки файла промокода и добавление записи в бд."""
    if message.text == "Отмена":
        await message.answer("Отменено", reply_markup=kb.promocodes)
        await state.clear()
    else:
        await message.answer("Отправлен некорректный файл.")


# @router.message(F.text == "Удалить промокод")
@router.callback_query(PromocodeDeleteCallback.filter())
async def admin_delete_promocode(
    query: CallbackQuery,
    state: FSMContext,
    callback_data: PromocodeDeleteCallback,
):
    """Обработка выбора кнопки 'Удалить промокод'."""
    keyboard_list = []
    PAGE_SIZE = 5
    async with async_session() as session:
        promocodes = await session.execute(
            select(PromoCode)
            .offset(callback_data.page * PAGE_SIZE)
            .limit(PAGE_SIZE)
        )
        promocodes = promocodes.scalars().all()
        count = await session.execute(
            select(func.count()).select_from(PromoCode)
        )
        count = count.scalar()
    for promocode in promocodes:
        keyboard_list.append(
            [
                InlineKeyboardButton(
                    text=promocode.promocode,
                    callback_data=PromocodeItemDeleteCallback(
                        promocode_id=promocode.promocode_id
                    ).pack(),
                )
            ]
        )

    keyboard_list.append(
        [InlineKeyboardButton(text="Назад", callback_data="admin")]
    )
    pagination = []
    if callback_data.page > 0:
        pagination.append(
            InlineKeyboardButton(
                text="<",
                callback_data=PromocodeDeleteCallback(
                    page=callback_data.page - 1
                ).pack(),
            )
        )
    if count > (callback_data.page + 1) * PAGE_SIZE:
        pagination.append(
            InlineKeyboardButton(
                text=">",
                callback_data=PromocodeDeleteCallback(
                    page=callback_data.page + 1
                ).pack(),
            )
        )

    keyboard_list.append(pagination)
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_list)
    await query.message.edit_text("Выберите промокод:", reply_markup=keyboard)


@router.callback_query(PromocodeItemDeleteCallback.filter())
async def delete_promocode(
    message: CallbackQuery,
    state: FSMContext,
    callback_data: PromocodeItemDeleteCallback,
):
    """
    Обработка ввода id промокода и удаление записи из бд.
    """
    try:
        async with async_session() as session:
            delete_promocode = delete(PromoCode).where(
                PromoCode.promocode_id == callback_data.promocode_id
            )
            await session.execute(delete_promocode)
            await session.commit()
    except Exception:
        await message.answer("Попробуйте еще раз")
    else:
        await message.answer("Промокод успешно удален")
        await message.message.edit_text(
            "Управление промокодами", reply_markup=kb.promocodes
        )
    finally:
        await state.clear()
