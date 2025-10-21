from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from db.crud.comments import (
    count_entrance_comments,
    count_flat_comments,
    count_house_comments,
    create_entrance_comment,
    create_flat_comment,
    create_house_comment,
    delete_entrance_comment,
    delete_flat_comment,
    delete_house_comment,
    get_comments_by_entrance_id,
    get_comments_by_flat_number,
    get_comments_by_house_id,
    get_entrance_comment_by_id,
    get_flat_comment_by_id,
    get_house_comment_by_id,
    update_entrance_comment,
    update_flat_comment,
    update_house_comment,
)
from db.crud.houses import get_entrance_by_flat_number, get_house_by_entrance_id
from db.crud.users import get_user_by_id, get_users_by_role
from db.db import async_session
from keyboards.inline import get_comments_keyboard

router = Router()


async def notify_admins_about_new_comment(bot, house_id: int, text: str, user_name: str):
    async with async_session() as session:
        admins = await get_users_by_role(session, role_id=10)  # Assuming admin role_id is 10
        for admin in admins:
            await bot.send_message(
                admin.id,
                f"Новый комментарий к дому #{house_id} от {user_name}:\n\n{text}",
            )


class CommentFSM(StatesGroup):
    waiting_for_house_comment = State()
    waiting_for_house_comment_edit = State()
    waiting_for_entrance_comment = State()
    waiting_for_entrance_comment_edit = State()
    waiting_for_flat_comment = State()
    waiting_for_flat_comment_edit = State()


# House Comments
@router.callback_query(F.data.startswith("add_comment_house:"))
async def add_house_comment_start(callback: CallbackQuery, state: FSMContext):
    house_id = int(callback.data.split(":")[1])
    await state.update_data(house_id=house_id)
    await callback.message.answer("Введите ваш комментарий:")
    await state.set_state(CommentFSM.waiting_for_house_comment)
    await callback.answer()


