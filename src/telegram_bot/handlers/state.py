from aiogram.fsm.state import State, StatesGroup
from config import database_url


DATABSE_URL = database_url


class Level(StatesGroup):
    main = State()
    parent = State()
    faq = State()
    therapist = State()
    role_chose = State()
    waiting_for_message = State()
