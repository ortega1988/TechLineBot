from typing import Optional, Sequence

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import HousingOffice


async def create_housing_office(
    session: AsyncSession,
    name: str,
    address: str,
    city_id: int,
    zone_id: int,
    comments: str = "",
    photo_url: str = "",
    working_hours: str = "",
    phone: str = "",
    email: str = "",
) -> HousingOffice:
    office = HousingOffice(
        name=name,
        address=address,
        city_id=city_id,
        zone_id=zone_id,
        comments=comments,
        photo_url=photo_url,
        working_hours=working_hours,
        phone=phone,
        email=email,
    )
    session.add(office)
    await session.commit()
    await session.refresh(office)
    return office


async def get_housing_office_by_id(
    session: AsyncSession, office_id: int
) -> Optional[HousingOffice]:
    result = await session.execute(
        select(HousingOffice).where(HousingOffice.id == office_id)
    )
    return result.scalar_one_or_none()


async def get_all_housing_offices(session: AsyncSession) -> Sequence[HousingOffice]:
    result = await session.execute(select(HousingOffice))
    return result.scalars().all()


async def update_housing_office(
    session: AsyncSession, office_id: int, **kwargs
) -> Optional[HousingOffice]:
    await session.execute(
        update(HousingOffice).where(HousingOffice.id == office_id).values(**kwargs)
    )
    await session.commit()
    return await get_housing_office_by_id(session, office_id)


async def delete_housing_office(session: AsyncSession, office_id: int) -> None:
    await session.execute(delete(HousingOffice).where(HousingOffice.id == office_id))
    await session.commit()
