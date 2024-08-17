from aiogram.fsm.state import State, StatesGroup


class Level(StatesGroup):
    """Стейты пользователя."""

    main = State()
    parent = State()
    faq = State()
    therapist = State()
    role_chose = State()
    waiting_for_message = State()
    awaiting_admin_reply = State()
    notification_hour = State()


class AdminStates(StatesGroup):
    """Стейты администратора."""

    admin = State()
    links = State()
    promocodes = State()
    users = State()
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
    waiting_button_file = State()
    waiting_on_button_text = State()
    waiting_button_text = State()
    waiting_on_button_text_create = State()
    waiting_button_text_create = State()
    waiting_button_file_create = State()
    waiting_user_id_to_ban = State()
    waiting_user_id_to_unban = State()
    send_mailing = State()
