import os
import sys
from typing import Optional

from sqlalchemy import and_, or_, select
from vkbottle import Callback, Keyboard, KeyboardButtonColor, Text

parent_folder_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)
sys.path.append(parent_folder_path)
from db.models import (Button, NotificationInterval,  # noqa
                       NotificationWeekDay, RoleType, async_session)

role_keyboard = (
    Keyboard(inline=True)
    .add(
        Callback("Родитель", payload={"type": "role", "role": "parent"}),
        color=KeyboardButtonColor.PRIMARY,
    )
    .add(
        Callback(
            "Логопед", payload={"type": "role", "role": "speech_therapist"}
        ),
        color=KeyboardButtonColor.PRIMARY,
    )
    .add(
        Callback("Информация", payload={"type": "main_info"}),
        color=KeyboardButtonColor.SECONDARY,
    )
)

parent_keyboard = (
    Keyboard(one_time=False)
    .add(Text("Отметить результат занятий"), color=KeyboardButtonColor.PRIMARY)
    .row()
    .add(Text("Пройти диагностику"), color=KeyboardButtonColor.PRIMARY)
    .add(Text("Полезные видео"), color=KeyboardButtonColor.PRIMARY)
    .row()
    .add(Text("Частые вопросы"), color=KeyboardButtonColor.PRIMARY)
    .row()
    .add(Text("Получать напоминания"), color=KeyboardButtonColor.PRIMARY)
    .row()
    .add(Text("Связаться с логопедом"), color=KeyboardButtonColor.SECONDARY)
    .row()
    .add(Text("Изменить роль"), color=KeyboardButtonColor.SECONDARY)
)

faq_keyboard = (
    Keyboard(one_time=False)
    .add(Text("Как заниматься"), color=KeyboardButtonColor.PRIMARY)
    .row()
    .add(Text("Не получается заниматься"), color=KeyboardButtonColor.PRIMARY)
    .row()
    .add(Text("Причины нарушения речи"), color=KeyboardButtonColor.PRIMARY)
    .row()
    .add(Text("Купить для iOS"), color=KeyboardButtonColor.SECONDARY)
    .row()
    .add(Text("Назад"), color=KeyboardButtonColor.NEGATIVE)
)

speech_therapist_keyboard = (
    Keyboard(one_time=False)
    .add(Text("Отметить результат занятий"), color=KeyboardButtonColor.PRIMARY)
    .row()
    .add(Text("Обучение"), color=KeyboardButtonColor.PRIMARY)
    .add(Text("Учреждениям"), color=KeyboardButtonColor.PRIMARY)
    .row()
    .add(Text("Методические рекомендации"), color=KeyboardButtonColor.PRIMARY)
    .row()
    .add(Text("Купить для iOS"), color=KeyboardButtonColor.PRIMARY)
    .add(Text("Вывести на ПК"), color=KeyboardButtonColor.PRIMARY)
    .row()
    .add(Text("Частые вопросы"), color=KeyboardButtonColor.PRIMARY)
    .row()
    .add(Text("Связаться с автором"), color=KeyboardButtonColor.SECONDARY)
    .add(Text("Изменить роль"), color=KeyboardButtonColor.SECONDARY)
)

admin_keyboard = (
    Keyboard(inline=True)
    .add(
        Callback(
            "Промокоды",
            payload={"type": "promocodes"},
        ),
        color=KeyboardButtonColor.PRIMARY,
    )
    .row()
    .add(
        Callback(
            "Кнопки", payload={"type": "buttons", "parent_button_id": None}
        ),
        color=KeyboardButtonColor.PRIMARY,
    )
    .row()
    .add(
        Callback("Пользователи", payload={"type": "users"}),
        color=KeyboardButtonColor.PRIMARY,
    )
    .row()
    .add(
        Callback("Рассылка", payload={"type": "mailing"}),
        color=KeyboardButtonColor.PRIMARY,
    )
)

cancel_keyboard = Keyboard(one_time=True).add(
    Text("Отмена"), color=KeyboardButtonColor.NEGATIVE
)

admin_promocodes_keyboard = (
    Keyboard(inline=True)
    .add(
        Callback("Добавить промокод", payload={"type": "add_promocode"}),
        color=KeyboardButtonColor.PRIMARY,
    )
    .row()
    .add(
        Callback("Удалить промокод", payload={"type": "delete_promocode"}),
        color=KeyboardButtonColor.PRIMARY,
    )
    .row()
    .add(
        Callback("Назад", payload={"type": "admin"}),
        color=KeyboardButtonColor.NEGATIVE,
    )
)


async def get_main_keyboard(role_type: Optional[RoleType]) -> Keyboard:
    async with async_session() as session:
        if role_type is None:
            buttons = await session.execute(
                select(Button).where(
                    and_(
                        Button.parent_button_id.is_(None),
                        Button.is_in_main_menu.is_(True),
                    )
                )
            )
        else:
            buttons = await session.execute(
                select(Button).where(
                    and_(
                        Button.parent_button_id.is_(None),
                        or_(
                            Button.to_role == role_type,
                            Button.to_role.is_(None),
                        ),
                    )
                )
            )
        buttons: list[Button] = buttons.scalars().all()

    keyboard = Keyboard(inline=role_type is None)
    for button in buttons:
        keyboard.row().add(
            Callback(
                button.button_name,
                {
                    "type": "button_click",
                    "button_id": button.button_id,
                    "authorized": role_type is not None,
                },
            )
        )

    return keyboard


