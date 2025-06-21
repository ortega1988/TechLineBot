import asyncio
import logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command




load_dotenv()
TOKEN = os.getenv("TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет Лошарам!")


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())