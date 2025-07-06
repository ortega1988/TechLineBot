from aiogram.fsm.state import State, StatesGroup

class AccessRequest(StatesGroup):
    selecting_role = State()
    entering_area = State()


class AddZoneFSM(StatesGroup):
    waiting_for_branch = State()
    waiting_for_city = State()
    waiting_for_area = State()
    waiting_for_zone_name = State()
    confirming = State()


class AddGKSFSM(StatesGroup):
    waiting_for_region = State()
    waiting_for_number = State()

class FindHouseFSM(StatesGroup):
    waiting_for_address = State()
    confirming_add = State()
    waiting_for_city_auto = State()


class AddHousingOffice2GISFSM(StatesGroup):
    waiting_for_name = State()
    confirming_add = State()


class AddBranchFSM(StatesGroup):
    waiting_for_id_and_name = State()
    confirming = State()


class AddCityFSM(StatesGroup):
    waiting_for_region = State()
    waiting_for_city_name = State()
    waiting_for_city_url = State()
    confirming = State()