from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from fsm.states import AddGKSFSM
from keyboards.inline import get_list_gks_menu
from db.db import async_session
from db.crud.areas import get_area_by_id, create_area


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

    async with async_session() as session:
        exists = await get_area_by_id(session, area_id)
        if not exists:
            await create_area(
                session=session,
                area_id=area_id,
                name=name,
                branch_id=int(region)
            )

    await message.answer(
        f"✅ ГКС <b>{name}</b> ({region}) добавлен."
    )
    await state.clear()
