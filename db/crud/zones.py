from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import ScalarResult
from sqlalchemy.orm import selectinload
from db.models import Zone, City


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
    city_id: int,
    area_id: str,
    branch_id: int
) -> Zone:
    zone = Zone(
        name=name,
        city_id=city_id,
        area_id=area_id,
        branch_id=branch_id
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

async def get_zones_by_area(session: AsyncSession, area_id: str) -> Sequence[Zone]:
    result = await session.execute(select(Zone).where(Zone.area_id == area_id))
    return result.scalars().all()


async def get_zones_by_area_and_city(session: AsyncSession, area_id: str, city_id: int) -> Sequence[Zone]:
    result = await session.execute(
        select(Zone).where(Zone.area_id == area_id, Zone.city_id == city_id)
    )
    return result.scalars().all()