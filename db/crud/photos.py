from typing import Optional
from collections.abc import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import ScalarResult
from db.models import EntrancePhoto


async def get_photo_by_id(
    session: AsyncSession, photo_id: int
) -> Optional[EntrancePhoto]:
    result: ScalarResult[EntrancePhoto] = (
        await session.execute(
            select(EntrancePhoto).where(EntrancePhoto.id == photo_id)
        )
    ).scalars()
    return result.first()


async def get_photos_by_entrance(
    session: AsyncSession, entrance_id: int
) -> Sequence[EntrancePhoto]:
    result: ScalarResult[EntrancePhoto] = (
        await session.execute(
            select(EntrancePhoto).where(EntrancePhoto.entrance_id == entrance_id)
        )
    ).scalars()
    return result.all()
