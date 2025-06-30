import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import async_session
from db.models import Role, Branch, City, Zone, Area, AreaZone

from sqlalchemy import text


async def clear_db(session):
    await session.execute(text('DELETE FROM area_zones'))
    await session.execute(text('DELETE FROM zones'))
    await session.execute(text('DELETE FROM areas'))
    await session.execute(text('DELETE FROM houses'))
    await session.execute(text('DELETE FROM house_entrances'))
    await session.execute(text('DELETE FROM entrance_equipment'))
    await session.execute(text('DELETE FROM entrance_photos'))
    await session.execute(text('DELETE FROM users'))
    await session.execute(text('DELETE FROM cities'))
    await session.execute(text('DELETE FROM branches'))
    await session.execute(text('DELETE FROM roles'))
    await session.commit()
    print("✅ База очищена")



async def seed_data(session: AsyncSession):
    # ✅ Роли
    roles = [
        Role(id=0, name="Администратор", description="Главный администратор"),
        Role(id=1, name="РН", description="Руководитель направления"),
        Role(id=2, name="РГКС", description="Руководитель группы клиентского сервиса"),
        Role(id=3, name="СИ", description="Старший инженер"),
        Role(id=50, name="Новичок", description="Начальная роль при старте"),
    ]
    session.add_all(roles)
    await session.commit()
    await session.flush()
    

    # ✅ Филиалы
    branches = [
        Branch(id=16, name="Казанский"),
    ]
    session.add_all(branches)
    await session.flush()

    # ✅ Города
    cities = [
        City(name="Казань", url="https://2gis.ru/kazan", branch_id=16),
        City(name="Иннополис", url="https://2gis.ru/innopolis", branch_id=16),
        City(name="Зеленодольск", url="https://2gis.ru/zelenodolsk", branch_id=16),
    ]
    session.add_all(cities)
    await session.commit()
    await session.flush()

    # ✅ Зоны
    zone_map = {city.name: city.id for city in cities}
    zones = [
        Zone(name="Авиастроительный", branch_id=16, city_id=zone_map["Казань"]),
        Zone(name="Советский", branch_id=16, city_id=zone_map["Казань"]),
        Zone(name="Вахитовский", branch_id=16, city_id=zone_map["Казань"]),
        Zone(name="Ново-Савиновский", branch_id=16, city_id=zone_map["Казань"]),
        Zone(name="Верхнеуслонский", branch_id=16, city_id=zone_map["Иннополис"]),
        Zone(name="-", branch_id=16, city_id=zone_map["Зеленодольск"]),
    ]
    session.add_all(zones)
    await session.commit()
    await session.flush()  # Нужно, чтобы получить id зон для связки с участками

    # ✅ Участки
    areas = [
        Area(id="16.1", name="Участок 16.1", branch_id=16),
        Area(id="16.2", name="Участок 16.2", branch_id=16),
    ]
    session.add_all(areas)
    await session.commit()
    await session.flush()  # Получаем id для areas, если они автоинкрементные

    # ✅ Связка участков с зонами
    zone_map = {zone.name: zone.id for zone in zones}

    area_zones = [
        AreaZone(area_id="16.1", zone_id=zone_map["Авиастроительный"]),
        AreaZone(area_id="16.1", zone_id=zone_map["Ново-Савиновский"]),
        AreaZone(area_id="16.2", zone_id=zone_map["Советский"]),
        AreaZone(area_id="16.2", zone_id=zone_map["Вахитовский"]),
    ]
    session.add_all(area_zones)
    await session.flush()

    await session.commit()
    print("✅ Seed выполнен успешно")


async def main():
    async with async_session() as session:
        await clear_db(session)
        await seed_data(session)


if __name__ == "__main__":
    asyncio.run(main())
