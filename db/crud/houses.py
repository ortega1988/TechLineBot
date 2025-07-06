from typing import Optional
from collections.abc import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import ScalarResult
from db.models import House, HouseEntrance


async def get_house_by_id(session: AsyncSession, house_id: int) -> Optional[House]:
    result = await session.execute(
        select(House).where(House.id == house_id)
    )
    return result.scalar_one_or_none()


async def get_houses_by_area(
    session: AsyncSession, area_id: str
) -> Sequence[House]:
    result: ScalarResult[House] = (
        await session.execute(
            select(House).where(House.area_id == area_id)
        )
    ).scalars()
    return result.all()


async def get_house_by_address(
    session: AsyncSession,
    area_id: str,
    zone_id: int,
    street: str,
    house_number: str
) -> Optional[House]:
    result = await session.execute(
        select(House).where(
            House.area_id == area_id,
            House.zone_id == zone_id,
            House.street == street,
            House.house_number == house_number,
            House.is_active == True
        )
    )
    return result.scalars().first()


async def create_house_with_entrances(
    session: AsyncSession,
    *,
    area_id: str,
    zone_id: int,
    street: str,
    house_number: str,
    floors: int,
    entrances: int,
    created_by: int,
    notes: str = ""
) -> House:
    house = House(
        area_id=area_id,
        zone_id=zone_id,
        street=street,
        house_number=house_number,
        floors=floors,
        entrances=entrances,
        is_in_gks=False,
        is_active=True,
        created_by=created_by,
        updated_by=created_by,
        notes=notes
    )
    session.add(house)
    await session.flush()  # Чтобы получить house.id

    for i in range(1, entrances + 1):
        entrance = HouseEntrance(
            house_id=house.id,
            entrance_number=i,
            floors=floors,
            is_active=True,
            created_by=created_by,
            updated_by=created_by,
            notes=""
        )
        session.add(entrance)

    await session.commit()
    await session.refresh(house)
    return house


async def get_entrances_by_house(
    session: AsyncSession, house_id: int
) -> Sequence[HouseEntrance]:
    result: ScalarResult[HouseEntrance] = (
        await session.execute(
            select(HouseEntrance).where(HouseEntrance.house_id == house_id)
        )
    ).scalars()
    return result.all()



