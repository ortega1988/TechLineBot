from typing import Optional

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User


async def get_user_by_id(session: AsyncSession, user_id: int) -> Optional[User]:
    result: Result = await session.execute(select(User).where(User.id == user_id))
    return result.scalars().first()


async def create_user(
    session: AsyncSession,
    user_id: int,
    full_name: str,
    username: Optional[str],
    role_id: int,
) -> User:
    user = User(
        id=user_id,
        full_name=full_name,
        username=username,
        role_id=role_id,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def update_user_name(
    session: AsyncSession,
    user_id: int,
    full_name: Optional[str] = None,
    username: Optional[str] = None,
) -> Optional[User]:
    user = await get_user_by_id(session, user_id)
    if user is None:
        return None

    if full_name is not None:
        user.full_name = full_name
    if username is not None:
        user.username = username

    await session.commit()
    await session.refresh(user)
    return user


async def set_user_role(
    session: AsyncSession,
    user_id: int,
    role_id: int,
) -> Optional[User]:
    user = await get_user_by_id(session, user_id)
    if user is None:
        return None

    user.role_id = role_id
    await session.commit()
    await session.refresh(user)
    return user


async def get_super_admin(session: AsyncSession) -> Optional[User]:
    result: Result = await session.execute(select(User).where(User.role_id == 0))
    return result.scalars().first()


async def get_rn_by_branch(session: AsyncSession, branch_id: str) -> Optional[User]:
    result: Result = await session.execute(
        select(User).where(User.role_id == 1, User.branch_id == int(branch_id))
    )
    return result.scalars().first()


async def get_rgks_by_area(session: AsyncSession, area_id: str) -> Optional[User]:
    result: Result = await session.execute(
        select(User).where(User.role_id == 2, User.area_id == area_id)
    )
    return result.scalars().first()


async def set_default_city_for_user(
    session: AsyncSession, user_id: int, city_id: int
) -> None:
    from db.models import User

    user = await session.get(User, user_id)
    if user:
        user.default_city_id = city_id
        await session.commit()


async def get_users_by_role(session: AsyncSession, role_id: int) -> Sequence[User]:
    result: Result = await session.execute(select(User).where(User.role_id == role_id))
    return result.scalars().all()
