from aiogram.fsm.state import StatesGroup, State


class States(StatesGroup):
    add_channel = State()
    setting_channel = State()
    add_editor = State()
    new_post = State()
    button = State()
    hidden_button = State()



