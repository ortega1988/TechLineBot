from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from fsm.states import AccessRequest
from db.db import db
from keyboards.inline import select_role_keyboard
from keyboards.inline import build_approval_keyboard
from utils.messages import build_access_request_message


router = Router()

SUPER_ADMIN_ROLE = 0
ROLES = {
    "role_rn": 1,
    "role_rgks": 2,
    "role_si": 3,
}

@router.callback_query(F.data == "request_access")
async def start_access(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AccessRequest.selecting_role)
    await callback.message.answer("👤 Кем вы хотите быть в системе?", reply_markup=select_role_keyboard())
    await callback.answer()


@router.callback_query(F.data.in_(ROLES.keys()))
async def handle_role_selection(callback: CallbackQuery, state: FSMContext):
    role_key = callback.data
    role_id = ROLES[role_key]
    await state.update_data(role_id=role_id)

    await state.set_state(AccessRequest.entering_area)
    await callback.message.answer("📍 Введите номер участка (например, <code>16.2</code>) или филиала (<code>16</code>) в зависимости от выбранной роли:")
    await callback.answer()


@router.message(AccessRequest.entering_area)
async def handle_area_input(message: Message, state: FSMContext):
    data = await state.get_data()
    role_id = data["role_id"]
    user = await db.fetchone("SELECT * FROM users WHERE id = %s", (message.from_user.id,))
    await state.clear()

    area_input = message.text.strip()

    # Запрос от РН (роль 1) → главному админу
    if role_id == 1:
        exists = await db.fetchone("SELECT * FROM branches WHERE id = %s", (area_input,))
        if not exists:
            await message.answer("❌ Филиал не найден.")
            return

        admin = await db.fetchone("SELECT id FROM users WHERE role_id = %s", (SUPER_ADMIN_ROLE,))
        if admin:
            await message.bot.send_message(
                chat_id=admin["id"],
                text=build_access_request_message(user, "РН", area_input),
                reply_markup=build_approval_keyboard(user["id"], role_id, area_input)
            )
            await message.answer("✅ Запрос отправлен администратору.")
        else:
            await message.answer("⚠️ Главный администратор не найден.")

    # Запрос от РГКС (2) → РН
    elif role_id == 2:
        exists = await db.fetchone("SELECT * FROM areas WHERE id = %s", (area_input,))
        if not exists:
            await message.answer("❌ Участок не найден.")
            return

        branch_id = area_input.split(".")[0]
        target = await db.fetchone("SELECT id FROM users WHERE branch_id = %s AND role_id = 1", (branch_id,))
        if target:
            await message.bot.send_message(
                chat_id=target["id"],
                text=build_access_request_message(user, "РГКС", area_input),
                reply_markup=build_approval_keyboard(user["id"], role_id, area_input)
            )
            await message.answer("✅ Запрос отправлен руководителю направления.")
        else:
            await message.answer("⚠️ РН филиала не найден.")

    # Запрос от СИ (3) → РГКС
    elif role_id == 3:
        exists = await db.fetchone("SELECT * FROM areas WHERE id = %s", (area_input,))
        if not exists:
            await message.answer("❌ Участок не найден.")
            return

        target = await db.fetchone("SELECT id FROM users WHERE area_id = %s AND role_id = 2", (area_input,))
        if target:
            await message.bot.send_message(
                chat_id=target["id"],
                text=build_access_request_message(user, "СИ", area_input),
                reply_markup=build_approval_keyboard(user["id"], role_id, area_input)
            )
            await message.answer("✅ Запрос отправлен руководителю группы.")
        else:
            await message.answer("⚠️ РГКС участка не найден.")


router.callback_query(F.data.startswith("approve:"))
async def handle_approve(callback: CallbackQuery):
    _, user_id, role_id, area = callback.data.split(":")
    user_id, role_id = int(user_id), int(role_id)

    # Назначаем роль и участок/филиал
    await db.execute("""
        UPDATE users 
        SET role_id = %s, 
            area_id = %s, 
            is_active = TRUE 
        WHERE id = %s
    """, (role_id, area, user_id))

    await callback.message.edit_text("✅ Доступ одобрен.")
    await callback.bot.send_message(user_id, "🎉 Ваша заявка на доступ одобрена!")

@router.callback_query(F.data.startswith("reject:"))
async def handle_reject(callback: CallbackQuery):
    _, user_id, role_id, area = callback.data.split(":")
    user_id = int(user_id)

    await callback.message.edit_text("❌ Доступ отклонён.")
    await callback.bot.send_message(user_id, "🚫 Ваша заявка на доступ была отклонена.")