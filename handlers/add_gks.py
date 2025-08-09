from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from db.crud.areas import create_area, get_area_by_id
from db.crud.branches import get_all_branches
from db.db import async_session
from fsm.states import AddGKSFSM
from keyboards.inline import get_admin_menu, get_regions_gks_keyboard

router = Router()


@router.callback_query(F.data == "admin:add_gks")
async def start_add_gks(callback: CallbackQuery, state: FSMContext):
    async with async_session() as session:
        regions = await get_all_branches(session)
    await callback.message.edit_text(
        "Выберите регион (филиал) для ГКС:",
        reply_markup=get_regions_gks_keyboard(regions),
    )
    await state.set_state(AddGKSFSM.waiting_for_region)
    await callback.answer()


@router.callback_query(
    AddGKSFSM.waiting_for_region, F.data.startswith("add_gks_region_")
)
async def select_gks_region(callback: CallbackQuery, state: FSMContext):
    branch_id = int(callback.data.replace("add_gks_region_", ""))
    await state.update_data(branch_id=branch_id)
    await callback.message.edit_text(
        "Введите номер ГКС (только число, например: <b>3</b>)"
    )
    await state.set_state(AddGKSFSM.waiting_for_number)
    await callback.answer()


@router.message(AddGKSFSM.waiting_for_number)
async def add_gks_number(message: Message, state: FSMContext):
    number = message.text.strip()
    if not number.isdigit() or int(number) <= 0:
        await message.answer("⚠️ Введите только положительное число, например: 2")
        return
    data = await state.get_data()
    branch_id = data["branch_id"]
    area_id = f"{branch_id}.{number}"
    name = f"ГКС {number}"
    async with async_session() as session:
        if await get_area_by_id(session, area_id):
            await message.answer(
                f"⚠️ Участок с ID <b>{area_id}</b> уже существует для этого региона!"
            )
            return
        await create_area(
            session=session, area_id=area_id, name=name, branch_id=branch_id
        )

    await message.answer(
        f"✅ <b>{name}</b> (участок: {area_id}, филиал: {branch_id}) добавлен.",
        reply_markup=get_admin_menu(),
    )
    await state.clear()
