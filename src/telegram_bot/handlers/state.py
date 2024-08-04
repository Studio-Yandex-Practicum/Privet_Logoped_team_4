from aiogram.fsm.state import State, StatesGroup
from config import database_url

DATABASE_URL = database_url


class Level(StatesGroup):
    main = State()
    parent = State()
    faq = State()
    therapist = State()
    role_chose = State()
    admin = State()
    links = State()
    promocodes = State()


class AdminOptions(StatesGroup):
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
