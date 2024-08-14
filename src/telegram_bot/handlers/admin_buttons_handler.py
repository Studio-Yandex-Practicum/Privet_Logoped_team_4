from pathlib import Path

import keyboard.keyboard as kb
from aiogram import Bot, F, Router
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from callbacks import (
    ButtonAddCallback,
    ButtonAddFileCallback,
    ButtonAddTypeCallback,
    ButtonChooseRoleCallback,
    ButtonDeleteCallback,
    ButtonGroupCallback,
    ButtonInfoCallback,
    ButtonOnButtonTextCallback,
    ButtonRoleCallback,
    ButtonTextCallback,
    ButtonTypeCallback,
    ButtonInMainMenuCallback
)
from sqlalchemy import select, update

from db.models import Button, ButtonType, RoleType, async_session

from .state import AdminStates

router = Router()


@router.callback_query(ButtonInfoCallback.filter())
async def button_info_handler(
    callback: CallbackQuery, callback_data: ButtonInfoCallback
):
    """Обработка выбора кнопки 'Информация о кнопке'."""
    await callback.answer()
    # await callback.message.delete()

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(Button).where(
                    Button.button_id == callback_data.button_id
                )
            )
            button: Button = result.scalars().first()

    message = await kb.get_button_text_info(button)

    keyboard = await kb.get_button_settings_keyboard(button)
    await callback.message.edit_text(message, reply_markup=keyboard)


@router.callback_query(ButtonDeleteCallback.filter())
async def button_delete_handler(
    callback: CallbackQuery, callback_data: ButtonDeleteCallback
):
    """Обработка выбора кнопки 'Удалить кнопку'."""
    await callback.answer()
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(Button).where(
                    Button.button_id == callback_data.button_id
                )
            )
            button = result.scalars().first()
            await session.delete(button)

    await callback.message.delete()
    await callback.message.answer(
        "Кнопка успешно удалена", reply_markup=kb.admin
    )


@router.callback_query(ButtonOnButtonTextCallback.filter())
async def button_on_text_handler(
    callback: CallbackQuery,
    callback_data: ButtonOnButtonTextCallback,
    state: FSMContext,
):
    """Обработка выбора кнопки 'Удалить кнопку'."""
    await callback.answer()
    await state.set_state(AdminStates.waiting_on_button_text)
    await state.update_data(button_id=callback_data.button_id)

    await callback.message.delete()
    await callback.message.answer(
        "Отправьте текст на кнопке", reply_markup=kb.cancel
    )


@router.callback_query(ButtonTypeCallback.filter())
async def button_type_handler(
    callback: CallbackQuery,
    callback_data: ButtonTypeCallback,
):
    """Обработка выбора кнопки 'Удалить кнопку'."""
    await callback.answer()

    if callback_data.button_type:
        async with async_session() as session:
            async with session.begin():
                result = await session.execute(
                    select(Button).where(
                        Button.button_id == callback_data.button_id
                    )
                )
                button = result.scalars().first()
                button.button_type = callback_data.button_type
                # if callback_data.button_type in [
                #     ButtonType.ADMIN_MESSAGE,
                #     ButtonType.MAILING,
                #     ButtonType.NOTIFICATION,
                # ]:
                #     button.text = ""
        await callback.message.answer(
            "Тип кнопки изменен", reply_markup=kb.admin
        )
        return
    type_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Текст",
                    callback_data=ButtonTypeCallback(
                        button_id=callback_data.button_id,
                        button_type=ButtonType.TEXT,
                    ).pack(),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Файл",
                    callback_data=ButtonTypeCallback(
                        button_id=callback_data.button_id,
                        button_type=ButtonType.FILE,
                    ).pack(),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Группа",
                    callback_data=ButtonTypeCallback(
                        button_id=callback_data.button_id,
                        button_type=ButtonType.GROUP,
                    ).pack(),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Рассылка",
                    callback_data=ButtonTypeCallback(
                        button_id=callback_data.button_id,
                        button_type=ButtonType.MAILING,
                    ).pack(),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Написать админам",
                    callback_data=ButtonTypeCallback(
                        button_id=callback_data.button_id,
                        button_type=ButtonType.ADMIN_MESSAGE,
                    ).pack(),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Настройка уведомлений",
                    callback_data=ButtonTypeCallback(
                        button_id=callback_data.button_id,
                        button_type=ButtonType.NOTIFICATION,
                    ).pack(),
                ),
            ],
        ]
    )
    await callback.message.edit_text("Выберите тип", reply_markup=type_kb)


