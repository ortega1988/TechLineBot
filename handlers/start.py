from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import async_session
from db.crud.users import get_user_by_id, create_user
from db.crud.roles import get_role_name

from keyboards.inline import request_access_keyboard, build_main_menu





router = Router()

NEWBIE_ROLE_ID = 50


@router.message(CommandStart())
async def handle_start(message: Message):
    tg_id = message.from_user.id

    session: AsyncSession
    async with async_session() as session:
        user = await get_user_by_id(session, tg_id)
        role_name = await get_role_name(session, user.role_id) if user else None

        match user:
            case None:
                await create_user(
                    session=session,
                    user_id=tg_id,
                    full_name=message.from_user.full_name,
                    username=message.from_user.username,
                    role_id=NEWBIE_ROLE_ID,
                )

                await message.answer(
                    "👋 Добро пожаловать!\n"
                    "Вы зарегистрированы как <b>новичок</b>.\n"
                    "Пожалуйста, нажмите кнопку ниже, чтобы запросить доступ.",
                    reply_markup=request_access_keyboard(),
                )

            case _ if user.role_id in (0, 1, 2, 3):
                await message.answer(
                    f"👋 Добро пожаловать, {user.full_name}!\n"
                    f"Вы вошли как <b>{role_name}</b>.",
                    reply_markup=build_main_menu(user.role_id),
                )

            case _ if user.role_id == NEWBIE_ROLE_ID:
                await message.answer(
                    f"👋 С возвращением, {user.full_name}!\n"
                    "У вас пока нет доступа. Нажмите кнопку ниже, чтобы его запросить.",
                    reply_markup=request_access_keyboard(),
                )

            case _:
                await message.answer(
                    "⚠️ Неизвестная роль. Пожалуйста, обратитесь к администратору."
                )