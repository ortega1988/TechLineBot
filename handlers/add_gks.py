from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from fsm.states import AddGKSFSM
from keyboards.inline import get_list_gks_menu
from db.queries import area_exists, insert_area

router = Router()

@router.callback_query(F.data == "admin:gks_menu")
async def open_gks_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "🛠 Меню администрирования:",
        reply_markup=get_list_gks_menu()
    )

@router.callback_query(F.data == "admin:add_gks")
async def add_gks(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Введите номер участка:")
    await state.set_state(AddGKSFSM.waiting_id)

@router.message(AddGKSFSM.waiting_id)
async def add_gks_id(message: Message, state: FSMContext):
    await state.update_data(id=message.text.strip())
    await message.answer("Введите название ГКС:")
    await state.set_state(AddGKSFSM.waiting_name)

@router.message(AddGKSFSM.waiting_name)
async def add_gks_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await message.answer("Введите регион (номер филиала):")
    await state.set_state(AddGKSFSM.waiting_region)

@router.message(AddGKSFSM.waiting_region)
async def add_gks_region(message: Message, state: FSMContext):
    data = await state.get_data()
    area_id = data["id"]
    name = data["name"]
    region = message.text.strip()

    exists = await area_exists(area_id)
    if not exists:
        await insert_area(area_id, name, region)

    await message.answer(
        f"✅ ГКС <b>{name}</b> ({region}) добавлен."
    )
    await state.clear()
