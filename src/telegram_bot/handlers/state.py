from aiogram.fsm.state import State, StatesGroup


class Level(StatesGroup):
    """Стейты пользователя."""
    main = State()
    parent = State()
    faq = State()
    therapist = State()
    role_chose = State()


class NotificationStates(StatesGroup):
    notification = State()
    every_day = State()
    other_day = State()
    day_week_choice = State()
    user_choice = State()


class AdminStates(StatesGroup):
    """Стейты администратора."""
    admin = State()
    links = State()
    promocodes = State()
    waiting_link_name = State()
    waiting_link_type = State()
    waiting_link = State()
    waiting_link_to_role = State()
    delete_link = State()
    waiting_promocode = State()
    waiting_promocode_filepath = State()
    delete_promocode = State()
    upload_link_file = State()
    upload_promocode_file = State()
