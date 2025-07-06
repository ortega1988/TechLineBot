from typing import Optional, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import City, Zone
from db.crud.cities import get_all_cities, get_cities_by_branch
from db.crud.zones import get_zones_by_city, get_zones_by_branch


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


async def resolve_city_zone_from_comment(
    session: AsyncSession,
    user,  # объект пользователя (User)
    comment: str
):
    # Получаем все доступные города и зоны пользователя (например, по branch/area)
    branch_id = user.branch_id
    cities = await get_cities_by_branch(session, branch_id)
    zones = await get_zones_by_branch(session, branch_id)

    # Сначала ищем ПОЛНОЕ совпадение зоны (района)
    zone_obj = next(
        (zone for zone in zones if zone.name.lower() in comment.lower()),
        None
    )

    # Сначала ищем ПОЛНОЕ совпадение города
    city_obj = next(
        (city for city in cities if city.name.lower() in comment.lower()),
        None
    )

    # Логика: если оба найдены — проверяем, что зона принадлежит этому городу!
    if city_obj and zone_obj:
        if zone_obj.city_id == city_obj.id:
            return city_obj.id, zone_obj.id
        else:
            # Название города и района в комментарии не согласованы — игнорируем
            return None, None

    # Если есть только зона — ищем её город
    if zone_obj:
        city_for_zone = next((city for city in cities if city.id == zone_obj.city_id), None)
        if city_for_zone:
            return city_for_zone.id, zone_obj.id
        else:
            return None, None

    # Если есть только город — не подбираем случайный район!
    # Пользователь должен явно указать и район, и город в комментарии,
    # иначе возвращаем None (ЖЭУ нельзя добавить)
    return None, None

