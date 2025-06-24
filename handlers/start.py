from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart

from db.queries import get_user, insert_new_user, get_role_name, NEWBIE_ROLE_ID
from keyboards.inline import request_access_keyboard, build_main_menu

router = Router()

@router.message(CommandStart())
async def handle_start(message: Message):
    tg_id = message.from_user.id
    user = await get_user(tg_id)

    if user:
        role_name = await get_role_name(user["role_id"])
    else:
        role_name = None

    match user:
        case None:
            # регистрируем
            await insert_new_user(
                tg_id,
                message.from_user.full_name,
                message.from_user.username
            )
            await message.answer(
                "👋 Добро пожаловать!\n"
                "Вы зарегистрированы как <b>новичок</b>.\n"
                "Пожалуйста, нажмите кнопку ниже, чтобы запросить доступ.",
                reply_markup=request_access_keyboard()
            )

        case _ if user["role_id"] == 3:
            await message.answer(
                f"👋 Добро пожаловать, {user['full_name']}!\n"
                f"Вы вошли как <b>{role_name}</b>.",
                reply_markup=build_main_menu(user["role_id"])
            )

        case _ if user["role_id"] < 3:
            await message.answer(
                f"👋 Добро пожаловать, {user['full_name']}!\n"
                f"Вы вошли как <b>{role_name}</b>.",
                reply_markup=build_main_menu(user["role_id"])
            )

        case _ if user["role_id"] == NEWBIE_ROLE_ID:
            await message.answer(
                f"👋 С возвращением, {user['full_name']}!\n"
                "У вас пока нет доступа. Нажмите кнопку ниже, чтобы его запросить.",
                reply_markup=request_access_keyboard()
            )

        case _:
            await message.answer("⚠️ Неизвестная роль. Пожалуйста, обратитесь к администратору.")
