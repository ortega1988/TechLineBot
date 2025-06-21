from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from db.db import db
from keyboards.inline import request_access_keyboard, build_main_menu

router = Router()

@router.message(CommandStart())
async def handle_start(message: Message):
    tg_id = message.from_user.id
    user = await db.fetchone("SELECT * FROM users WHERE id = %s", (tg_id,))
    if user:
        role = await db.fetchone("SELECT name FROM roles WHERE id = %s", (user["role_id"],))
        role_name = role["name"] if role else f"Роль {user['role_id']}"
    

    match user:
        # 🔹 1. Юзера нет в БД — регистрируем как новичка
        case None:
            await db.execute("""
                INSERT INTO users (id, full_name, username, role_id)
                VALUES (%s, %s, %s, %s)
            """, (
                tg_id,
                message.from_user.full_name,
                message.from_user.username,
                50  # Новичок
            ))
            await message.answer(
                "👋 Добро пожаловать!\n"
                "Вы зарегистрированы как <b>новичок</b>.\n"
                "Пожалуйста, нажмите кнопку ниже, чтобы запросить доступ.",
                reply_markup=request_access_keyboard()
            )

        # 🔹 2. Роль = 3 (старший инженер) — меню без админки
        case _ if user["role_id"] == 3:
            role = await db.fetchone("SELECT name FROM roles WHERE id = %s", (user["role_id"],))
            role_name = role["name"] if role else f"Роль {user['role_id']}"
            await message.answer(
                f"👋 Добро пожаловать, {user['full_name']}!\nВы вошли как <b>{role_name}</b>.",
                reply_markup=build_main_menu(user["role_id"])
            )

        # 🔹 3. Роль < 3 (руководитель ГКС, направления, админ) — меню с админкой
        case _ if user["role_id"] < 3:
            await message.answer(
                f"👋 Добро пожаловать, {user['full_name']}!\nВы вошли как <b>{role_name}</b>.",
                reply_markup=build_main_menu(user["role_id"])
            )

        # 🔹 4. Роль = 50 (новичок) — запрос доступа
        case _ if user["role_id"] == 50:
            await message.answer(
                f"👋 С возвращением, {user['full_name']}!\n"
                "У вас пока нет доступа. Нажмите кнопку ниже, чтобы его запросить.",
                reply_markup=request_access_keyboard()
            )
            
        case _:
            await message.answer("⚠️ Неизвестная роль. Пожалуйста, обратитесь к администратору.")