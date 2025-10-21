from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import EntranceComment, FlatComment, HouseComment


async def create_house_comment(
    session: AsyncSession, *, house_id: int, user_id: int, text: str
) -> HouseComment:
    comment = HouseComment(house_id=house_id, user_id=user_id, text=text)
    session.add(comment)
    await session.commit()
    await session.refresh(comment)
    return comment


async def get_comments_by_house_id(
    session: AsyncSession, *, house_id: int, page: int = 1, limit: int = 10
) -> Sequence[HouseComment]:
    stmt = (
        select(HouseComment)
        .where(HouseComment.house_id == house_id)
        .order_by(HouseComment.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    )
    result = await session.execute(stmt)
    return result.scalars().all()


async def count_house_comments(session: AsyncSession, *, house_id: int) -> int:
    stmt = select(func.count()).select_from(HouseComment).where(HouseComment.house_id == house_id)
    result = await session.execute(stmt)
    return result.scalar_one()


async def get_house_comment_by_id(session: AsyncSession, *, comment_id: int) -> HouseComment | None:
    return await session.get(HouseComment, comment_id)


async def update_house_comment(session: AsyncSession, *, comment_id: int, text: str) -> HouseComment | None:
    comment = await get_house_comment_by_id(session, comment_id=comment_id)
    if comment:
        comment.text = text
        await session.commit()
        await session.refresh(comment)
    return comment


async def delete_house_comment(session: AsyncSession, *, comment_id: int) -> bool:
    comment = await get_house_comment_by_id(session, comment_id=comment_id)
    if comment:
        await session.delete(comment)
        await session.commit()
        return True
    return False


async def create_entrance_comment(
    session: AsyncSession, *, entrance_id: int, user_id: int, text: str
) -> EntranceComment:
    comment = EntranceComment(entrance_id=entrance_id, user_id=user_id, text=text)
    session.add(comment)
    await session.commit()
    await session.refresh(comment)
    return comment


async def get_comments_by_entrance_id(
    session: AsyncSession, *, entrance_id: int, page: int = 1, limit: int = 10
) -> Sequence[EntranceComment]:
    stmt = (
        select(EntranceComment)
        .where(EntranceComment.entrance_id == entrance_id)
        .order_by(EntranceComment.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    )
    result = await session.execute(stmt)
    return result.scalars().all()


async def count_entrance_comments(session: AsyncSession, *, entrance_id: int) -> int:
    stmt = select(func.count()).select_from(EntranceComment).where(EntranceComment.entrance_id == entrance_id)
    result = await session.execute(stmt)
    return result.scalar_one()


async def get_entrance_comment_by_id(session: AsyncSession, *, comment_id: int) -> EntranceComment | None:
    return await session.get(EntranceComment, comment_id)


async def update_entrance_comment(session: AsyncSession, *, comment_id: int, text: str) -> EntranceComment | None:
    comment = await get_entrance_comment_by_id(session, comment_id=comment_id)
    if comment:
        comment.text = text
        await session.commit()
        await session.refresh(comment)
    return comment


async def delete_entrance_comment(session: AsyncSession, *, comment_id: int) -> bool:
    comment = await get_entrance_comment_by_id(session, comment_id=comment_id)
    if comment:
        await session.delete(comment)
        await session.commit()
        return True
    return False


async def create_flat_comment(
    session: AsyncSession,
    *,
    house_id: int,
    entrance_id: int | None,
    flat_number: int,
    user_id: int,
    text: str,
) -> FlatComment:
    comment = FlatComment(
        house_id=house_id,
        entrance_id=entrance_id,
        flat_number=flat_number,
        user_id=user_id,
        text=text,
    )
    session.add(comment)
    await session.commit()
    await session.refresh(comment)
    return comment


async def get_comments_by_flat_number(
    session: AsyncSession, *, house_id: int, flat_number: int, page: int = 1, limit: int = 10
) -> Sequence[FlatComment]:
    stmt = (
        select(FlatComment)
        .where(FlatComment.house_id == house_id, FlatComment.flat_number == flat_number)
        .order_by(FlatComment.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    )
    result = await session.execute(stmt)
    return result.scalars().all()


async def count_flat_comments(session: AsyncSession, *, house_id: int, flat_number: int) -> int:
    stmt = (
        select(func.count())
        .select_from(FlatComment)
        .where(FlatComment.house_id == house_id, FlatComment.flat_number == flat_number)
    )
    result = await session.execute(stmt)
    return result.scalar_one()


async def get_flat_comment_by_id(session: AsyncSession, *, comment_id: int) -> FlatComment | None:
    return await session.get(FlatComment, comment_id)


async def update_flat_comment(session: AsyncSession, *, comment_id: int, text: str) -> FlatComment | None:
    comment = await get_flat_comment_by_id(session, comment_id=comment_id)
    if comment:
        comment.text = text
        await session.commit()
        await session.refresh(comment)
    return comment


async def delete_flat_comment(session: AsyncSession, *, comment_id: int) -> bool:
    comment = await get_flat_comment_by_id(session, comment_id=comment_id)
    if comment:
        await session.delete(comment)
        await session.commit()
        return True
    return False
