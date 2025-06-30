from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result

from db.models import Area


async def get_area_by_id(
    session: AsyncSession,
    area_id: str
) -> Optional[Area]:
    result: Result = await session.execute(
        select(Area).where(Area.id == area_id)
    )
    return result.scalars().first()


async def create_area(
    session: AsyncSession,
    area_id: str,
    name: str,
    branch_id: int,
) -> Area:
    area = Area(
        id=area_id,
        name=name,
        branch_id=branch_id,
    )
    session.add(area)
    await session.commit()
    await session.refresh(area)
    return area
