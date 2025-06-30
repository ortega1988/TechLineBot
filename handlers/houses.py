from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from fsm.states import FindHouseFSM
from db.db import async_session
from db.crud.users import get_user_by_id
from db.crud.houses import get_house_by_address, create_house_with_entrances, get_entrances_by_house
from db.crud.zones import get_zone_by_area
from keyboards.inline import get_list_gks_menu, get_confirm_add_keyboard
from utils.messages import build_house_address_info
from utils.parser import parse_house_from_2gis
from utils.address import detect_city_and_zone_by_address

from datetime import datetime
import re

router = Router()


@router.callback_query(F.data == "find_house")
async def start_find_house(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    async with async_session() as session:
        user = await get_user_by_id(session, user_id)

        if user is None or not user.area_id:
            await callback.message.answer("❌ У вас не указан участок. Пожалуйста, обратитесь к администратору.")
            await callback.answer()
            return

        zone = await get_zone_by_area(session, user.area_id)

        if zone is None:
            await callback.message.answer("❌ Не удалось определить город и район по вашему участку.")
            await callback.answer()
            return

        await state.update_data(
            area_id=user.area_id,
            city=zone.city,
            zone_name=zone.name
        )

    await callback.message.answer(
        "🏘 Введите адрес дома в формате:\n"
        "<b>Улица Номер</b> (пример: <b>Тимирязева 4</b> или <b>Ленина 5А</b>)"
    )
    await state.set_state(FindHouseFSM.waiting_for_address)
    await callback.answer()


@router.message(FindHouseFSM.waiting_for_address)
async def input_address(message: Message, state: FSMContext):
    data = await state.get_data()
    area_id = data["area_id"]

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
        house = await get_house_by_address(
            session,
            city=data["city"],
            area_id=area_id,
            street=street,
            house_number=house_number
        )

        if house is None:
            await message.answer("🔍 Дом не найден в базе, ищем в 2ГИС...")

            info = await parse_house_from_2gis(
                city_url=data["city"].url,
                search_query=f"{street} {house_number}"
            )

            if info is None:
                await message.answer("❌ Дом не найден в 2ГИС.")
                await state.clear()
                return

            city, zone = await detect_city_and_zone_by_address(session, info.get("address", ""))

            if city is None:
                await message.answer("❌ Не удалось определить город по адресу.")
                await state.clear()
                return

            if zone is None:
                await message.answer(f"🏙️ Город {city.name} найден, район не определён.")
            else:
                await message.answer(f"🏙️ Город: {city.name}, район: {zone.name}")

            # Разбор title для улицы и номера
            title = info.get('title', '')
            if ',' in title:
                street_part, number_part = title.rsplit(',', 1)
                parsed_street = street_part.replace('Улица', '').strip()
                parsed_house_number = number_part.strip()
            else:
                parsed_street = street
                parsed_house_number = house_number

            # Количество подъездов
            entrances_match = re.search(r'(\d+)', info.get('entrances', ''))
            entrances_count = int(entrances_match.group(1)) if entrances_match else 1

            # Количество этажей
            floors_match = re.search(r'(\d+)', info.get('floors', ''))
            floors_count = int(floors_match.group(1)) if floors_match else 1

            # Формирование данных по подъездам
            entrance_info = {}
            for item in info.get('apartments', []):
                parts = item.split(": квартиры ")
                if len(parts) == 2:
                    entrance_number = int(parts[0].split()[0])
                    flats = parts[1].strip()
                    entrance_info[entrance_number] = flats

            text = build_house_address_info(
                city_name=city.name,
                zone_name=zone.name if zone else 'Без района',
                street=parsed_street,
                house_number=parsed_house_number,
                floors=floors_count,
                entrances=entrances_count,
                entrance_info=entrance_info,
                notes="Добавлено с 2ГИС",
                updated_at=datetime.now().strftime("%d.%m.%Y %H:%M")
            )

            await message.answer(text, reply_markup=get_confirm_add_keyboard())

            await state.update_data(
                parsed_house={
                    "street": parsed_street,
                    "house_number": parsed_house_number,
                    "floors": floors_count,
                    "entrances": entrances_count,
                    "entrance_info": entrance_info,
                    "zone_id": zone.id if zone else None,
                    "notes": f"Добавлено автоматически с 2ГИС. Адрес: {info.get('address')}"
                }
            )

            await state.set_state(FindHouseFSM.confirming_add)
            return

        else:
            entrances = await get_entrances_by_house(session, house.id)

    entrances_data = []
    for entrance in entrances:
        flats_range = entrance.flats_text or "Не указано"
        entrances_data.append({
            'entrance_number': entrance.entrance_number,
            'floors': entrance.floors or 'Не указано',
            'flats_range': flats_range
        })

    text = build_house_address_info(
        city_name=house.zone.city.name,
        zone_name=house.zone.name,
        street=house.street,
        house_number=house.house_number,
        floors=house.floors,
        entrances=house.entrances,
        entrance_info={e['entrance_number']: e['flats_range'] for e in entrances_data},
        notes=house.notes,
        updated_at=house.updated_at.strftime("%d.%m.%Y %H:%M")
    )

    await message.answer(text, reply_markup=get_list_gks_menu())
    await state.clear()