@router.message(
    F.text == "Отмена", StateFilter(AdminStates.waiting_on_button_text)
)
async def cancel_button_on_text_handler(message: Message, state: FSMContext):
    """Обработка отмены ввода текста на кнопке."""
    await message.answer("Отменено", reply_markup=kb.admin)
    await state.clear()


@router.message(StateFilter(AdminStates.waiting_on_button_text))
async def get_button_on_text(message: Message, state: FSMContext):
    """Обработка ввода текста на кнопке."""
    async with async_session() as session:
        async with session.begin():
            data = await state.get_data()
            result = await session.execute(
                select(Button).where(Button.button_id == data["button_id"])
            )
            button = result.scalars().first()
            button.button_name = message.text

    await message.answer("Текст изменен", reply_markup=kb.admin)
    await state.clear()


@router.callback_query(ButtonTextCallback.filter())
async def button_text_handler(
    callback: CallbackQuery,
    callback_data: ButtonTextCallback,
    state: FSMContext,
):
    """Обработка выбора кнопки 'Изменить текст при нажатии'."""
    await callback.answer()
    await state.set_state(AdminStates.waiting_button_text)
    await state.update_data(button_id=callback_data.button_id)

    await callback.message.delete()
    await callback.message.answer(
        "Отправьте текст при нажатии на кнопку", reply_markup=kb.cancel
    )


@router.message(
    F.text == "Отмена", StateFilter(AdminStates.waiting_button_text)
)
async def cancel_button_text_handler(message: Message, state: FSMContext):
    """Обработка отмены ввода текста при нажатии на кнопку."""
    await message.answer("Отменено", reply_markup=kb.admin)
    await state.clear()


@router.message(StateFilter(AdminStates.waiting_button_text))
async def get_button_text(message: Message, state: FSMContext):
    """Обработка ввода текста при нажатии на кнопку."""
    async with async_session() as session:
        async with session.begin():
            data = await state.get_data()
            result = await session.execute(
                select(Button).where(Button.button_id == data["button_id"])
            )
            button = result.scalars().first()
            button.text = message.text

    await message.answer("Текст изменен", reply_markup=kb.admin)
    await state.clear()


@router.callback_query(ButtonChooseRoleCallback.filter())
async def button_choose_role_handler(
    callback: CallbackQuery, callback_data: ButtonChooseRoleCallback
):
    """Обработка выбора роли."""
    await callback.answer()
    await callback.message.delete()

    await callback.message.answer(
        "Выберите роль",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Родитель",
                        callback_data=ButtonRoleCallback(
                            button_id=callback_data.button_id,
                            button_role=RoleType.PARENT,
                        ).pack(),
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="Логопед",
                        callback_data=ButtonRoleCallback(
                            button_id=callback_data.button_id,
                            button_role=RoleType.SPEECH_THERAPIST,
                        ).pack(),
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="Всем",
                        callback_data=ButtonRoleCallback(
                            button_id=callback_data.button_id,
                            button_role=None,
                        ).pack(),
                    )
                ],
            ]
        ),
    )


@router.callback_query(ButtonRoleCallback.filter())
async def button_role_handler(
    callback: CallbackQuery, callback_data: ButtonRoleCallback
):
    """Обработка выбора роли."""
    await callback.answer()

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(Button).where(
                    Button.button_id == callback_data.button_id
                )
            )
            button = result.scalars().first()
            button.to_role = callback_data.button_role

    await callback.message.delete()
    await callback.message.answer("Роль изменена", reply_markup=kb.admin)


@router.callback_query(ButtonGroupCallback.filter())
async def admin_buttons_handler(
    callback: CallbackQuery, callback_data: ButtonGroupCallback
):
    """Обработка выбора кнопки 'Кнопки'."""
    await callback.answer()
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(Button).where(
                    Button.parent_button_id == callback_data.button_id
                )
            )
            buttons = result.scalars().all()

    btns = []
    for button in buttons:
        btns.append(
            [
                InlineKeyboardButton(
                    text=button.button_name,
                    callback_data=ButtonInfoCallback(
                        button_id=button.button_id
                    ).pack(),
                ),
            ]
        )

    if len(buttons) < 5:
        btns.append(
            [
                InlineKeyboardButton(
                    text="Добавить кнопку",
                    callback_data=ButtonAddCallback(
                        parent_button_id=callback_data.button_id
                    ).pack(),
                )
            ]
        )
    if callback_data.button_id is not None:
        btns.append(
            [
                InlineKeyboardButton(
                    text="Назад",
                    callback_data=ButtonInfoCallback(
                        button_id=callback_data.button_id
                    ).pack(),
                ),
            ]
        )
    else:
        btns.append(
            [
                InlineKeyboardButton(
                    text="Назад",
                    callback_data="admin",
                ),
            ]
        )

    await callback.message.edit_text(
        f"{len(buttons)} кнопок",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=btns),
    )


