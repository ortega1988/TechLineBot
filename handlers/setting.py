from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from fsm.states import SettingsFSM
from aiogram.types import CallbackQuery
from db.crud.users import get_user_by_id, set_default_city_for_user
from db.crud.cities import get_cities_by_branch_id
from keyboards.inline import get_setting_cities_keyboard
from db.db import async_session

router = Router()

@router.callback_query(F.data == "settings")
async def show_settings(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    async with async_session() as session:
        user = await get_user_by_id(session, user_id)
        if not user or not user.branch_id:
            await callback.message.answer("❌ У вас не указан регион.")
            await callback.answer()
            return

        cities = await get_cities_by_branch_id(session, user.branch_id)
        if not cities:
            await callback.message.answer("❌ В вашем регионе нет городов.")
            await callback.answer()
            return

    await callback.message.answer(
        "Выберите город по умолчанию для поиска:",
        reply_markup=get_setting_cities_keyboard(cities, current_city_id=user.default_city_id)
    )
    await state.set_state(SettingsFSM.waiting_for_city_settings)
    await callback.answer()

@router.callback_query(F.data.startswith("settings_city_"))
async def set_default_city_settings(callback: CallbackQuery, state: FSMContext):
    city_id = int(callback.data.replace("settings_city_", ""))
    user_id = callback.from_user.id
    async with async_session() as session:
        await set_default_city_for_user(session, user_id, city_id)
        user = await get_user_by_id(session, user_id)
        cities = await get_cities_by_branch_id(session, user.branch_id)
    await callback.message.edit_text(callback.message.text, reply_markup=get_setting_cities_keyboard(cities, current_city_id=user.default_city_id))
    await state.clear()
    await callback.answer()

