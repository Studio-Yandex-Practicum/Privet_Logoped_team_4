from vkbottle import Keyboard, KeyboardButtonColor, Text, Callback

role_keyboard = (
    Keyboard(one_time=True)
    .add(Text("Родитель"), color=KeyboardButtonColor.PRIMARY)
    .add(Text("Логопед"), color=KeyboardButtonColor.PRIMARY)
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
        Callback("Кнопки", payload={"type": "buttons", "parent_button_id": None}),
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
