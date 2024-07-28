from aiogram.fsm.state import State, StatesGroup

class Level(StatesGroup):
    main = State()
    parent = State()
    faq = State()
    therapist = State()
