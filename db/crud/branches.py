from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result
from db.models import Branch
from collections.abc import Sequence


async def get_branch_by_id(session: AsyncSession, branch_id: int) -> Optional[Branch]:
    result = await session.execute(select(Branch).where(Branch.id == branch_id))
    return result.scalar_one_or_none()

async def get_branch_by_name(session: AsyncSession, name: str) -> Optional[Branch]:
    result = await session.execute(select(Branch).where(Branch.name == name))
    return result.scalar_one_or_none()

async def create_branch(session: AsyncSession, name: str, branch_id: int) -> Branch:
    branch = Branch(id=branch_id, name=name)
    session.add(branch)
    await session.commit()
    await session.refresh(branch)
    return branch


async def get_all_branches(session: AsyncSession) -> Sequence[Branch]:
    result = await session.execute(select(Branch).order_by(Branch.name))
    return result.scalars().all()