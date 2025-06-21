import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command


logging.basicConfig(level=logging.INFO)

bot = Bot(token="8056672850:AAEIwgFTrT-_LDg4ds8PYRtjsHHLC70CYdw")
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет Детям223332222!")


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())