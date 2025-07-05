from aiogram.fsm.state import State, StatesGroup

class AccessRequest(StatesGroup):
    selecting_role = State()
    entering_area = State()


class AddZoneFSM(StatesGroup):
    waiting_area = State()
    waiting_zone_name = State()
    waiting_city = State()
    waiting_region = State()


class AddGKSFSM(StatesGroup):
    waiting_id = State()
    waiting_name = State()
    waiting_region = State()


class FindHouseFSM(StatesGroup):
    waiting_for_address = State()
    confirming_add = State()
    test = State()


class AddHousingOffice2GISFSM(StatesGroup):
    waiting_for_name = State()
    confirming_add = State()