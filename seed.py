import asyncio

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from db.db import async_session  # если у тебя есть уже сессия, иначе определи engine
from db.models import Role

# Начальные роли (id, name, description)
ROLES = [
    (0, "Главный администратор", "Главный администратор"),
    (10, "РН", "Руководитель Направления"),
    (20, "РГКС", "Руководитель группы клиентского сервиса"),
    (30, "СИ", "Старший Инженер"),
    (50, "Новичек", "незарегестрированный пользователь"),
]


async def seed_roles():
    async with async_session() as session:
        for id_, name, desc in ROLES:
            role = await session.get(Role, id_)
            if not role:
                session.add(Role(id=id_, name=name, description=desc))
        await session.commit()
    print("Roles seeded!")


if __name__ == "__main__":
    asyncio.run(seed_roles())
