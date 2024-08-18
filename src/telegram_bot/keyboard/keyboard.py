import os
import sys
from typing import Optional

import callbacks as cb
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from sqlalchemy import and_, or_, select

grand_parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(grand_parent_dir)
from db.models import NotificationInterval  # noqa
from db.models import (
    Button,
    ButtonType,
    NotificationIntervalType,
    NotificationWeekDay,
    RoleType,
    async_session,
)

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

links = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Добавить ссылку")],
        [KeyboardButton(text="Удалить ссылку")],
        [KeyboardButton(text="Загрузить файл")],
        [KeyboardButton(text="Назад")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите пункт меню...",
)

links_types = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Ссылка")],
        [KeyboardButton(text="Путь к файлу")],
        [KeyboardButton(text="Отмена")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите пункт меню...",
)
admin = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Промокоды", callback_data="promocodes"),
        ],
        [
            InlineKeyboardButton(
                text="Кнопки",
                callback_data=cb.ButtonGroupCallback(button_id=None).pack(),
            ),
        ],
        [
            InlineKeyboardButton(
                text="Пользователи",
                callback_data="users",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Рассылка",
                callback_data="mailing",
            ),
        ],
    ],
)

users = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Заблокировать пользователя", callback_data="ban_user"
            )
        ],
        [
            InlineKeyboardButton(
                text="Разблокировать пользователя", callback_data="unban_user"
            )
        ],
        [InlineKeyboardButton(text="Назад", callback_data="admin")],
    ],
)

links_to_role = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Родитель")],
        [KeyboardButton(text="Логопед")],
        [KeyboardButton(text="Общее")],
        [KeyboardButton(text="Отмена")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите пункт меню...",
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
    one_time_keyboard=True,
    input_field_placeholder="Выберите пункт меню...",
)

role = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Родитель", callback_data="parent"),
            InlineKeyboardButton(text="Логопед", callback_data="therapist"),
        ],
        [InlineKeyboardButton(text="Информация", callback_data="info")],
    ],
)

mailing = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Отправить рассылку", callback_data="send_mailing"
            )
        ],
        [InlineKeyboardButton(text="Назад", callback_data="admin")],
    ],
)

mailing_role = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Родителям",
                callback_data=cb.MailingButtonRole(
                    role=RoleType.PARENT
                ).pack(),
            )
        ],
        [
            InlineKeyboardButton(
                text="Логопедам",
                callback_data=cb.MailingButtonRole(
                    role=RoleType.SPEECH_THERAPIST
                ).pack(),
            )
        ],
        [
            InlineKeyboardButton(
                text="Всем",
                callback_data=cb.MailingButtonRole(role=None).pack(),
            )
        ],
    ],
)


def get_notifications_keyboard(
    button_id: int, on: bool
) -> InlineKeyboardMarkup:
    if on:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Выбрать интервал",
                        callback_data=cb.NotificationIntervalCallback(
                            interval=None,
                            button_id=button_id,
                        ).pack(),
                    ),
                    InlineKeyboardButton(
                        text="Выключить уведомления",
                        callback_data=cb.EnableNotifications(
                            is_enabled=False, button_id=button_id
                        ).pack(),
                    ),
                ],
            ],
            resize_keyboard=True,
            input_field_placeholder="Выберите пункт меню...",
        )
    else:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Включить уведомления",
                        callback_data=cb.EnableNotifications(
                            is_enabled=True,
                            button_id=button_id,
                        ).pack(),
                    )
                ],
            ],
        )


def get_notifications_interval_keyboard(
    button_id: int,
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Каждый день",
                    callback_data=cb.NotificationIntervalCallback(
                        interval=NotificationIntervalType.EVERY_DAY,
                        button_id=button_id,
                    ).pack(),
                ),
                InlineKeyboardButton(
                    text="Через день",
                    callback_data=cb.NotificationIntervalCallback(
                        interval=NotificationIntervalType.OTHER_DAY,
                        button_id=button_id,
                    ).pack(),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Выбор пользователя",
                    callback_data=cb.NotificationIntervalCallback(
                        interval=NotificationIntervalType.USER_CHOICE,
                        button_id=button_id,
                    ).pack(),
                ),
            ],
        ]
    )


def get_notifications_dayofweek_keyboard(
    button_id: int,
) -> InlineKeyboardMarkup:
    days_of_week = {
        NotificationWeekDay.MONDAY: "Понедельник",
        NotificationWeekDay.TUESDAY: "Вторник",
        NotificationWeekDay.WEDNESDAY: "Среда",
        NotificationWeekDay.THURSDAY: "Четверг",
        NotificationWeekDay.FRIDAY: "Пятница",
        NotificationWeekDay.SATURDAY: "Суббота",
        NotificationWeekDay.SUNDAY: "Воскресенье",
    }
    buttons = []
    for day, text in days_of_week.items():
        buttons.append(
            [
                InlineKeyboardButton(
                    text=text,
                    callback_data=cb.NotificationIntervalCallback(
                        interval=NotificationIntervalType.USER_CHOICE,
                        button_id=button_id,
                        day_of_week=day,
                    ).pack(),
                )
            ]
        )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


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
    if (
        button.button_type
        in [
            ButtonType.FILE,
            ButtonType.TEXT,
        ]
        and button.parent_button_id is None
    ):
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


async def get_mailing_settings_keyboard(state: dict) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=(
                    "Отправить всем: ✅"
                    if state["ignore_subscribed"]
                    else "Отправить всем: ❌"
                ),
                callback_data=cb.MailingButtonSettings(
                    message=state["message"],
                    role=state["role"],
                    ignore_subscribed=not state["ignore_subscribed"],
                ).pack(),
            ),
        ],
        [
            InlineKeyboardButton(
                text=(
                    "Всем ролям"
                    if state["role"] is None
                    else (
                        "Только родителям"
                        if state["role"] == RoleType.PARENT
                        else "Только логопедам"
                    )
                ),
                callback_data="mailing_settings_role",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Отмена",
                callback_data="send_mailing",
            ),
            InlineKeyboardButton(
                text="Отправить",
                callback_data="send_mailing_messages",
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
