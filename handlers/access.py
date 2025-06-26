# access.py
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from fsm.states import AccessRequest
from db.queries import (
    get_user_by_id,
    branch_exists,
    area_exists,
    get_super_admin,
    get_rn_by_branch,
    get_rgks_by_area,
    update_user_role_area,
)
from keyboards.inline import select_role_keyboard, build_approval_keyboard
from utils.messages import build_access_request_message

router = Router()

ROLES = {
    "role_rn": 1,
    "role_rgks": 2,
    "role_si": 3,
}

@router.callback_query(F.data == "request_access")
async def start_access(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AccessRequest.selecting_role)
    await callback.message.answer(
        "👤 Кем вы хотите быть в системе?",
        reply_markup=select_role_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data.in_(ROLES.keys()))
async def handle_role_selection(callback: CallbackQuery, state: FSMContext):
    role_id = ROLES[callback.data]
    await state.update_data(role_id=role_id)
    await state.set_state(AccessRequest.entering_area)
    await callback.message.answer(
        "📍 Введите номер участка (например, <code>16.2</code>) "
        "или филиала (<code>16</code>) в зависимости от выбранной роли:"
    )
    await callback.answer()

@router.message(AccessRequest.entering_area)
async def handle_area_input(message: Message, state: FSMContext):
    data = await state.get_data()
    role_id = data["role_id"]
    user = await get_user_by_id(message.from_user.id)
    await state.clear()
    if user is None:
        await message.answer("❌ Ошибка: ваш аккаунт не найден в базе данных. Пожалуйста, зарегистрируйтесь.")
        return

    area_input = message.text.strip()

    # Запрос от РН (role_id = 1) → супер-админ
    if role_id == ROLES["role_rn"]:
        if not await branch_exists(area_input):
            await message.answer("❌ Филиал не найден.")
            return

        admin = await get_super_admin()
        if admin:
            await message.bot.send_message(
                chat_id=admin["id"],
                text=build_access_request_message(user, "РН", area_input),
                reply_markup=build_approval_keyboard(user["id"], role_id, area_input)
            )
            await message.answer("✅ Запрос отправлен администратору.")
        else:
            await message.answer("⚠️ Главный администратор не найден.")

    # Запрос от РГКС (role_id = 2) → РН
    elif role_id == ROLES["role_rgks"]:
        if not await area_exists(area_input):
            await message.answer("❌ Участок не найден.")
            return

        branch_id = area_input.split(".")[0]
        target = await get_rn_by_branch(branch_id)
        if target:
            await message.bot.send_message(
                chat_id=target["id"],
                text=build_access_request_message(user, "РГКС", area_input),
                reply_markup=build_approval_keyboard(user["id"], role_id, area_input)
            )
            await message.answer("✅ Запрос отправлен руководителю направления.")
        else:
            await message.answer("⚠️ РН филиала не найден.")

    # Запрос от СИ (role_id = 3) → РГКС
    elif role_id == ROLES["role_si"]:
        if not await area_exists(area_input):
            await message.answer("❌ Участок не найден.")
            return

        target = await get_rgks_by_area(area_input)
        if target:
            await message.bot.send_message(
                chat_id=target["id"],
                text=build_access_request_message(user, "СИ", area_input),
                reply_markup=build_approval_keyboard(user["id"], role_id, area_input)
            )
            await message.answer("✅ Запрос отправлен руководителю группы.")
        else:
            await message.answer("⚠️ РГКС участка не найден.")

@router.callback_query(F.data.startswith("approve:"))
async def handle_approve(callback: CallbackQuery):
    _, user_id, role_id, area = callback.data.split(":")
    user_id, role_id = int(user_id), int(role_id)

    await update_user_role_area(user_id, role_id, area)
    await callback.message.edit_text("✅ Доступ одобрен.")
    await callback.bot.send_message(user_id, "🎉 Ваша заявка на доступ одобрена!")

@router.callback_query(F.data.startswith("reject:"))
async def handle_reject(callback: CallbackQuery):
    _, user_id, *_ = callback.data.split(":")
    user_id = int(user_id)

    await callback.message.edit_text("❌ Доступ отклонён.")
    await callback.bot.send_message(user_id, "🚫 Ваша заявка на доступ была отклонена.")
