from vkbottle import Keyboard, KeyboardButtonColor, Text

role_keyboard = (
    Keyboard(one_time=True)
    .add(Text('Родитель'), color=KeyboardButtonColor.PRIMARY)
    .add(Text('Логопед'), color=KeyboardButtonColor.PRIMARY)
)

parent_keyboard = (
    Keyboard(one_time=False)
    .add(Text('Отметить результат занятий'),
         color=KeyboardButtonColor.PRIMARY)
    .row()
    .add(Text('Пройти диагностику'), color=KeyboardButtonColor.PRIMARY)
    .add(Text('Полезные видео'), color=KeyboardButtonColor.PRIMARY)
    .row()
    .add(Text('Частые вопросы'), color=KeyboardButtonColor.PRIMARY)
    .row()
    .add(Text('Получать напоминания'), color=KeyboardButtonColor.PRIMARY)
    .row()
    .add(Text('Связаться с логопедом'), color=KeyboardButtonColor.SECONDARY)
    .row()
    .add(Text('Изменить роль'), color=KeyboardButtonColor.SECONDARY)
)

faq_keyboard = (
    Keyboard(one_time=False)
    .add(Text('Как заниматься'), color=KeyboardButtonColor.PRIMARY)
    .row()
    .add(Text('Не получается заниматься'), color=KeyboardButtonColor.PRIMARY)
    .row()
    .add(Text('Причины нарушения речи'), color=KeyboardButtonColor.PRIMARY)
    .row()
    .add(Text('Купить для iOS'), color=KeyboardButtonColor.SECONDARY)
    .row()
    .add(Text('Назад'), color=KeyboardButtonColor.NEGATIVE)
)

speech_therapist_keyboard = (
    Keyboard(one_time=False)
    .add(Text('Отметить результат занятий'),
         color=KeyboardButtonColor.PRIMARY)
    .row()
    .add(Text('Обучение'), color=KeyboardButtonColor.PRIMARY)
    .add(Text('Учреждениям'), color=KeyboardButtonColor.PRIMARY)
    .row()
    .add(Text('Методические рекомендации'),
         color=KeyboardButtonColor.PRIMARY)
    .row()
    .add(Text('Купить для iOS'), color=KeyboardButtonColor.PRIMARY)
    .add(Text('Вывести на ПК'), color=KeyboardButtonColor.PRIMARY)
    .row()
    .add(Text('Частые вопросы'), color=KeyboardButtonColor.PRIMARY)
    .row()
    .add(Text('Связаться с автором'), color=KeyboardButtonColor.SECONDARY)
    .add(Text('Изменить роль'), color=KeyboardButtonColor.SECONDARY)
)

admin_keyboard = (
    Keyboard(one_time=False)
    .add(Text('Материалы'),
         color=KeyboardButtonColor.PRIMARY)
    .row()
    .add(Text('Промокоды'),
         color=KeyboardButtonColor.PRIMARY)
)

cancel_keyboard = (
    Keyboard(one_time=True)
    .add(Text('Отмена'),
         color=KeyboardButtonColor.NEGATIVE)
)

admin_links_keyboard = (
    Keyboard(one_time=False)
    .add(Text('Добавить новую ссылку'),
         color=KeyboardButtonColor.PRIMARY)
    .row()
    .add(Text('Удалить ссылку'),
         color=KeyboardButtonColor.PRIMARY)
    .row()
    .add(Text('Загрузить файл'),
         color=KeyboardButtonColor.PRIMARY)
    .row()
    .add(Text('Назад'),
         color=KeyboardButtonColor.NEGATIVE)
)

admin_links_types_keyboard = (
    Keyboard(one_time=True)
    .add(Text('Ссылка'),
         color=KeyboardButtonColor.PRIMARY)
    .row()
    .add(Text('Путь к файлу'),
         color=KeyboardButtonColor.PRIMARY)
    .row()
    .add(Text('Отмена'),
         color=KeyboardButtonColor.NEGATIVE)
)

admin_links_to_role_keyboard = (
    Keyboard(one_time=True)
    .add(Text('Родитель'),
         color=KeyboardButtonColor.PRIMARY)
    .row()
    .add(Text('Логопед'),
         color=KeyboardButtonColor.PRIMARY)
    .row()
    .add(Text('Общее'),
         color=KeyboardButtonColor.PRIMARY)
    .row()
    .add(Text('Отмена'),
         color=KeyboardButtonColor.NEGATIVE)
)

admin_promocodes_keyboard = (
    Keyboard(one_time=False)
    .add(Text('Добавить новый промокод'),
         color=KeyboardButtonColor.PRIMARY)
    .row()
    .add(Text('Удалить промокод'),
         color=KeyboardButtonColor.PRIMARY)
    .row()
    .add(Text('Загрузить файл'),
         color=KeyboardButtonColor.PRIMARY)
    .row()
    .add(Text('Назад'),
         color=KeyboardButtonColor.NEGATIVE)
)