@router.message(CommentFSM.waiting_for_house_comment)
async def add_house_comment_process(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    house_id = data["house_id"]
    user_id = message.from_user.id
    text = message.text

    async with async_session() as session:
        await create_house_comment(
            session, house_id=house_id, user_id=user_id, text=text
        )
        await message.answer("✅ Комментарий к дому успешно добавлен.")
        await notify_admins_about_new_comment(
            bot, house_id, text, message.from_user.full_name
        )

    await state.clear()


@router.callback_query(F.data.startswith("view_comments_house:"))
async def view_house_comments(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split(":")
    house_id = int(parts[1])
    page = int(parts[2]) if len(parts) > 2 else 1

    async with async_session() as session:
        comments = await get_comments_by_house_id(
            session, house_id=house_id, page=page
        )
        total_comments = await count_house_comments(session, house_id=house_id)

    if not comments:
        await callback.message.answer("К этому дому пока нет комментариев.")
        await callback.answer()
        return

    text = "💬 Комментарии к дому:\n\n"
    for comment in comments:
        text += f"<b>От:</b> {comment.user.full_name}\n"
        text += f"<b>Комментарий:</b> {comment.text}\n"
        text += f"<b>Дата:</b> {comment.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"

    await callback.message.answer(
        text,
        reply_markup=get_comments_keyboard(
            "house", house_id, page, total_comments, 0
        ),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("edit_comment_house:"))
async def edit_house_comment_start(callback: CallbackQuery, state: FSMContext):
    comment_id = int(callback.data.split(":")[1])
    async with async_session() as session:
        comment = await get_house_comment_by_id(session, comment_id=comment_id)
        if not comment:
            await callback.message.answer("❌ Комментарий не найден.")
            await callback.answer()
            return

        user = await get_user_by_id(session, callback.from_user.id)
        if not (comment.user_id == user.id or user.role_id <= 10):
            await callback.message.answer("❌ У вас нет прав для редактирования этого комментария.")
            await callback.answer()
            return

    await state.update_data(comment_id=comment_id)
    await callback.message.answer("Введите новый текст комментария:")
    await state.set_state(CommentFSM.waiting_for_house_comment_edit)
    await callback.answer()


@router.message(CommentFSM.waiting_for_house_comment_edit)
async def edit_house_comment_process(message: Message, state: FSMContext):
    data = await state.get_data()
    comment_id = data["comment_id"]
    text = message.text

    async with async_session() as session:
        await update_house_comment(session, comment_id=comment_id, text=text)
        await message.answer("✅ Комментарий к дому успешно изменен.")

    await state.clear()


@router.callback_query(F.data.startswith("delete_comment_house:"))
async def delete_house_comment_process(callback: CallbackQuery, state: FSMContext):
    comment_id = int(callback.data.split(":")[1])

    async with async_session() as session:
        comment = await get_house_comment_by_id(session, comment_id=comment_id)
        if not comment:
            await callback.message.answer("❌ Комментарий не найден.")
            await callback.answer()
            return

        user = await get_user_by_id(session, callback.from_user.id)
        if not (comment.user_id == user.id or user.role_id <= 10):
            await callback.message.answer("❌ У вас нет прав для удаления этого комментария.")
            await callback.answer()
            return

        await delete_house_comment(session, comment_id=comment_id)
        await callback.message.answer("✅ Комментарий к дому успешно удален.")

    await callback.answer()


# Entrance Comments
@router.callback_query(F.data.startswith("add_comment_entrance:"))
async def add_entrance_comment_start(callback: CallbackQuery, state: FSMContext):
    entrance_id = int(callback.data.split(":")[1])
    await state.update_data(entrance_id=entrance_id)
    await callback.message.answer("Введите ваш комментарий:")
    await state.set_state(CommentFSM.waiting_for_entrance_comment)
    await callback.answer()


@router.message(CommentFSM.waiting_for_entrance_comment)
async def add_entrance_comment_process(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    entrance_id = data["entrance_id"]
    user_id = message.from_user.id
    text = message.text

    async with async_session() as session:
        comment = await create_entrance_comment(
            session, entrance_id=entrance_id, user_id=user_id, text=text
        )
        house = await get_house_by_entrance_id(session, entrance_id=entrance_id)
        await message.answer("✅ Комментарий к подъезду успешно добавлен.")
        if house:
            await notify_admins_about_new_comment(
                bot, house.id, text, message.from_user.full_name
            )

    await state.clear()


@router.callback_query(F.data.startswith("view_comments_entrance:"))
async def view_entrance_comments(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split(":")
    entrance_id = int(parts[1])
    page = int(parts[2]) if len(parts) > 2 else 1

    async with async_session() as session:
        comments = await get_comments_by_entrance_id(
            session, entrance_id=entrance_id, page=page
        )
        total_comments = await count_entrance_comments(session, entrance_id=entrance_id)

    if not comments:
        await callback.message.answer("К этому подъезду пока нет комментариев.")
        await callback.answer()
        return

    text = "💬 Комментарии к подъезду:\n\n"
    for comment in comments:
        text += f"<b>От:</b> {comment.user.full_name}\n"
        text += f"<b>Комментарий:</b> {comment.text}\n"
        text += f"<b>Дата:</b> {comment.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"

    await callback.message.answer(
        text,
        reply_markup=get_comments_keyboard(
            "entrance", entrance_id, page, total_comments, 0
        ),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("edit_comment_entrance:"))
async def edit_entrance_comment_start(callback: CallbackQuery, state: FSMContext):
    comment_id = int(callback.data.split(":")[1])
    async with async_session() as session:
        comment = await get_entrance_comment_by_id(session, comment_id=comment_id)
        if not comment:
            await callback.message.answer("❌ Комментарий не найден.")
            await callback.answer()
            return

        user = await get_user_by_id(session, callback.from_user.id)
        if not (comment.user_id == user.id or user.role_id <= 10):
            await callback.message.answer("❌ У вас нет прав для редактирования этого комментария.")
            await callback.answer()
            return

    await state.update_data(comment_id=comment_id)
    await callback.message.answer("Введите новый текст комментария:")
    await state.set_state(CommentFSM.waiting_for_entrance_comment_edit)
    await callback.answer()


@router.message(CommentFSM.waiting_for_entrance_comment_edit)
async def edit_entrance_comment_process(message: Message, state: FSMContext):
    data = await state.get_data()
    comment_id = data["comment_id"]
    text = message.text

    async with async_session() as session:
        await update_entrance_comment(session, comment_id=comment_id, text=text)
        await message.answer("✅ Комментарий к подъезду успешно изменен.")

    await state.clear()


@router.callback_query(F.data.startswith("delete_comment_entrance:"))
async def delete_entrance_comment_process(callback: CallbackQuery, state: FSMContext):
    comment_id = int(callback.data.split(":")[1])

    async with async_session() as session:
        comment = await get_entrance_comment_by_id(session, comment_id=comment_id)
        if not comment:
            await callback.message.answer("❌ Комментарий не найден.")
            await callback.answer()
            return

        user = await get_user_by_id(session, callback.from_user.id)
        if not (comment.user_id == user.id or user.role_id <= 10):
            await callback.message.answer("❌ У вас нет прав для удаления этого комментария.")
            await callback.answer()
            return

        await delete_entrance_comment(session, comment_id=comment_id)
        await callback.message.answer("✅ Комментарий к подъезду успешно удален.")

    await callback.answer()


# Flat Comments
@router.callback_query(F.data.startswith("add_comment_flat:"))
async def add_flat_comment_start(callback: CallbackQuery, state: FSMContext):
    house_id, flat_number = map(int, callback.data.split(":")[1:])
    await state.update_data(house_id=house_id, flat_number=flat_number)
    await callback.message.answer("Введите ваш комментарий:")
    await state.set_state(CommentFSM.waiting_for_flat_comment)
    await callback.answer()


@router.message(CommentFSM.waiting_for_flat_comment)
async def add_flat_comment_process(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    house_id = data["house_id"]
    flat_number = data["flat_number"]
    user_id = message.from_user.id
    text = message.text

    async with async_session() as session:
        entrance = await get_entrance_by_flat_number(session, house_id=house_id, flat_number=flat_number)
        entrance_id = entrance.id if entrance else None
        await create_flat_comment(
            session,
            house_id=house_id,
            flat_number=flat_number,
            user_id=user_id,
            text=text,
            entrance_id=entrance_id,
        )
        await message.answer("✅ Комментарий к квартире успешно добавлен.")
        await notify_admins_about_new_comment(
            bot, house_id, text, message.from_user.full_name
        )

    await state.clear()


@router.callback_query(F.data.startswith("view_comments_flat:"))
async def view_flat_comments(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split(":")
    house_id, flat_number = map(int, parts[1:3])
    page = int(parts[3]) if len(parts) > 3 else 1

    async with async_session() as session:
        comments = await get_comments_by_flat_number(
            session, house_id=house_id, flat_number=flat_number, page=page
        )
        total_comments = await count_flat_comments(
            session, house_id=house_id, flat_number=flat_number
        )

    if not comments:
        await callback.message.answer("К этой квартире пока нет комментариев.")
        await callback.answer()
        return

    text = f"💬 Комментарии к квартире №{flat_number}:\n\n"
    for comment in comments:
        text += f"<b>От:</b> {comment.user.full_name}\n"
        text += f"<b>Комментарий:</b> {comment.text}\n"
        text += f"<b>Дата:</b> {comment.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"

    await callback.message.answer(
        text,
        reply_markup=get_comments_keyboard(
            "flat", house_id, page, total_comments, flat_number
        ),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("edit_comment_flat:"))
async def edit_flat_comment_start(callback: CallbackQuery, state: FSMContext):
    comment_id = int(callback.data.split(":")[1])
    async with async_session() as session:
        comment = await get_flat_comment_by_id(session, comment_id=comment_id)
        if not comment:
            await callback.message.answer("❌ Комментарий не найден.")
            await callback.answer()
            return

        user = await get_user_by_id(session, callback.from_user.id)
        if not (comment.user_id == user.id or user.role_id <= 10):
            await callback.message.answer("❌ У вас нет прав для редактирования этого комментария.")
            await callback.answer()
            return

    await state.update_data(comment_id=comment_id)
    await callback.message.answer("Введите новый текст комментария:")
    await state.set_state(CommentFSM.waiting_for_flat_comment_edit)
    await callback.answer()


@router.message(CommentFSM.waiting_for_flat_comment_edit)
async def edit_flat_comment_process(message: Message, state: FSMContext):
    data = await state.get_data()
    comment_id = data["comment_id"]
    text = message.text

    async with async_session() as session:
        await update_flat_comment(session, comment_id=comment_id, text=text)
        await message.answer("✅ Комментарий к квартире успешно изменен.")

    await state.clear()


@router.callback_query(F.data.startswith("delete_comment_flat:"))
async def delete_flat_comment_process(callback: CallbackQuery, state: FSMContext):
    comment_id = int(callback.data.split(":")[1])

    async with async_session() as session:
        comment = await get_flat_comment_by_id(session, comment_id=comment_id)
        if not comment:
            await callback.message.answer("❌ Комментарий не найден.")
            await callback.answer()
            return

        user = await get_user_by_id(session, callback.from_user.id)
        if not (comment.user_id == user.id or user.role_id <= 10):
            await callback.message.answer("❌ У вас нет прав для удаления этого комментария.")
            await callback.answer()
            return

        await delete_flat_comment(session, comment_id=comment_id)
        await callback.message.answer("✅ Комментарий к квартире успешно удален.")

    await callback.answer()
