import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

from config import *
from handlers import register_all_routers

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


dp = Dispatcher()
register_all_routers(dp)


async def main():
    logger.info("Запускаем TechLineBot...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
