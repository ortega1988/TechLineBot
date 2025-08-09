from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from keyboards.inline import get_admin_menu

router = Router()


@router.callback_query(F.data == "admin_panel")
async def open_admin_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "🛠 Меню администрирования:", reply_markup=get_admin_menu()
    )
