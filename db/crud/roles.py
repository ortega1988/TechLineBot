from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.engine import Result

from db.models import Role


async def get_role_name(session: AsyncSession, role_id: int) -> Optional[str]:
    result: Result = await session.execute(
        select(Role.name).where(Role.id == role_id)
    )
    return result.scalar_one_or_none()
