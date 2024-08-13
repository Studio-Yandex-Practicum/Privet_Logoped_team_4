from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from callbacks import (
    ButtonGroupCallback,
    PromocodeDeleteCallback,
    VisitButtonCallback,
)
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
                callback_data=ButtonGroupCallback(button_id=None).pack(),
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
                callback_data=PromocodeDeleteCallback().pack(),
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
    ],
)


async def get_start_keyboard(
    role: RoleType, parent_button_id: Optional[int] = None
) -> InlineKeyboardMarkup:
    async with async_session() as session:
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
                callback_data=VisitButtonCallback(
                    button_id=button.button_id
                ).pack(),
            )
        ]
        for button in buttons
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
