from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from fsm.states import AddZoneFSM
from keyboards.inline import get_list_zones_menu
from db.queries import get_zone_id_by_name_and_city, link_area_with_zone, insert_zone

router = Router()

@router.callback_query(F.data == "admin:zone_menu")
async def open_zone_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "🛠 Меню администрирования:",
        reply_markup=get_list_zones_menu()
    )

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
    await message.answer("Введите регион (номер филиала):")
    await state.set_state(AddZoneFSM.waiting_city)

@router.message(AddZoneFSM.waiting_city)
async def input_city(message: Message, state: FSMContext):
    data = await state.get_data()
    area = data["area"]
    zone_name = data["zone_name"]
    city = data["city"]
    region = message.text.strip()

    # Проверяем существование зоны
    zone = await get_zone_id_by_name_and_city(zone_name, city)

    if not zone:
        await insert_zone(zone_name, city, region)
        zone = await get_zone_id_by_name_and_city(zone_name, city)
        if not zone:
            return

    # Привязываем зону к участку
    await link_area_with_zone(area, zone["id"])

    await message.answer(
        f"✅ Район <b>{zone_name}</b> ({city}) добавлен к участку <b>{area}</b>."
    )
    await state.clear()
