from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from fsm.states import AddHousingOffice2GISFSM
from db.db import async_session
from db.crud.housing_offices import create_housing_office
from db.crud.users import get_user_by_id
from db.crud.cities import get_city_by_id
from utils.parser import parse_housing_office_from_2gis
from utils.address import resolve_city_zone_from_comment
from db.crud.zones import get_zones_by_area, get_zones_by_city
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
        if not user or not user.default_city_id:
            await message.answer(
                "❌ У вас не выбран город по умолчанию. "
                "Пожалуйста, укажите его в настройках и попробуйте снова."
            )
            await state.clear()
            return

        city = await get_city_by_id(session, user.default_city_id)
        if not city:
            await message.answer("❌ Не удалось найти город по умолчанию. Обратитесь к администратору.")
            await state.clear()
            return

        city_url = city.url
        name = message.text.strip()

        await message.answer(f"🔎 Ищем ЖЭУ <b>{name}</b> в городе <b>{city.name}</b> через 2ГИС...")

        result = await parse_housing_office_from_2gis(city_url=city_url, org_name=name)
        if not result:
            await message.answer("❌ ЖЭУ не найдено в 2ГИС. Попробуйте еще раз или обратитесь к администратору.")
            await state.clear()
            return

        # Найти район по комментарию — только если он действительно есть!
        zones = await get_zones_by_city(session, city.id)
        zone_obj = next(
            (zone for zone in zones if zone.name.lower() in result.get("comments", "").lower()),
            None
        )
        if not zone_obj:
            await message.answer(
                "❌ Район (зона) из комментария не найден в базе.\n"
                "Добавьте сначала этот район, а потом повторите добавление ЖЭУ."
            )
            await state.clear()
            return
        city_name = city.name
        zone_name = zone_obj.name
        parsed_address = result["address"]  # например: "Улица Адоратского, 12а, 1 этаж"

        # Тыдели из address только улицу, номер и этаж (можно через split и join)
        address_parts = [city_name, zone_name] + [x.strip() for x in parsed_address.split(",")]
        formatted_address = ", ".join(address_parts)  # Казань, Ново-Савиновский, Улица Адоратского, 12а, 1 этаж

        # В комментарии всегда только это:
        comments = "Добавлено с 2ГИС"

        # Обновляем state с zone_id
        await state.update_data(parsed=result, city_id=city.id, zone_id=zone_obj.id)
        text = (
            f"🏢 <b>Название:</b> {result['title']}\n"
            f"📍 <b>Адрес:</b> {formatted_address}\n"
            f"🗺 <b>Район (зона):</b> {zone_name}\n"
            f"☎️ <b>Телефон:</b> {result['phone'] or '—'}\n"
            f"⏰ <b>Время работы:</b> {result['working_hours'] or '—'}\n"
            f"💬 <b>Комментарии:</b> {comments}"
        )
        await message.answer(text, reply_markup=get_confirm_add_housing_office_keyboard())
        await state.set_state(AddHousingOffice2GISFSM.confirming_add)


@router.callback_query(AddHousingOffice2GISFSM.confirming_add, F.data == "add_housing_office_confirm")
async def confirm_add(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    result = data["parsed"]

    async with async_session() as session:
        user = await get_user_by_id(session, callback.from_user.id)
        city_id, zone_id = await resolve_city_zone_from_comment(session, user, result.get("comments", ""))

        if not city_id or not zone_id:
            await state.clear()
            await callback.answer()
            return

        await create_housing_office(
            session=session,
            name=result.get("title", ""),
            address=result.get("address", ""),
            city_id=city_id,
            zone_id=zone_id,
            comments="добавлено с 2ГИС",
            working_hours=result.get("working_hours", ""),
            phone=result.get("phone", ""),
            email="",       # если email не парсится
            photo_url="",   # если фото не парсится
        )
    await callback.message.edit_text("✅ ЖЭУ успешно добавлено!", reply_markup=get_admin_menu())
    await state.clear()
    await callback.answer()
