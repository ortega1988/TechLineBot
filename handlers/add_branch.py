from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from fsm.states import AddBranchFSM
from db.db import async_session
from db.crud.branches import get_branch_by_id, get_branch_by_name, create_branch
from keyboards.inline import get_confirm_add_branch_keyboard, get_admin_menu

router = Router()

@router.callback_query(F.data == "add_branch")
async def start_add_branch(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите <b>ID и название филиала</b> в одну строку (например: <b>16 Казанский</b>):")
    await state.set_state(AddBranchFSM.waiting_for_id_and_name)
    await callback.answer()

@router.message(AddBranchFSM.waiting_for_id_and_name)
async def process_branch_id_and_name(message: Message, state: FSMContext):
    parts = message.text.strip().split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("⚠️ Введите ID и название через пробел (например: <b>16 Казанский</b>)")
        return
    try:
        branch_id = int(parts[0])
        if branch_id <= 0:
            raise ValueError
    except Exception:
        await message.answer("⚠️ ID филиала должен быть положительным числом!")
        return
    name = parts[1].strip()
    if not name:
        await message.answer("⚠️ Название филиала не может быть пустым!")
        return

    async with async_session() as session:
        exist_id = await get_branch_by_id(session, branch_id)
        if exist_id:
            await message.answer("⚠️ Филиал с таким ID уже существует!")
            return
        exist_name = await get_branch_by_name(session, name)
        if exist_name:
            await message.answer("⚠️ Филиал с таким названием уже существует!")
            return

    await state.update_data(branch_id=branch_id, name=name)
    await message.answer(
        f"Добавить филиал:\n<b>ID:</b> {branch_id}\n<b>Название:</b> {name}\n\nПодтвердить?",
        reply_markup=get_confirm_add_branch_keyboard()
    )
    await state.set_state(AddBranchFSM.confirming)

@router.callback_query(AddBranchFSM.confirming, F.data == "add_branch_confirm")
async def confirm_branch(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    branch_id = data.get("branch_id")
    name = data.get("name")
    async with async_session() as session:
        await create_branch(session, name=name, branch_id=branch_id)
    await callback.message.edit_text("✅ Филиал успешно добавлен!", reply_markup=get_admin_menu())
    await state.clear()
    await callback.answer()
