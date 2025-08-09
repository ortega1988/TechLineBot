from collections.abc import Sequence
from typing import Optional

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Area


async def get_area_by_id(session: AsyncSession, area_id: str) -> Optional[Area]:
    result = await session.execute(select(Area).where(Area.id == area_id))
    return result.scalar_one_or_none()


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


async def get_areas_by_branch_id(
    session: AsyncSession, branch_id: int
) -> Sequence[Area]:
    result = await session.execute(
        select(Area).where(Area.branch_id == branch_id).order_by(Area.id)
    )
    return result.scalars().all()
