from db.db import db


NEWBIE_ROLE_ID = 50
SUPER_ADMIN_ROLE_ID = 0
RN_ROLE_ID = 1
RGKS_ROLE_ID = 2
SI_ROLE_ID = 3


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


# =============================
# ==== Работа с ДОСТУПОМ ======
# =============================


async def get_user_by_id(user_id: int) -> dict | None:
    """Получить пользователя по Telegram ID."""
    return await db.fetchone(
        "SELECT * FROM users WHERE id = %s",
        (user_id,)
    )

async def branch_exists(branch_id: str) -> bool:
    """Проверить, существует ли филиал."""
    row = await db.fetchone(
        "SELECT id FROM branches WHERE id = %s",
        (branch_id,)
    )
    return bool(row)

async def area_exists(area_id: str) -> bool:
    """Проверить, существует ли участок."""
    row = await db.fetchone(
        "SELECT id FROM areas WHERE id = %s",
        (area_id,)
    )
    return bool(row)

async def get_super_admin() -> dict | None:
    """Получить пользователя-суперадмина (role_id = 0)."""
    return await db.fetchone(
        "SELECT id FROM users WHERE role_id = %s",
        (SUPER_ADMIN_ROLE_ID,)
    )

async def get_rn_by_branch(branch_id: str) -> dict | None:
    """Получить РН по номеру филиала."""
    return await db.fetchone(
        "SELECT id FROM users WHERE branch_id = %s AND role_id = %s",
        (branch_id, RN_ROLE_ID)
    )

async def get_rgks_by_area(area_id: str) -> dict | None:
    """Получить РГКС по номеру участка."""
    return await db.fetchone(
        "SELECT id FROM users WHERE area_id = %s AND role_id = %s",
        (area_id, RGKS_ROLE_ID)
    )

async def update_user_role_area(user_id: int, role_id: int, area_id: str) -> None:
    """Обновить роль, участок/филиал и включить пользователя."""
    await db.execute(
        """
        UPDATE users
        SET role_id   = %s,
            area_id   = %s,
            is_active = TRUE
        WHERE id = %s
        """,
        (role_id, area_id, user_id)
    )


# =============================
# ==== Работа с ЗОНАМИ ========
# =============================

async def get_zone_id_by_name_and_city(name: str, city: str) -> dict | None:
    """Получить зону по имени и городу."""
    return await db.fetchone(
        "SELECT id FROM zones WHERE name = %s AND city = %s",
        (name, city)
    )

async def insert_zone(name: str, city: str, branch_id: str) -> None:
    """Добавить новую зону."""
    await db.execute(
        "INSERT INTO zones (name, city, branch_id) VALUES (%s, %s, %s)",
        (name, city, branch_id)
    )

async def link_area_with_zone(area_id: str, zone_id: int) -> None:
    """Привязать участок к зоне."""
    await db.execute(
        "INSERT IGNORE INTO area_zones (area_id, zone_id) VALUES (%s, %s)",
        (area_id, zone_id)
    )


# =============================
# ==== Работа с ГКС (участками)
# =============================


async def insert_area(area_id: str, name: str, branch_id: str) -> None:
    """Добавить участок (ГКС)."""
    await db.execute(
        "INSERT INTO areas (id, name, branch_id) VALUES (%s, %s, %s)",
        (area_id, name, branch_id)
    )