@router.callback_query(ButtonAddCallback.filter())
async def button_add_handler(
    callback: CallbackQuery, callback_data: ButtonAddCallback
):
    """Обработка выбора кнопки 'Добавить кнопку'."""
    await callback.answer()

    # await callback.message.delete()

    await callback.message.edit_text(
        "Выберите тип кнопки",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Текст",
                        callback_data=ButtonAddTypeCallback(
                            parent_button_id=callback_data.parent_button_id,
                            button_type=ButtonType.TEXT,
                        ).pack(),
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="Файл",
                        callback_data=ButtonAddTypeCallback(
                            parent_button_id=callback_data.parent_button_id,
                            button_type=ButtonType.FILE,
                        ).pack(),
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="Группа",
                        callback_data=ButtonAddTypeCallback(
                            parent_button_id=callback_data.parent_button_id,
                            button_type=ButtonType.GROUP,
                        ).pack(),
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="Рассылка",
                        callback_data=ButtonAddTypeCallback(
                            parent_button_id=callback_data.parent_button_id,
                            button_type=ButtonType.MAILING,
                        ).pack(),
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="Написать админам",
                        callback_data=ButtonAddTypeCallback(
                            parent_button_id=callback_data.parent_button_id,
                            button_type=ButtonType.ADMIN_MESSAGE,
                        ).pack(),
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="Настройка уведомлений",
                        callback_data=ButtonAddTypeCallback(
                            parent_button_id=callback_data.parent_button_id,
                            button_type=ButtonType.NOTIFICATION,
                        ).pack(),
                    ),
                ],
            ]
        ),
    )


@router.callback_query(ButtonAddTypeCallback.filter())
async def button_add_type_handler(
    callback: CallbackQuery,
    callback_data: ButtonAddTypeCallback,
    state: FSMContext,
):
    """Обработка выбора кнопки 'Добавить кнопку'."""
    await callback.answer()

    # await callback.message.delete()

    await callback.message.edit_text(
        "Введите текст на кнопке", reply_markup=kb.cancel
    )
    await state.set_state(AdminStates.waiting_on_button_text_create)
    await state.update_data(
        button_type=callback_data.button_type,
        parent_button_id=callback_data.parent_button_id,
    )


@router.message(
    F.text == "Отмена", StateFilter(AdminStates.waiting_on_button_text_create)
)
async def cancel_on_button_text_create_handler(
    message: Message, state: FSMContext
):
    """Обработка отмены ввода текста при нажатии на кнопку."""
    await message.answer("Отменено", reply_markup=kb.admin)
    await state.clear()


@router.message(StateFilter(AdminStates.waiting_on_button_text_create))
async def get_on_button_text_create(message: Message, state: FSMContext):
    """Обработка ввода текста при нажатии на кнопку."""
    await state.update_data(text=message.text)

    data = await state.get_data()

    if data["button_type"] in [
        ButtonType.TEXT,
        ButtonType.FILE,
        ButtonType.GROUP,
    ]:
        await message.answer(
            "Введите текст при нажатии на кнопку", reply_markup=kb.cancel
        )

        await state.set_state(AdminStates.waiting_button_text_create)
    else:
        async with async_session() as session:
            async with session.begin():
                button = Button(
                    button_name=message.text,
                    parent_button_id=data["parent_button_id"],
                    button_type=data["button_type"],
                    text="",
                    file_path="",
                )
                session.add(button)

        await message.answer("Кнопка добавлена", reply_markup=kb.admin)

        await state.clear()


@router.message(
    StateFilter(AdminStates.waiting_button_text_create), F.text == "Отмена"
)
async def cancel_button_text_create_handler(
    message: Message, state: FSMContext
):
    """Обработка отмены ввода текста при нажатии на кнопку."""
    await message.answer("Отменено", reply_markup=kb.admin)
    await state.clear()


