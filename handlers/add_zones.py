from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from fsm.states import AddZoneFSM
from keyboards.inline import get_branches_keyboard, get_cities_keyboard, get_areas_keyboard
from db.crud.branches import get_all_branches
from db.crud.cities import get_cities_by_branch_id
from db.crud.areas import get_areas_by_branch_id
from db.db import async_session
from db.crud.zones import (
    get_zone_by_name_and_city,
    create_zone
)


router = Router()


@router.callback_query(F.data == "admin:add_zone")
async def add_zone_start(callback: CallbackQuery, state: FSMContext):
    async with async_session() as session:
        branches = await get_all_branches(session)
    await callback.message.edit_text("Выберите филиал:", reply_markup=get_branches_keyboard(branches))
    await state.set_state(AddZoneFSM.waiting_for_branch)
    await callback.answer()

@router.callback_query(AddZoneFSM.waiting_for_branch, F.data.startswith("add_zone_branch_"))
async def select_branch(callback: CallbackQuery, state: FSMContext):
    branch_id = int(callback.data.replace("add_zone_branch_", ""))
    await state.update_data(branch_id=branch_id)
    async with async_session() as session:
        cities = await get_cities_by_branch_id(session, branch_id)
    await callback.message.edit_text("Выберите город:", reply_markup=get_cities_keyboard(cities))
    await state.set_state(AddZoneFSM.waiting_for_city)
    await callback.answer()

@router.callback_query(AddZoneFSM.waiting_for_city, F.data.startswith("add_zone_city_"))
async def select_city(callback: CallbackQuery, state: FSMContext):
    city_id = int(callback.data.replace("add_zone_city_", ""))
    await state.update_data(city_id=city_id)
    data = await state.get_data()
    branch_id = data["branch_id"]
    async with async_session() as session:
        areas = await get_areas_by_branch_id(session, branch_id)
    await callback.message.edit_text("Выберите ГКС:", reply_markup=get_areas_keyboard(areas))
    await state.set_state(AddZoneFSM.waiting_for_area)
    await callback.answer()

@router.callback_query(AddZoneFSM.waiting_for_area, F.data.startswith("add_zone_area_"))
async def select_area(callback: CallbackQuery, state: FSMContext):
    area_id = callback.data.replace("add_zone_area_", "")
    await state.update_data(area_id=area_id)
    await callback.message.edit_text("Введите название района:")
    await state.set_state(AddZoneFSM.waiting_for_zone_name)
    await callback.answer()

@router.message(AddZoneFSM.waiting_for_zone_name)
async def input_zone_name(message: Message, state: FSMContext):
    zone_name = message.text.strip()
    data = await state.get_data()
    branch_id = data["branch_id"]
    city_id = data["city_id"]
    area_id = data["area_id"]
    async with async_session() as session:
        existing = await get_zone_by_name_and_city(session, zone_name, city_id)
        if existing:
            await message.answer("⚠️ Такой район уже есть в этом городе!")
            return
        zone = await create_zone(session=session, name=zone_name, city_id=city_id, area_id=area_id, branch_id=branch_id)
    await message.answer(f"✅ Район <b>{zone_name}</b> добавлен.")
    await state.clear()
