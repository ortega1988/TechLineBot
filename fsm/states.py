from aiogram.fsm.state import State, StatesGroup

class AccessRequest(StatesGroup):
    selecting_role = State()
    entering_area = State()