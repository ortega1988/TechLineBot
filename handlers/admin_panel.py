from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from keyboards.inline import get_admin_menu
from aiogram.fsm.context import FSMContext

from db.db import db

router = Router()


@router.callback_query(F.data == "admin_panel")
async def open_admin_menu(callback: CallbackQuery):
    await callback.message.edit_text("🛠 Меню администрирования:", reply_markup=get_admin_menu())