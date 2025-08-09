from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from db.crud.areas import get_area_by_id
from db.crud.branches import get_branch_by_id
from db.crud.users import (
    get_rgks_by_area,
    get_rn_by_branch,
    get_super_admin,
    get_user_by_id,
    set_user_role,
)
from db.db import async_session
from fsm.states import AccessRequest
from keyboards.inline import build_approval_keyboard, select_role_keyboard
from utils.messages import build_access_request_message

router = Router()

ROLES = {
    "role_rn": 1,  # Руководитель направления
    "role_rgks": 2,  # Руководитель группы КС
    "role_si": 3,  # Старший инженер
}


@router.callback_query(F.data == "request_access")
async def start_access(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AccessRequest.selecting_role)
    await callback.message.answer(
        "👤 Кем вы хотите быть в системе?", reply_markup=select_role_keyboard()
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

    async with async_session() as session:
        user = await get_user_by_id(session, message.from_user.id)
        await state.clear()

        if user is None:
            await message.answer(
                "❌ Ошибка: ваш аккаунт не найден в базе данных. Пожалуйста, зарегистрируйтесь."
            )
            return

        area_input = message.text.strip()

        # Запрос от РН → супер-админ
        if role_id == ROLES["role_rn"]:
            branch = await get_branch_by_id(session, area_input)
            if not branch:
                await message.answer("❌ Филиал не найден.")
                return

            admin = await get_super_admin(session)
            if admin:
                await message.bot.send_message(
                    chat_id=admin.id,
                    text=build_access_request_message(user, "РН", area_input),
                    reply_markup=build_approval_keyboard(user.id, role_id, area_input),
                )
                await message.answer("✅ Запрос отправлен администратору.")
            else:
                await message.answer("⚠️ Главный администратор не найден.")

        # Запрос от РГКС → РН
        elif role_id == ROLES["role_rgks"]:
            area = await get_area_by_id(session, area_input)
            if not area:
                await message.answer("❌ Участок не найден.")
                return

            branch_id = area_input.split(".")[0]
            target = await get_rn_by_branch(session, branch_id)
            if target:
                await message.bot.send_message(
                    chat_id=target.id,
                    text=build_access_request_message(user, "РГКС", area_input),
                    reply_markup=build_approval_keyboard(user.id, role_id, area_input),
                )
                await message.answer("✅ Запрос отправлен руководителю направления.")
            else:
                await message.answer("⚠️ РН филиала не найден.")

        # Запрос от СИ → РГКС
        elif role_id == ROLES["role_si"]:
            area = await get_area_by_id(session, area_input)
            if not area:
                await message.answer("❌ Участок не найден.")
                return

            target = await get_rgks_by_area(session, area_input)
            if target:
                await message.bot.send_message(
                    chat_id=target.id,
                    text=build_access_request_message(user, "СИ", area_input),
                    reply_markup=build_approval_keyboard(user.id, role_id, area_input),
                )
                await message.answer("✅ Запрос отправлен руководителю группы.")
            else:
                await message.answer("⚠️ РГКС участка не найден.")


@router.callback_query(F.data.startswith("approve:"))
async def handle_approve(callback: CallbackQuery):
    _, user_id, role_id, area = callback.data.split(":")
    user_id, role_id = int(user_id), int(role_id)

    async with async_session() as session:
        await set_user_role(session, user_id, role_id, area)

    await callback.message.edit_text("✅ Доступ одобрен.")
    await callback.bot.send_message(user_id, "🎉 Ваша заявка на доступ одобрена!")


@router.callback_query(F.data.startswith("reject:"))
async def handle_reject(callback: CallbackQuery):
    _, user_id, *_ = callback.data.split(":")
    user_id = int(user_id)

    await callback.message.edit_text("❌ Доступ отклонён.")
    await callback.bot.send_message(user_id, "🚫 Ваша заявка на доступ была отклонена.")
