import re
from datetime import datetime

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from db.crud.cities import get_cities_by_area, get_cities_by_branch, get_city_by_id
from db.crud.houses import (
    get_entrance_by_id,
    get_entrances_by_house,
    get_flat_details,
    get_house_by_address,
    get_house_by_entrance_id,
    get_house_by_id,
    set_housing_office_for_house,
)
from db.crud.housing_offices import (
    create_housing_office,
    get_housing_office_by_id,
    get_housing_offices_by_city,
)
from db.crud.parsed_houses import get_house_parsed_view, save_parsed_house_to_db
from db.crud.users import get_user_by_id, set_default_city_for_user
from db.crud.zones import get_zones_by_area_and_city
from db.db import async_session
from fsm.states import AttachHousingOfficeFSM, FindHouseFSM
from keyboards.inline import (
    get_admin_menu,
    get_confirm_add_keyboard,
    get_entrance_menu,
    get_flat_menu,
    get_house_cities_keyboard,
    get_housing_offices_keyboard,
    get_list_houses_menu,
)
from utils.address import detect_city_and_zone_by_address
from utils.messages import build_house_address_info, build_parsed_house_info
from utils.parser import parse_house_from_2gis

router = Router()


@router.callback_query(F.data == "find_house")
async def start_find_house(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    async with async_session() as session:
        user = await get_user_by_id(session, user_id)
        if not user or not user.area_id or user.role_id > 30:
            await callback.message.answer("❌ Нет доступа.")
            await callback.answer()
            return
        if not user.default_city_id:
            # Нет города — предлагаем выбрать
            cities = await get_cities_by_branch(session, user.branch_id)
            await callback.message.answer(
                "Выберите город по умолчанию для поиска:",
                reply_markup=get_house_cities_keyboard(cities),
            )
            await state.set_state(FindHouseFSM.waiting_for_city_auto)
            await callback.answer()
            return
        # город уже выбран — продолжаем обычную логику
        await state.update_data(city_id=user.default_city_id, area_id=user.area_id)
        await callback.message.answer(
            "🏘 Введите адрес дома в формате:\n"
            "<b>Улица Номер</b> (пример: <b>Тимирязева 4</b>)"
        )
        await state.set_state(FindHouseFSM.waiting_for_address)
        await callback.answer()


@router.callback_query(
    FindHouseFSM.waiting_for_city_auto, F.data.startswith("find_house_city_")
)
async def set_default_city_and_continue(callback: CallbackQuery, state: FSMContext):
    city_id = int(callback.data.replace("find_house_city_", ""))
    user_id = callback.from_user.id
    async with async_session() as session:
        await set_default_city_for_user(session, user_id, city_id)
        user = await get_user_by_id(session, user_id)
    await state.update_data(city_id=city_id, area_id=user.area_id)
    await callback.message.answer(
        "🏘 Введите адрес дома в формате:\n"
        "<b>Улица Номер</b> (пример: <b>Тимирязева 4</b>)"
    )
    await state.set_state(FindHouseFSM.waiting_for_address)
    await callback.answer()


@router.message(FindHouseFSM.waiting_for_address)
async def input_address(message: Message, state: FSMContext):
    data = await state.get_data()
    area_id = data["area_id"]
    city_id = data["city_id"]

    parts = message.text.replace(",", " ").split()
    if len(parts) < 2:
        await message.answer(
            "⚠️ Неверный формат.\nВведите <b>улицу и номер дома</b> одним сообщением.\n"
            "Пример: <b>Тимирязева 4</b>"
        )
        return

    street = " ".join(parts[:-1])
    house_number = parts[-1]

    async with async_session() as session:
        # Получаем все районы (zones) для выбранного города и area_id пользователя
        zones = await get_zones_by_area_and_city(
            session, area_id=area_id, city_id=city_id
        )
        if not zones:
            await message.answer("❌ Ваша ГКС не обслуживает этот город.")
            await state.clear()
            return
        zone_ids = [z.id for z in zones]

        # Ищем дом по ВСЕМ районам в зоне ответственности пользователя
        house = None
        found_zone = None
        for zone_id in zone_ids:
            house = await get_house_by_address(
                session=session,
                area_id=area_id,
                zone_id=zone_id,
                street=street,
                house_number=house_number,
            )
            if house:
                found_zone = zone_id
                break

        if house is not None:
            parsed = await get_house_parsed_view(session, house.id)
            if not parsed:
                await message.answer("⚠️ Не удалось получить данные о доме.")
                await state.clear()
                return

            # Можно найти имя зоны (района) для вывода
            zone_obj = next((z for z in zones if z.id == found_zone), None)
            zone_name = zone_obj.name if zone_obj else "—"

            text = build_parsed_house_info(
                parsed_data=parsed,
                db_city_name=parsed["address"].split(",")[0].strip(),
                db_zone_name=zone_name,
                notes=parsed["notes"],
                updated_at=parsed["updated_at"],
                jeu_address=parsed["jeu_address"],
            )
            markup = await get_list_houses_menu(
                housing_office_id=house.housing_office_id,
                house_id=house.id,
                session=session,
            )
            await message.answer(text, reply_markup=markup)
            await state.clear()
            return

        # === Дом не найден в базе, парсим с 2ГИС ===
        city = await get_city_by_id(session, city_id)
        await message.answer("🔍 Дом не найден в базе, ищем в 2ГИС...")

        info = await parse_house_from_2gis(
            city_url=city.url, search_query=f"{street} {house_number}"
        )
        if info is None:
            await message.answer("❌ Дом не найден в 2ГИС.")
            await state.clear()
            return

        # Определяем город и район по адресу (из info)
        city_obj, zone_obj = await detect_city_and_zone_by_address(
            session, info.get("address", "")
        )

        if city_obj is None or city_obj.id != city_id:
            await message.answer(
                "❌ Город из 2ГИС не совпадает с выбранным городом пользователя."
            )
            await state.clear()
            return

        if zone_obj is None or zone_obj.id not in zone_ids:
            await message.answer(
                "❌ Район этого дома не входит в вашу зону ответственности."
            )
            await state.clear()
            return

        # Разбор title для улицы и номера
        title = info.get("title", "")
        if "," in title:
            street_part, number_part = title.rsplit(",", 1)
            parsed_street = street_part.replace("Улица", "").strip()
            parsed_house_number = number_part.strip()
        else:
            parsed_street = street
            parsed_house_number = house_number

        entrances_count = (
            int(re.search(r"(\d+)", info.get("entrances", "")).group(1))
            if re.search(r"(\d+)", info.get("entrances", ""))
            else 1
        )
        floors_count = (
            int(re.search(r"(\d+)", info.get("floors", "")).group(1))
            if re.search(r"(\d+)", info.get("floors", ""))
            else 1
        )

        entrance_info = {}
        for item in info.get("apartments", []):
            parts = item.split(": квартиры ")
            if len(parts) == 2:
                entrance_number = int(parts[0].split()[0])
                flats = parts[1].strip()
                entrance_info[entrance_number] = flats

        text = build_house_address_info(
            city_name=city_obj.name,
            zone_name=zone_obj.name if zone_obj else "Без района",
            street=parsed_street,
            house_number=parsed_house_number,
            floors=floors_count,
            entrances=entrances_count,
            entrance_info=entrance_info,
            notes="Добавлено с 2ГИС",
            updated_at=datetime.now().strftime("%d.%m.%Y %H:%M"),
        )

        await message.answer(text, reply_markup=get_confirm_add_keyboard())

        await state.update_data(
            parsed_house={
                "title": f"{parsed_street} {parsed_house_number}",
                "floors": f"{floors_count} этажей",
                "entrances": f"{entrances_count} подъездов",
                "apartments": [
                    f"{entrance_num} подъезд: квартиры {flats_str}"
                    for entrance_num, flats_str in entrance_info.items()
                ],
                "area_id": area_id,
                "zone_id": zone_obj.id if zone_obj else None,
                "notes": "Добавлено с 2ГИС",
            },
        )

        await state.set_state(FindHouseFSM.confirming_add)


@router.callback_query(
    FindHouseFSM.confirming_add, F.data == "add_housing_office_confirm"
)
async def confirm_add(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    parsed_house_data = data["parsed_house"]
    area_id = data["area_id"]
    zone_id = parsed_house_data["zone_id"]
    user_id = callback.from_user.id

    async with async_session() as session:
        await save_parsed_house_to_db(
            session,
            parsed_data=parsed_house_data,
            area_id=area_id,
            zone_id=zone_id,
            created_by=user_id,
            notes=parsed_house_data.get("notes"),
        )

    await callback.message.edit_text(
        "✅ Дом успешно добавлен!", reply_markup=get_admin_menu()
    )
    await state.clear()
    await callback.answer()


@router.callback_query(F.data.startswith("attach_housing_office:"))
async def attach_housing_office(callback: CallbackQuery, state: FSMContext):
    house_id = int(callback.data.split(":")[1])
    async with async_session() as session:
        house = await get_house_by_id(session, house_id)
        if not house:
            await callback.message.answer("❌ Дом не найден.")
            await callback.answer()
            return

        # У дома есть зона, у зоны есть город
        city_id = house.zone.city_id
        housing_offices = await get_housing_offices_by_city(session, city_id)

        if not housing_offices:
            await callback.message.answer(
                "❌ В этом городе нет зарегистрированных ЖЭУ."
            )
            await callback.answer()
            return

        await state.update_data(house_id=house_id)
        await callback.message.edit_text(
            "Выберите ЖЭУ для привязки:",
            reply_markup=get_housing_offices_keyboard(housing_offices),
        )
        await state.set_state(AttachHousingOfficeFSM.waiting_for_housing_office)
        await callback.answer()


@router.callback_query(
    AttachHousingOfficeFSM.waiting_for_housing_office,
    F.data.startswith("select_housing_office:"),
)
async def select_housing_office(callback: CallbackQuery, state: FSMContext):
    housing_office_id = int(callback.data.split(":")[1])
    data = await state.get_data()
    house_id = data["house_id"]

    async with async_session() as session:
        await set_housing_office_for_house(session, house_id, housing_office_id)
        await callback.message.edit_text("✅ ЖЭУ успешно привязано к дому.")
        # Можно добавить обновление информации о доме, если нужно

    await state.clear()
    await callback.answer()


@router.callback_query(F.data.startswith("house:details"))
async def house_details(callback: CallbackQuery, state: FSMContext):
    house_id = int(callback.data.split(":")[1])
    async with async_session() as session:
        entrances = await get_entrances_by_house(session, house_id)
        text = "Выберите подъезд:\n"
        buttons = []
        for entrance in entrances:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=f"Подъезд №{entrance.entrance_number}",
                        callback_data=f"entrance:details:{entrance.id}",
                    )
                ]
            )
        await callback.message.edit_text(
            text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
        )
        await callback.answer()


