from db.db import db


NEWBIE_ROLE_ID = 50

async def get_user(tg_id: int) -> dict | None:
    """Получить пользователя по Telegram ID."""
    return await db.fetchone(
        "SELECT * FROM users WHERE id = %s",
        (tg_id,)
    )

async def insert_new_user(tg_id: int, full_name: str, username: str) -> None:
    """Добавить нового пользователя с ролью 'Новичок'."""
    await db.execute(
        """
        INSERT INTO users (id, full_name, username, role_id)
        VALUES (%s, %s, %s, %s)
        """,
        (tg_id, full_name, username, NEWBIE_ROLE_ID)
    )

async def get_role_name(role_id: int) -> str | None:
    """Получить название роли по её ID."""
    row = await db.fetchone(
        "SELECT name FROM roles WHERE id = %s",
        (role_id,)
    )
    return row["name"] if row else None
