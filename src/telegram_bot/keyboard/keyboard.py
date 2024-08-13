from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
import callbacks as cb
from typing import Optional
import sys
import os
from sqlalchemy import and_, select, or_

grand_parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(grand_parent_dir)
from db.models import RoleType, async_session, Button, ButtonType  # noqa

main = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Родитель")],
        [KeyboardButton(text="Логопед")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите пункт меню...",
)

parent = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Отметить результат занятий"),
            KeyboardButton(text="Пройти диагностику"),
            KeyboardButton(text="Полезные видео"),
        ],
        [
            KeyboardButton(text="Частые вопросы"),
            KeyboardButton(text="Получать напоминания"),
            KeyboardButton(text="Связаться с логопедом"),
        ],
        [KeyboardButton(text="Изменить роль")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите пункт меню...",
)

faq = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Как заниматься?"),
            KeyboardButton(text="Не получается заниматься"),
        ],
        [
            KeyboardButton(text="Причины нарушения речи"),
            KeyboardButton(text="Купить для iOS"),
        ],
        [KeyboardButton(text="Назад")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите пункт меню...",
)

therapist = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Отметить результат занятий"),
            KeyboardButton(text="Обучение"),
            KeyboardButton(text="Учреждениям"),
        ],
        [
            KeyboardButton(text="Методические рекомендации"),
            KeyboardButton(text="Купить для iOS"),
            KeyboardButton(text="Вывести на ПК"),
        ],
        [
            KeyboardButton(text="Частые вопросы"),
            KeyboardButton(text="Связаться с автором"),
        ],
        [KeyboardButton(text="Изменить роль")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите пункт меню...",
)

admin = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Промокоды", callback_data="promocodes"),
            InlineKeyboardButton(
                text="Кнопки",
                callback_data=cb.ButtonGroupCallback(button_id=None).pack(),
            ),
        ],
    ],
)

promocodes = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Добавить промокод", callback_data="add_promocode"
            )
        ],
        [
            InlineKeyboardButton(
                text="Удалить промокод",
                callback_data=cb.PromocodeDeleteCallback().pack(),
            )
        ],
        [InlineKeyboardButton(text="Назад", callback_data="admin")],
    ],
)

cancel = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Отмена")]],
    resize_keyboard=True,
    input_field_placeholder="Выберите пункт меню...",
)

role = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Родитель", callback_data="parent")],
        [InlineKeyboardButton(text="Логопед", callback_data="therapist")],
        [InlineKeyboardButton(text="Информация", callback_data="info")],
    ],
)


async def get_start_keyboard(
    role: Optional[RoleType], parent_button_id: Optional[int] = None
) -> InlineKeyboardMarkup:
    async with async_session() as session:
        if role is None:
            result = await session.execute(
                select(Button).where(
                    Button.is_in_main_menu,
                )
            )
            buttons = result.scalars().all()
        else:
            result = await session.execute(
                select(Button).where(
                    and_(
                        Button.parent_button_id == parent_button_id,
                        or_(Button.to_role == role, Button.to_role.is_(None)),
                    )
                )
            )
            buttons = result.scalars().all()

    buttons = [
        [
            InlineKeyboardButton(
                text=button.button_name,
                callback_data=cb.VisitButtonCallback(
                    button_id=button.button_id, authorized=role is not None
                ).pack(),
            )
        ]
        for button in buttons
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def get_button_text_info(button: Button):
    message = f"Текст на кнопке: {button.button_name}\n"
    if button.button_type in [
        ButtonType.FILE,
        ButtonType.GROUP,
        ButtonType.TEXT,
    ]:
        message += f"Текст при нажатии: {button.text}\n"

    if button.button_type == ButtonType.FILE:
        message += "Кнопка отправит файл\n"

    if button.button_type == ButtonType.GROUP:
        message += "Кнопка отправит вложенное меню\n"

    if button.button_type == ButtonType.MAILING:
        message += "Кнопка для управления рассылкой\n"

    if button.button_type == ButtonType.ADMIN_MESSAGE:
        message += "Кнопка для связи с админом\n"

    if button.to_role is not None:
        message += f'Кнопка для {"родителей" if button.to_role == RoleType.PARENT else "логопедов"}\n'
    else:
        message += "Кнопка для всех пользователей\n"

    return message


async def get_button_settings_keyboard(button: Button):
    buttons = []
    # buttons.append(
    #     [
    #         InlineKeyboardButton(
    #             text="Изменить тип кнопки",
    #             callback_data=ButtonTypeCallback(
    #                 button_id=button.button_id,
    #             ).pack(),
    #         ),
    #     ],
    # )
    buttons.append(
        [
            InlineKeyboardButton(
                text="Изменить текст на кнопке",
                callback_data=cb.ButtonOnButtonTextCallback(
                    button_id=button.button_id
                ).pack(),
            ),
        ],
    )
    buttons.append(
        [
            InlineKeyboardButton(
                text=f'Показывать при входе: {"✅" if button.is_in_main_menu else "❌"}',
                callback_data=cb.ButtonInMainMenuCallback(
                    button_id=button.button_id,
                    is_enabled=button.is_in_main_menu,
                ).pack(),
            ),
        ],
    )
    if button.button_type in [
        ButtonType.FILE,
        ButtonType.GROUP,
        ButtonType.TEXT,
    ]:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Изменить текст при нажатии",
                    callback_data=cb.ButtonTextCallback(
                        button_id=button.button_id
                    ).pack(),
                ),
            ]
        )

    if button.button_type == ButtonType.FILE:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Изменить файл",
                    callback_data=cb.ButtonAddFileCallback(
                        button_id=button.button_id
                    ).pack(),
                ),
            ]
        )
    if button.button_type == ButtonType.GROUP:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Изменить вложенное меню",
                    callback_data=cb.ButtonGroupCallback(
                        button_id=button.button_id
                    ).pack(),
                )
            ]
        )
    buttons.append(
        [
            InlineKeyboardButton(
                text="Показывать ролям",
                callback_data=cb.ButtonChooseRoleCallback(
                    button_id=button.button_id
                ).pack(),
            ),
        ]
    )
    buttons.append(
        [
            InlineKeyboardButton(
                text="Удалить кнопку",
                callback_data=cb.ButtonDeleteCallback(
                    button_id=button.button_id
                ).pack(),
            ),
        ],
    )
    if button.parent_button_id is not None:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Родительская кнопка",
                    callback_data=cb.ButtonInfoCallback(
                        button_id=button.parent_button_id
                    ).pack(),
                )
            ]
        )
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Назад",
                    callback_data=cb.ButtonGroupCallback(
                        button_id=button.parent_button_id
                    ).pack(),
                )
            ]
        )
    else:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Назад",
                    callback_data=cb.ButtonGroupCallback(
                        button_id=None
                    ).pack(),
                ),
            ]
        )

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    return keyboard