@router.callback_query(F.data.startswith("entrance:details"))
async def entrance_details(callback: CallbackQuery, state: FSMContext):
    entrance_id = int(callback.data.split(":")[1])
    async with async_session() as session:
        entrance = await get_entrance_by_id(session, entrance_id)
        text = f"Подъезд №{entrance.entrance_number}\n\n"
        await callback.message.edit_text(
            text, reply_markup=await get_entrance_menu(entrance_id, session)
        )
        await callback.answer()


@router.callback_query(F.data.startswith("flat:details"))
async def flat_details(callback: CallbackQuery, state: FSMContext):
    house_id, flat_number = map(int, callback.data.split(":")[1:])
    async with async_session() as session:
        flat_details = await get_flat_details(
            session, house_id=house_id, flat_number=flat_number
        )
        text = f"Информация о квартире №{flat_number}\n\n"
        if flat_details:
            text += f"Подъезд: {flat_details.entrance.entrance_number}\n"
        else:
            text += "Нет дополнительной информации."
        await callback.message.edit_text(
            text, reply_markup=await get_flat_menu(house_id, flat_number, session)
        )
        await callback.answer()


@router.callback_query(F.data.startswith("view_house:"))
async def view_house(callback: CallbackQuery, state: FSMContext):
    house_id = int(callback.data.split(":")[1])
    async with async_session() as session:
        house = await get_house_by_id(session, house_id)
        parsed = await get_house_parsed_view(session, house.id)
        zone_obj = house.zone
        zone_name = zone_obj.name if zone_obj else "—"
        text = build_parsed_house_info(
            parsed_data=parsed,
            db_city_name=parsed["address"].split(",")[0].strip(),
            db_zone_name=zone_name,
            notes=parsed["notes"],
            updated_at=parsed["updated_at"],
            jeu_address=parsed["jeu_address"],
        )
        markup = await get_list_houses_menu(
            housing_office_id=house.housing_office_id,
            house_id=house.id,
            session=session,
        )
        await callback.message.edit_text(text, reply_markup=markup)
        await callback.answer()


@router.callback_query(F.data.startswith("view_entrance:"))
async def view_entrance(callback: CallbackQuery, state: FSMContext):
    entrance_id = int(callback.data.split(":")[1])
    async with async_session() as session:
        house = await get_house_by_entrance_id(session, entrance_id=entrance_id)
        if house:
            callback.data = f"house:details:{house.id}"
            await house_details(callback, state)
        else:
            await start_find_house(callback, state)


@router.callback_query(F.data.startswith("view_flat:"))
async def view_flat(callback: CallbackQuery, state: FSMContext):
    house_id, flat_number = map(int, callback.data.split(":")[1:])
    async with async_session() as session:
        entrance = await get_entrance_by_flat_number(
            session, house_id=house_id, flat_number=flat_number
        )
        if entrance:
            callback.data = f"entrance:details:{entrance.id}"
            await entrance_details(callback, state)
        else:
            callback.data = f"house:details:{house_id}"
            await house_details(callback, state)
