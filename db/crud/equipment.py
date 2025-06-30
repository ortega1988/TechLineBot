from typing import Optional
from collections.abc import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import ScalarResult
from db.models import EntranceEquipment


async def get_equipment_by_id(
    session: AsyncSession, equipment_id: int
) -> Optional[EntranceEquipment]:
    result: ScalarResult[EntranceEquipment] = (
        await session.execute(
            select(EntranceEquipment).where(EntranceEquipment.id == equipment_id)
        )
    ).scalars()
    return result.first()


async def get_equipment_by_entrance(
    session: AsyncSession, entrance_id: int
) -> Sequence[EntranceEquipment]:
    result: ScalarResult[EntranceEquipment] = (
        await session.execute(
            select(EntranceEquipment).where(EntranceEquipment.entrance_id == entrance_id)
        )
    ).scalars()
    return result.all()
