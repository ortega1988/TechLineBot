from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from fsm.states import AddZoneFSM
from keyboards.inline import get_list_zones_menu
from aiogram.fsm.context import FSMContext

from db.db import db

router = Router()

@router.callback_query(F.data == "admin:zone_menu")
async def open_zone_menu(callback: CallbackQuery):
    await callback.message.edit_text("🛠 Меню администрирования:", reply_markup=get_list_zones_menu())

@router.callback_query(F.data == "admin:add_zone")
async def admin_add_zone(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Введите номер участка:")
    await state.set_state(AddZoneFSM.waiting_area)

@router.message(AddZoneFSM.waiting_area)
async def input_area(message: Message, state: FSMContext):
    await state.update_data(area=message.text.strip())
    await message.answer("Введите название района:")
    await state.set_state(AddZoneFSM.waiting_zone_name)

@router.message(AddZoneFSM.waiting_zone_name)
async def input_zone(message: Message, state: FSMContext):
    await state.update_data(zone_name=message.text.strip())
    await message.answer("Введите город:")
    await state.set_state(AddZoneFSM.waiting_region)

@router.message(AddZoneFSM.waiting_region)
async def input_region(message: Message, state: FSMContext):
    await state.update_data(city=message.text.strip())
    await message.answer("Введите регион:")
    await state.set_state(AddZoneFSM.waiting_city)


@router.message(AddZoneFSM.waiting_city)
async def input_city(message: Message, state: FSMContext):
    data = await state.get_data()
    area = data["area"]
    zone_name = data["zone_name"]
    city = data["city"]
    region = message.text.strip()

    # Проверка и добавление района
    zone = await db.fetchone("SELECT id FROM zones WHERE name = %s AND city = %s", (zone_name, city))
    if not zone:
        await db.execute("INSERT INTO zones (name, city, branch_id) VALUES (%s, %s, %s)", (zone_name, city, region))
        zone = await db.fetchone("SELECT id FROM zones WHERE name = %s AND city = %s", (zone_name, city))

    # Привязка района к участку
    await db.execute("INSERT IGNORE INTO area_zones (area_id, zone_id) VALUES (%s, %s)", (area, zone["id"]))

    await message.answer(f"✅ Район <b>{zone_name}</b> ({city}) добавлен к участку <b>{area}</b>.")
    await state.clear()