@router.message(StateFilter(AdminStates.waiting_button_text_create))
async def get_button_text_create(message: Message, state: FSMContext):
    """Обработка ввода текста при нажатии на кнопку."""
    await state.update_data(click_text=message.text)

    data = await state.get_data()
    if data["button_type"] == ButtonType.FILE:
        await message.answer("Выберите файл", reply_markup=kb.cancel)
        await state.set_state(AdminStates.waiting_button_file_create)
    else:
        async with async_session() as session:
            async with session.begin():
                button = Button(
                    button_name=data["text"],
                    parent_button_id=data["parent_button_id"],
                    button_type=data["button_type"],
                    text=message.text,
                    file_path="",
                )
                session.add(button)

        await message.answer("Кнопка добавлена", reply_markup=kb.admin)


@router.message(
    StateFilter(AdminStates.waiting_button_file_create), F.document
)
async def get_button_file_create(
    message: Message, state: FSMContext, bot: Bot
):
    """Обработка выбора файла при нажатии на кнопку."""
    dest = (
        Path(__file__).parent.parent.parent.parent
        / "files"
        / (
            message.document.file_id
            + "."
            + message.document.file_name.split(".")[-1]
        )
    )
    await bot.download(message.document.file_id, dest)

    data = await state.get_data()
    async with async_session() as session:
        async with session.begin():
            button = Button(
                button_name=data["text"],
                parent_button_id=data["parent_button_id"],
                button_type=data["button_type"],
                text=data["text"],
                file_path=str(dest),
            )
            session.add(button)

    await message.answer("Кнопка добавлена", reply_markup=kb.admin)


@router.message(
    StateFilter(AdminStates.waiting_button_file_create), F.text == "Отмена"
)
async def cancel_button_file_create_handler(
    message: Message, state: FSMContext
):
    """Обработка отмены выбора файла при нажатии на кнопку."""
    await message.answer("Отменено", reply_markup=kb.admin)
    await state.clear()


@router.message(StateFilter(AdminStates.waiting_button_file_create))
async def get_on_button_file_create(message: Message):
    """Обработка ввода некорректного файла при нажатии на кнопку."""
    await message.answer("Отправлен некорректный файл")


@router.callback_query(ButtonAddFileCallback.filter())
async def button_add_file_callback(
    callback: CallbackQuery,
    callback_data: ButtonAddFileCallback,
    state: FSMContext,
):
    """Обработка выбора кнопки 'Добавить файл'."""
    await callback.answer()
    await state.set_state(AdminStates.waiting_button_file)
    await state.update_data(button_id=callback_data.button_id)

    await callback.message.delete()
    await callback.message.answer("Выберите файл", reply_markup=kb.cancel)


@router.message(
    StateFilter(AdminStates.waiting_button_file), F.document
)
async def get_button_file_edit(message: Message, state: FSMContext, bot: Bot):
    """Обработка выбора файла при нажатии на кнопку."""
    dest = (
        Path(__file__).parent.parent.parent.parent
        / "files"
        / (
            message.document.file_id
            + "."
            + message.document.file_name.split(".")[-1]
        )
    )
    await bot.download(message.document.file_id, dest)

    data = await state.get_data()
    async with async_session() as session:
        async with session.begin():
            await session.execute(
                update(Button).where(Button.button_id == data["button_id"]).values(
                    file_path=str(dest)
                )
            )

    await message.answer("Кнопка обновлена", reply_markup=kb.admin)


@router.message(
    StateFilter(AdminStates.waiting_button_file), F.text == "Отмена"
)
async def cancel_button_file_edit_handler(message: Message, state: FSMContext):
    """Обработка отмены выбора файла при нажатии на кнопку."""
    await message.answer("Отменено", reply_markup=kb.admin)
    await state.clear()


@router.message(StateFilter(AdminStates.waiting_button_file))
async def get_on_button_file_edit(message: Message):
    """Обработка ввода некорректного файла при нажатии на кнопку."""
    await message.answer("Отправлен некорректный файл")


@router.callback_query(ButtonInMainMenuCallback.filter())
async def button_in_main_menu_handler(
    callback: CallbackQuery, callback_data: ButtonInMainMenuCallback
):
    """Обработка выбора кнопки 'В главном меню'."""
    await callback.answer()

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                update(Button).returning(Button).where(
                    Button.button_id == callback_data.button_id
                ).values(
                    is_in_main_menu=not callback_data.is_enabled
                )
            )
            button: Button = result.scalars().first()

    message = await kb.get_button_text_info(button)

    keyboard = await kb.get_button_settings_keyboard(button)
    await callback.message.edit_text(message, reply_markup=keyboard)
