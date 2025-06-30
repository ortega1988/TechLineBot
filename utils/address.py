from typing import Optional, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import City, Zone
from db.crud.cities import get_all_cities
from db.crud.zones import get_zones_by_city



async def detect_city_and_zone_by_address(
    session: AsyncSession,
    address: str
) -> Tuple[Optional[City], Optional[Zone]]:
    address_lower = address.lower()

    # Поиск города
    cities = await get_all_cities(session)
    city = next((c for c in cities if c.name.lower() in address_lower), None)

    if not city:
        return None, None  # Город не найден

    # Поиск зон для города
    zones = await get_zones_by_city(session, city.id)

    if not zones:
        return city, None  # Город есть, зоны отсутствуют

    # Поиск подходящего района
    zone = next((z for z in zones if z.name.lower() in address_lower), None)

    return city, zone