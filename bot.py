from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties
import asyncio
from config import *
from db.db import db
from db.init_db import init_database


from handlers import register_all_routers


bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()
register_all_routers(dp)


async def main():
    logger.info("Запускаем TechLineBot...")
    await db.connect()
    await init_database()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())