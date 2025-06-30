from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import ScalarResult
from sqlalchemy.orm import selectinload
from db.models import Zone, AreaZone, City


async def get_zone_by_id(
    session: AsyncSession,
    zone_id: int
) -> Optional[Zone]:
    result: ScalarResult[Zone] = (
        await session.execute(
            select(Zone).where(Zone.id == zone_id)
        )
    ).scalars()
    return result.first()


async def get_zone_by_name_and_city(
    session: AsyncSession,
    name: str,
    city_id: int
) -> Optional[Zone]:
    result: ScalarResult[Zone] = (
        await session.execute(
            select(Zone).where(
                Zone.name == name,
                Zone.city_id == city_id
            )
        )
    ).scalars()
    return result.first()


async def get_zones_by_branch(
    session: AsyncSession,
    branch_id: int
) -> Sequence[Zone]:
    result: ScalarResult[Zone] = (
        await session.execute(
            select(Zone).where(Zone.branch_id == branch_id)
        )
    ).scalars()
    return result.all()


async def get_zones_by_city(
    session: AsyncSession,
    city_id: int
) -> Sequence[Zone]:
    result: ScalarResult[Zone] = (
        await session.execute(
            select(Zone).where(Zone.city_id == city_id)
        )
    ).scalars()
    return result.all()


async def create_zone(
    session: AsyncSession,
    name: str,
    branch_id: int,
    city_id: int
) -> Zone:
    zone = Zone(
        name=name,
        branch_id=branch_id,
        city_id=city_id
    )
    session.add(zone)
    await session.commit()
    await session.refresh(zone)
    return zone


async def delete_zone(
    session: AsyncSession,
    zone_id: int
) -> bool:
    zone = await get_zone_by_id(session, zone_id)
    if zone is None:
        return False

    await session.delete(zone)
    await session.commit()
    return True


async def get_zone_by_area(session: AsyncSession, area_id: str) -> Optional[Zone]:
    result = await session.execute(
        select(Zone)
        .options(selectinload(Zone.city))  # Жадно грузим city
        .join(AreaZone, AreaZone.zone_id == Zone.id)
        .where(AreaZone.area_id == area_id)
    )
    return result.scalars().first()



async def link_area_with_zone(
    session: AsyncSession,
    area_id: str,
    zone_id: int
) -> AreaZone:
    link = AreaZone(
        area_id=area_id,
        zone_id=zone_id
    )
    session.add(link)
    await session.commit()
    await session.refresh(link)
    return link


async def get_zone_by_city_and_zone_name(
    session: AsyncSession,
    city_name: str,
    zone_name: str
) -> Optional[Zone]:
    result = await session.execute(
        select(Zone)
        .join(City, Zone.city_id == City.id)
        .options(selectinload(Zone.city))
        .where(City.name.ilike(city_name))
        .where(Zone.name.ilike(zone_name))
    )
    return result.scalars().first()