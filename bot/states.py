from aiogram.fsm.state import StatesGroup, State


class States(StatesGroup):
    add_channel = State()
    setting_channel = State()


