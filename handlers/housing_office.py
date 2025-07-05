from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from fsm.states import AddHousingOffice2GISFSM
from db.db import async_session
from db.crud.housing_offices import create_housing_office
from db.crud.users import get_user_by_id
from db.crud.zones import get_zone_by_area
from db.models import City
from utils.parser import parse_housing_office_from_2gis
from keyboards.inline import get_admin_menu
from keyboards.inline import get_confirm_add_housing_office_keyboard

router = Router()

@router.callback_query(F.data == "add_housing_office")
async def start_add(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите <b>название ЖЭУ</b> для поиска в 2ГИС:")
    await state.set_state(AddHousingOffice2GISFSM.waiting_for_name)
    await callback.answer()

@router.message(AddHousingOffice2GISFSM.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    user_id = message.from_user.id

    async with async_session() as session:
        user = await get_user_by_id(session, user_id)
        if not user or not user.area_id:
            await message.answer("❌ Не удалось определить ваш участок. Обратитесь к администратору.")
            await state.clear()
            return

        # Определяем зону и город по area пользователя
        zone = await get_zone_by_area(session, user.area_id)
        if not zone or not zone.city:
            await message.answer("❌ Не удалось определить город по вашему участку. Обратитесь к администратору.")
            await state.clear()
            return

        city: City = zone.city
        city_url = city.url
        name = message.text.strip()

        await message.answer(f"🔎 Ищем ЖЭУ <b>{name}</b> в городе <b>{city.name}</b> через 2ГИС...")

        result = await parse_housing_office_from_2gis(city_url=city_url, org_name=name)
        if not result:
            await message.answer("❌ ЖЭУ не найдено в 2ГИС. Попробуйте еще раз или обратитесь к администратору.")
            await state.clear()
            return

        await state.update_data(parsed=result)
        text = (
            f"<b>Проверьте данные:</b>\n\n"
            f"🏢 <b>Название:</b> {result['title']}\n"
            f"📍 <b>Адрес:</b> {result['address']}\n"
            f"☎️ <b>Телефон:</b> {result['phone'] or '—'}\n"
            f"⏰ <b>Время работы:</b> {result['working_hours'] or '—'}\n"
            f"💬 <b>Комментарии:</b> {result['comments'] or '—'}"
        )
        await message.answer(text, reply_markup=get_confirm_add_housing_office_keyboard())
        await state.set_state(AddHousingOffice2GISFSM.confirming_add)

@router.callback_query(AddHousingOffice2GISFSM.confirming_add, F.data == "add_housing_office_confirm")
async def confirm_add(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    result = data["parsed"]

    async with async_session() as session:
        await create_housing_office(
            session=session,
            name=result.get("title", ""),
            address=result.get("address", ""),
            comments=result.get("comments", ""),
            working_hours=result.get("working_hours", ""),
            phone=result.get("phone", ""),
        )
    await callback.message.edit_text("✅ ЖЭУ успешно добавлено!", reply_markup=get_admin_menu())
    await state.clear()
    await callback.answer()
