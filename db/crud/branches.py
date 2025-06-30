from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result
from db.models import Branch


async def get_branch_by_id(
    session: AsyncSession, branch_id: str
) -> Optional[Branch]:
    result: Result = await session.execute(
        select(Branch).where(Branch.id == int(branch_id))
    )
    return result.scalars().first()
