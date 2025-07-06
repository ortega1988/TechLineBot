from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from fsm.states import AddCityFSM
from db.db import async_session
from db.crud.branches import get_all_branches
from db.crud.cities import get_city_by_name, create_city
from keyboards.inline import get_regions_keyboard, get_confirm_add_city_keyboard, get_admin_menu

router = Router()

@router.callback_query(F.data == "add_city")
async def start_add_city(callback: CallbackQuery, state: FSMContext):
    async with async_session() as session:
        regions = await get_all_branches(session)
    await callback.message.answer(
        "Выберите регион (филиал) для нового города:",
        reply_markup=get_regions_keyboard(regions)
    )
    await state.set_state(AddCityFSM.waiting_for_region)
    await callback.answer()

@router.callback_query(AddCityFSM.waiting_for_region, F.data.startswith("add_city_region_"))
async def select_region(callback: CallbackQuery, state: FSMContext):
    branch_id = int(callback.data.replace("add_city_region_", ""))
    await state.update_data(branch_id=branch_id)
    await callback.message.edit_text("Введите название города:")
    await state.set_state(AddCityFSM.waiting_for_city_name)
    await callback.answer()

@router.message(AddCityFSM.waiting_for_city_name)
async def process_city_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if not name:
        await message.answer("⚠️ Название города не может быть пустым!")
        return

    async with async_session() as session:
        if await get_city_by_name(session, name):
            await message.answer("⚠️ Город с таким названием уже существует!")
            return

    await state.update_data(name=name)
    await message.answer("Вставьте ссылку на город в 2ГИС (например: https://2gis.ru/kazan):")
    await state.set_state(AddCityFSM.waiting_for_city_url)

@router.message(AddCityFSM.waiting_for_city_url)
async def process_city_url(message: Message, state: FSMContext):
    url = message.text.strip()
    if not url.startswith("http"):
        await message.answer("⚠️ Ссылка должна начинаться с http(s)://")
        return
    await state.update_data(url=url)
    data = await state.get_data()
    await message.answer(
        f"Добавить город?\n\n"
        f"<b>Регион:</b> {data['branch_id']}\n"
        f"<b>Название:</b> {data['name']}\n"
        f"<b>2ГИС:</b> {url}\n",
        reply_markup=get_confirm_add_city_keyboard()
    )
    await state.set_state(AddCityFSM.confirming)

@router.callback_query(AddCityFSM.confirming, F.data == "add_city_confirm")
async def confirm_city(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    async with async_session() as session:
        await create_city(session, name=data["name"], url=data["url"], branch_id=data["branch_id"])
    await callback.message.edit_text("✅ Город успешно добавлен!", reply_markup=get_admin_menu())
    await state.clear()
    await callback.answer()