admin_users_keyboard = (
    Keyboard(inline=True)
    .add(
        Callback("Заблокировать пользователя", payload={"type": "ban_user"}),
        color=KeyboardButtonColor.PRIMARY,
    )
    .row()
    .add(
        Callback(
            "Разблокировать пользователя", payload={"type": "unban_user"}
        ),
        color=KeyboardButtonColor.PRIMARY,
    )
    .row()
    .add(
        Callback("Назад", payload={"type": "admin"}),
        color=KeyboardButtonColor.NEGATIVE,
    )
)

mailing = (
    Keyboard(inline=True)
    .add(
        Callback("Отправить рассылку", payload={"type": "send_mailing"}),
        color=KeyboardButtonColor.PRIMARY,
    )
    .row()
    .add(
        Callback("Назад", payload={"type": "admin"}),
        color=KeyboardButtonColor.NEGATIVE,
    )
)


mailing_role = (
    Keyboard(inline=True)
    .add(
        Callback(
            "Родителям",
            payload={"type": "mailing_role", "role": "parent"},
        ),
        color=KeyboardButtonColor.PRIMARY,
    )
    .row()
    .add(
        Callback(
            "Логопедам",
            payload={"type": "mailing_role", "role": "speech_therapist"},
        ),
        color=KeyboardButtonColor.PRIMARY,
    )
    .row()
    .add(
        Callback("Всем", payload={"type": "mailing_role", "role": "all"}),
        color=KeyboardButtonColor.SECONDARY,
    )
)


async def get_mailing_settings_keyboard(state: dict) -> Keyboard:
    keyboard = Keyboard(inline=True)
    keyboard.add(
        Callback(
            (
                "Отправить всем: ✅"
                if state["ignore_subscribed"]
                else "Отправить всем: ❌"
            ),
            payload={
                "type": "mailing_settings",
                "ignore_subscribed": not state["ignore_subscribed"],
                "role": state["role"],
                "message": state["message"],
            },
        )
    )

    keyboard.row().add(
        Callback(
            (
                "Всем ролям"
                if state["role"] == "all"
                else (
                    "Только родителям"
                    if state["role"] == "parent"
                    else "Только логопедам"
                )
            ),
            payload={
                "type": "mailing_settings_role",
            },
        )
    )

    keyboard.row().add(
        Callback(
            "Отмена",
            payload={
                "type": "mailing",
            },
        )
    ).add(
        Callback(
            "Отправить",
            payload={
                "type": "send_mailing_messages",
            },
        )
    )

    return keyboard


def get_notifications_keyboard(button_id: int, on: bool) -> Keyboard:
    if on:
        keyboard = Keyboard(inline=True)
        keyboard.add(
            Callback(
                "Выбрать интервал",
                payload={
                    "type": "notification_interval",
                    "button_id": button_id,
                    "interval": None,
                },
            )
        )
        keyboard.row().add(
            Callback(
                "Выключить уведомления",
                payload={
                    "type": "enable_notifications",
                    "button_id": button_id,
                    "is_enabled": False,
                },
            )
        )
        return keyboard
    else:
        keyboard = Keyboard(inline=True)
        keyboard.add(
            Callback(
                "Включить уведомления",
                payload={
                    "type": "enable_notifications",
                    "button_id": button_id,
                    "is_enabled": True,
                },
            )
        )
        return keyboard


def get_notifications_interval_keyboard(
    button_id: int,
) -> Keyboard:
    keyboard = Keyboard(inline=True)
    keyboard.add(
        Callback(
            "Каждый день",
            payload={
                "type": "notification_interval",
                "button_id": button_id,
                "interval": NotificationInterval.EVERY_DAY,
            },
        )
    )
    keyboard.add(
        Callback(
            "Через день",
            payload={
                "type": "notification_interval",
                "button_id": button_id,
                "interval": NotificationInterval.OTHER_DAY,
            },
        )
    )
    keyboard.row().add(
        Callback(
            "Выбор пользователя",
            payload={
                "type": "notification_interval",
                "button_id": button_id,
                "interval": NotificationInterval.USER_CHOICE,
            },
        )
    )
    return keyboard


def get_notifications_dayofweek_keyboard(
    button_id: int,
) -> Keyboard:
    days_of_week = {
        NotificationWeekDay.MONDAY: "Понедельник",
        NotificationWeekDay.TUESDAY: "Вторник",
        NotificationWeekDay.WEDNESDAY: "Среда",
        NotificationWeekDay.THURSDAY: "Четверг",
        NotificationWeekDay.FRIDAY: "Пятница",
        NotificationWeekDay.SATURDAY: "Суббота",
        NotificationWeekDay.SUNDAY: "Воскресенье",
    }
    keyboard = Keyboard(inline=True)
    for day, text in days_of_week.items():
        if day == NotificationWeekDay.SATURDAY:
            keyboard.row()
        keyboard.add(
            Callback(
                text,
                payload={
                    "type": "notification_interval",
                    "button_id": button_id,
                    "interval": NotificationInterval.USER_CHOICE,
                    "day_of_week": day,
                },
            )
        )
    return keyboard
