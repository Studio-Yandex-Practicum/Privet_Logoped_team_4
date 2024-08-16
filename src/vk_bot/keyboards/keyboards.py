import os
import sys

from sqlalchemy import and_, or_, select
from vkbottle import Callback, Keyboard, KeyboardButtonColor, Text
from typing import Optional

parent_folder_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)
sys.path.append(parent_folder_path)
from db.models import Button, RoleType, async_session  # noqa

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
