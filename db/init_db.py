import logging
from db.db import db

logger = logging.getLogger(__name__)

async def init_database():
    try:
        async with db.pool.acquire() as conn:
            async with conn.cursor() as cur:
                # Таблица ролей
                await cur.execute("""
                    CREATE TABLE IF NOT EXISTS roles (
                        id TINYINT PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        description TEXT
                    )
                """)
                
                # Таблица филиалов
                await cur.execute("""
                    CREATE TABLE IF NOT EXISTS branches (
                        id TINYINT PRIMARY KEY,
                        name VARCHAR(100) NOT NULL
                    )
                """)
                
                # Филиалы
                await cur.execute("""
                    CREATE TABLE IF NOT EXISTS zones (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,        -- Название района (например, Ново‑Савиновский)
                        city VARCHAR(100) NOT NULL,        -- Город (например, Казань, Иннополис)
                        branch_id TINYINT NOT NULL,        -- Привязка к филиалу
                        FOREIGN KEY (branch_id) REFERENCES branches(id)
                            ON DELETE RESTRICT
                            ON UPDATE CASCADE
                    )
                """)
                
                # Участки
                await cur.execute("""
                    CREATE TABLE IF NOT EXISTS areas (
                        id VARCHAR(10) PRIMARY KEY,          
                        name VARCHAR(100) NOT NULL,          
                        branch_id TINYINT NOT NULL,          
                        FOREIGN KEY (branch_id) REFERENCES branches(id)
                    )
                """)
                
                
                # Связь района к участку
                await cur.execute("""
                    CREATE TABLE IF NOT EXISTS area_zones (
                        area_id VARCHAR(10) NOT NULL,        -- Участок (например, '16.1')
                        zone_id INT NOT NULL,                -- ID из таблицы zones
                        PRIMARY KEY (area_id, zone_id),
                        FOREIGN KEY (area_id) REFERENCES areas(id)
                            ON DELETE CASCADE
                            ON UPDATE CASCADE,
                        FOREIGN KEY (zone_id) REFERENCES zones(id)
                            ON DELETE CASCADE
                            ON UPDATE CASCADE
                    )
                """)

                # Таблица пользователей
                await cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id BIGINT PRIMARY KEY,                        -- Telegram ID
                        full_name VARCHAR(255),                       -- ФИО
                        username VARCHAR(50),                         -- Никнейм
                        phone VARCHAR(20),                            -- Телефон
                        area_id VARCHAR(10),                          -- Привязка к участку (например 16.2)
                        temp_area_id VARCHAR(10),                     -- Временный участок (командировка)
                        branch_id TINYINT,                            -- Если отвечает за весь филиал
                        role_id TINYINT NOT NULL,                     -- Уровень доступа
                        is_active TINYINT(1) DEFAULT 1,               -- Активен/неактивен
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        notes TEXT,

                        FOREIGN KEY (role_id) REFERENCES roles(id),
                        FOREIGN KEY (area_id) REFERENCES areas(id),
                        FOREIGN KEY (temp_area_id) REFERENCES areas(id),
                        FOREIGN KEY (branch_id) REFERENCES branches(id)
                    )
                """)
                
                    # Таблица домов
                await cur.execute("""
                    CREATE TABLE IF NOT EXISTS houses (
                        id             INT             NOT NULL AUTO_INCREMENT,
                        area_id        VARCHAR(10)     NOT NULL,
                        zone_id        INT             NOT NULL,
                        street         VARCHAR(255)    NOT NULL,
                        house_number   VARCHAR(50)     NOT NULL,
                        entrances      TINYINT UNSIGNED NOT NULL,
                        floors         TINYINT UNSIGNED NOT NULL,
                        is_in_gks      TINYINT(1)      NOT NULL DEFAULT 0 COMMENT '1 — в ведении ГКС, 0 — нет',
                        is_active      TINYINT(1)      NOT NULL DEFAULT 1 COMMENT '1 — активен, 0 — архив',
                        notes          TEXT,
                        created_at     DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at     DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        created_by     BIGINT          NOT NULL,
                        updated_by     BIGINT          NOT NULL,

                        PRIMARY KEY (id),
                        UNIQUE KEY uk_house (area_id, street, house_number),

                        KEY ix_zone (zone_id),
                        KEY ix_street (street),

                        FOREIGN KEY (area_id)    REFERENCES areas(id)   ON DELETE RESTRICT ON UPDATE CASCADE,
                        FOREIGN KEY (zone_id)    REFERENCES zones(id)   ON DELETE RESTRICT ON UPDATE CASCADE,
                        FOREIGN KEY (created_by) REFERENCES users(id)   ON DELETE RESTRICT ON UPDATE CASCADE,
                        FOREIGN KEY (updated_by) REFERENCES users(id)   ON DELETE RESTRICT ON UPDATE CASCADE
                    )
                """)
                
                
                    # Таблица подъездов
                await cur.execute("""
                    CREATE TABLE IF NOT EXISTS house_entrances (
                        id              INT             NOT NULL AUTO_INCREMENT,
                        house_id        INT             NOT NULL,
                        entrance_number SMALLINT        NOT NULL,
                        floors          TINYINT UNSIGNED,
                        is_active       TINYINT(1)      NOT NULL DEFAULT 1 COMMENT '1 — активен, 0 — архив',
                        notes           TEXT,

                        created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        created_by      BIGINT          NOT NULL,
                        updated_by      BIGINT          NOT NULL,

                        PRIMARY KEY (id),
                        UNIQUE KEY uk_entrance (house_id, entrance_number),

                        FOREIGN KEY (house_id)    REFERENCES houses(id)    ON DELETE CASCADE ON UPDATE CASCADE,
                        FOREIGN KEY (created_by)  REFERENCES users(id)     ON DELETE RESTRICT ON UPDATE CASCADE,
                        FOREIGN KEY (updated_by)  REFERENCES users(id)     ON DELETE RESTRICT ON UPDATE CASCADE
                    )
                """)
                
                
                    # Таблица оборудование подъездов
                await cur.execute("""
                    CREATE TABLE IF NOT EXISTS entrance_equipment (
                        id              INT             NOT NULL AUTO_INCREMENT,
                        entrance_id     INT             NOT NULL,
                        type            VARCHAR(100)    NOT NULL,
                        model           VARCHAR(100),
                        serial_number   VARCHAR(100),
                        status          VARCHAR(50)     DEFAULT 'Работает',
                        installed_at    DATETIME,
                        notes           TEXT,

                        created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        created_by      BIGINT          NOT NULL,
                        updated_by      BIGINT          NOT NULL,

                        PRIMARY KEY (id),
                        FOREIGN KEY (entrance_id) REFERENCES house_entrances(id) ON DELETE CASCADE ON UPDATE CASCADE,
                        FOREIGN KEY (created_by)  REFERENCES users(id)           ON DELETE RESTRICT ON UPDATE CASCADE,
                        FOREIGN KEY (updated_by)  REFERENCES users(id)           ON DELETE RESTRICT ON UPDATE CASCADE
                    )
                """)
                
                
                    # фото подъездов
                await cur.execute("""
                    CREATE TABLE IF NOT EXISTS entrance_photos (
                        id              INT             NOT NULL AUTO_INCREMENT,
                        entrance_id     INT             NOT NULL,
                        url             VARCHAR(500)    NOT NULL,
                        description     VARCHAR(255),

                        uploaded_at     DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        created_by      BIGINT          NOT NULL,

                        PRIMARY KEY (id),
                        FOREIGN KEY (entrance_id) REFERENCES house_entrances(id) ON DELETE CASCADE ON UPDATE CASCADE,
                        FOREIGN KEY (created_by)  REFERENCES users(id)           ON DELETE RESTRICT ON UPDATE CASCADE
                    )
                """)

                
                logger.info("🧱 Таблицы проверены/созданы")

                # Роли
                await cur.execute("SELECT COUNT(*) FROM roles")
                count = (await cur.fetchone())[0]
                if count == 0:
                    await cur.executemany("""
                        INSERT INTO roles (id, name, description) VALUES (%s, %s, %s)
                    """, [
                        (0, "Главный администратор", "Полный доступ"),
                        (1, "Руководитель направления", "Расширенные права"),
                        (2, "Руководитель группы КС", "Ограниченное управление"),
                        (3, "Старший инженер", "Базовые действия"),
                        (50, "Новичек", "Автоматическое добавление в базу"),
                    ])
                    logger.info("🎯 Роли по умолчанию добавлены")
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации таблиц базы данных: {e}")
