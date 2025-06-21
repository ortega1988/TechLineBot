import logging
import aiomysql
from dotenv import load_dotenv
import os


load_dotenv()
DB_HOST = os.getenv('DB_HOST')
DB_PORT = int(os.getenv('DB_PORT'))
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')


logger = logging.getLogger(__name__)


class Database:
    def __init__(self, host, port, user, password, db_name):
        self.pool = None
        self.config = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "db": db_name,
            "autocommit": True,
            "charset": "utf8mb4"
        }

    async def connect(self):
        try:
            self.pool = await aiomysql.create_pool(**self.config)
            logger.info("✅ Подключение к базе данных установлено.")
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к базе данных: {e}")
            raise

    async def close(self):
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            logger.info("🔒 Подключение к базе данных закрыто.")

    async def execute(self, query, params=()):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, params)

    async def fetchone(self, query, params=()):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(query, params)
                return await cur.fetchone()

    async def fetchall(self, query, params=()):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(query, params)
                return await cur.fetchall()


db = Database(
    host=DB_HOST,
    port=DB_PORT,
    user=DB_USER,
    password=DB_PASSWORD,
    db_name=DB_NAME
)
