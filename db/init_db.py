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
                
                # Филиалы
                await cur.execute("""
                    CREATE TABLE IF NOT EXISTS branches (
                        id TINYINT PRIMARY KEY,              
                        name VARCHAR(100) NOT NULL           
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
                        (50, "Новчиек", "Автоматическое добавление в базу"),
                    ])
                    logger.info("🎯 Роли по умолчанию добавлены")
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации таблиц базы данных: {e}")
