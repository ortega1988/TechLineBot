from typing import Optional
from collections.abc import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import ScalarResult
from db.models import HouseEntrance


async def get_entrance_by_id(
    session: AsyncSession, entrance_id: int
) -> Optional[HouseEntrance]:
    result: ScalarResult[HouseEntrance] = (
        await session.execute(
            select(HouseEntrance).where(HouseEntrance.id == entrance_id)
        )
    ).scalars()
    return result.first()


async def get_entrances_by_house(
    session: AsyncSession, house_id: int
) -> Sequence[HouseEntrance]:
    result: ScalarResult[HouseEntrance] = (
        await session.execute(
            select(HouseEntrance).where(HouseEntrance.house_id == house_id)
        )
    ).scalars()
    return result.all()
