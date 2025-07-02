import re
from typing import Optional, Dict, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.models import House, HouseEntrance, EntranceFlatsRange, Zone, City
from datetime import datetime
from sqlalchemy.orm import selectinload


def extract_house_meta(parsed_data: dict) -> Tuple[str, str, int, int, Dict[int, List[Tuple[int, int]]]]:
    title = parsed_data.get("title", "")
    floors_text = parsed_data.get("floors", "")
    entrances_text = parsed_data.get("entrances", "")
    apartments_raw = parsed_data.get("apartments", [])

    # Улица и номер
    street_match = re.match(r"^(.*?)\s+(\S+)$", title)
    street = street_match.group(1).strip() if street_match else title
    house_number = street_match.group(2).strip() if street_match else ""

    # Этажи
    floors_match = re.search(r"(\d+)", floors_text)
    floors = int(floors_match.group(1)) if floors_match else 0

    # Подъезды
    entrances_match = re.search(r"(\d+)", entrances_text)
    entrances = int(entrances_match.group(1)) if entrances_match else 1

    # Квартиры по подъездам
    entrances_info: dict[int, list[tuple[int, int]]] = {}
    for line in apartments_raw:
        if match := re.match(r"(\d+)\s+подъезд: квартиры\s+(.+)", line):
            entrance = int(match.group(1))
            ranges = match.group(2).split(", ")
            for r in ranges:
                if flat_match := re.match(r"(\d+)[–-](\d+)", r.strip()):
                    start, end = int(flat_match.group(1)), int(flat_match.group(2))
                    entrances_info.setdefault(entrance, []).append((start, end))

    return street, house_number, floors, entrances, entrances_info


async def save_parsed_house_to_db(
    session: AsyncSession,
    parsed_data: dict,
    area_id: str,
    zone_id: int,
    created_by: int,
    notes: Optional[str] = None
) -> int:
    street, house_number, floors, entrances_count, entrances_info = extract_house_meta(parsed_data)

    # Проверка на существующий дом
    stmt = select(House).where(
        House.area_id == area_id,
        House.street == street,
        House.house_number == house_number
    )
    existing = (await session.execute(stmt)).scalar_one_or_none()
    if existing:
        return existing.id  # уже есть

    # Создание дома
    house = House(
        area_id=area_id,
        zone_id=zone_id,
        street=street,
        house_number=house_number,
        entrances=entrances_count,
        floors=floors,
        notes=notes or "",
        created_by=created_by,
        updated_by=created_by,
    )
    session.add(house)
    await session.flush()  # чтобы получить house.id

    # Подъезды и диапазоны квартир
    for entrance_number in range(1, entrances_count + 1):
        flats_ranges = entrances_info.get(entrance_number, [])

        flats_text = ""
        if flats_ranges:
            all_ranges = [f"{s}–{e}" for s, e in flats_ranges]
            flats_text = ", ".join(all_ranges)

        he = HouseEntrance(
            house_id=house.id,
            entrance_number=entrance_number,
            floors=floors,
            flats_text=flats_text,
            notes="",
            created_by=created_by,
            updated_by=created_by,
        )
        session.add(he)
        await session.flush()  # получаем he.id

        for start, end in flats_ranges:
            session.add(EntranceFlatsRange(
                entrance_id=he.id,
                start_flat=start,
                end_flat=end
            ))

    await session.commit()
    return house.id



async def get_house_parsed_view(session: AsyncSession, house_id: int) -> Optional[Dict]:
    stmt = (
        select(House)
        .where(House.id == house_id)
        .options(
            selectinload(House.zone).selectinload(Zone.city),
            selectinload(House.entrances_rel).selectinload(HouseEntrance.flats_ranges)
        )
    )
    result = await session.execute(stmt)
    house = result.scalar_one_or_none()
    if house is None:
        return None

    title = f"{house.street} {house.house_number}"
    floors_text = f"{house.floors} этажей" if house.floors else "Не указано"
    entrances_text = f"{house.entrances} подъездов" if house.entrances else "Не указано"

    apartments = []
    for entrance in sorted(house.entrances_rel, key=lambda e: e.entrance_number):
        ranges = [f"{r.start_flat}–{r.end_flat}" for r in sorted(entrance.flats_ranges, key=lambda r: r.start_flat)]
        if ranges:
            apartments.append(f"{entrance.entrance_number} подъезд: квартиры {', '.join(ranges)}")

    city = house.zone.city.name if house.zone and house.zone.city else "неизвестно"
    zone = house.zone.name if house.zone else "неизвестно"
    address = f"{city}, {zone}"
    updated_at = house.updated_at.strftime("%d.%m.%Y %H:%M") if house.updated_at else "Не указано"

    return {
        "title": title,
        "floors": floors_text,
        "entrances": entrances_text,
        "apartments": apartments,
        "address": address,
        "notes": house.notes or "Нет",
        "updated_at": updated_at,
        "jeu_address": "нет информации"  # заглушка
    }