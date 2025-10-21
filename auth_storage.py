import logging
import asyncio
from playwright.async_api import async_playwright


async def prepare_storage():
    logging.basicConfig(level=logging.INFO)

    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch_persistent_context(
        user_data_dir="./user_data",
        headless=False,
        slow_mo=50,
        args=["--start-maximized"]
    )
    page = await browser.new_page()

    await page.goto("https://2gis.ru")
    logging.info("Открылся браузер. Выполните авторизацию вручную.")

    await asyncio.sleep(180)  # 3 минуты на авторизацию

    logging.info("✅ Состояние сохранено автоматически в папке ./user_data")

    await browser.close()
    await playwright.stop()


if __name__ == '__main__':
    asyncio.run(prepare_storage())
