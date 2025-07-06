from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import ScalarResult

from db.models import City


async def get_city_by_id(
    session: AsyncSession,
    city_id: int
) -> Optional[City]:
    result: ScalarResult[City] = (
        await session.execute(
            select(City).where(City.id == city_id)
        )
    ).scalars()
    return result.first()


async def get_city_by_name(
    session: AsyncSession,
    name: str
) -> Optional[City]:
    result: ScalarResult[City] = (
        await session.execute(
            select(City).where(City.name == name)
        )
    ).scalars()
    return result.first()


async def get_cities_by_branch(
    session: AsyncSession,
    branch_id: int
) -> Sequence[City]:
    result: ScalarResult[City] = (
        await session.execute(
            select(City).where(City.branch_id == branch_id)
        )
    ).scalars()
    return result.all()


async def create_city(
    session: AsyncSession,
    name: str,
    url: str,
    branch_id: int
) -> City:
    city = City(
        name=name,
        url=url,
        branch_id=branch_id
    )
    session.add(city)
    await session.commit()
    await session.refresh(city)
    return city


async def delete_city(
    session: AsyncSession,
    city_id: int
) -> bool:
    city = await get_city_by_id(session, city_id)
    if city is None:
        return False

    await session.delete(city)
    await session.commit()
    return True


async def get_all_cities(session: AsyncSession) -> Sequence[City]:
    result = await session.execute(select(City))
    return result.scalars().all()

async def get_cities_by_branch_id(session: AsyncSession, branch_id: int) -> Sequence[City]:
    result = await session.execute(select(City).where(City.branch_id == branch_id).order_by(City.name))
    return result.scalars().all()


from collections.abc import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.models import City, Zone

async def get_cities_by_area(session: AsyncSession, area_id: str) -> Sequence[City]:
    result = await session.execute(
        select(City)
        .join(Zone, City.id == Zone.city_id)
        .where(Zone.area_id == area_id)
        .distinct()
        .order_by(City.name)
    )
    return result.scalars().all()