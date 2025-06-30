import logging
import asyncio
from typing import Tuple, List, Optional
from pprint import pprint as pp
from playwright.async_api import async_playwright, Page, BrowserContext, TimeoutError as PlaywrightTimeoutError


def clean_text(text: str) -> str:
    return (
        text.replace('\xa0', ' ')
            .replace('\u200b', '')
            .strip()
    )


class DGisParser:
    def __init__(self, headless: bool = True):
        self.playwright = None
        self.browser: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.user_data_dir = "./user_data"
        self.headless = headless

    async def start(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=self.user_data_dir,
            headless=self.headless,
            slow_mo=50,
            args=[]
        )
        self.page = await self.browser.new_page()
        await self.page.goto("https://2gis.ru")

    async def stop(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def is_card_opened(self) -> bool:
        try:
            await self.page.wait_for_selector("div._49kxlr", timeout=5000)
            return True
        except PlaywrightTimeoutError:
            return False

    async def search_addresses(self, query: str, city_url: str) -> Tuple[List[dict], bool]:
        await self.page.goto(city_url)

        await self.page.wait_for_selector("input[placeholder='Поиск в 2ГИС']", timeout=10000)
        await self.page.fill("input[placeholder='Поиск в 2ГИС']", query)
        await self.page.keyboard.press("Enter")
        await self.page.wait_for_timeout(3000)

        if await self.is_card_opened():
            return [], True

        results = []
        try:
            await self.page.wait_for_selector("div._awwm2v", timeout=5000)
            blocks = self.page.locator("div._awwm2v div._1kf6gff")
            count = await blocks.count()

            for i in range(count):
                title = await blocks.nth(i).locator("a._1rehek").first.text_content()
                type_ = await blocks.nth(i).locator("div._1idnaau span._oqoid").first.text_content()
                href = await blocks.nth(i).locator("a._1rehek").first.get_attribute("href")

                if title and type_ and href:
                    type_ = type_.lower()
                    if any(word in type_ for word in ["жилой дом", "многоквартирный дом", "дом"]):
                        results.append({
                            "title": clean_text(title),
                            "url": f"https://2gis.ru{href.strip()}"
                        })
            return results, False

        except PlaywrightTimeoutError:
            return [], False

    async def parse_address(self, url: str = None) -> dict:
        if url:
            await self.page.goto(url)

        await self.page.wait_for_timeout(2000)

        info = {
            "title": "Не найдено",
            "floors": "Не указано",
            "entrances": "Не указано",
            "apartments": [],
            "address": ""
        }

        try:
            await self.page.wait_for_selector("div._49kxlr", timeout=15000)

            title_elem = self.page.locator("h1._1x89xo5 span").first
            if await title_elem.is_visible():
                info["title"] = clean_text(await title_elem.text_content())

            addr_parts = await self.page.locator("div._1idnaau span._sfdp8cg").all_text_contents()
            if addr_parts:
                info["address"] = clean_text(', '.join(addr_parts))

            floors_blocks = await self.page.locator("div._49kxlr span._wrdavn").all_text_contents()
            for block in floors_blocks:
                if "этаж" in block:
                    info["floors"] = clean_text(block)

            entrances_elem = self.page.locator("div._ksc2xc").first
            if await entrances_elem.is_visible():
                entrances_text = await entrances_elem.text_content()
                if entrances_text and "подъезд" in entrances_text:
                    info["entrances"] = clean_text(entrances_text)

            try:
                toggle = self.page.locator('div._z3fqkm')
                if await toggle.is_visible():
                    arrow = await toggle.locator('svg').get_attribute('style') or ""
                    if 'rotate(0deg)' in arrow:
                        await toggle.click()
                        await self.page.wait_for_selector('div._1ovqm446', timeout=5000)
                        await self.page.wait_for_timeout(1000)
            except Exception:
                pass

            apartments = self.page.locator("div._1y6lfljs")
            count = await apartments.count()
            for i in range(count):
                apt = await apartments.nth(i).text_content()
                if apt:
                    info["apartments"].append(clean_text(apt))

        except PlaywrightTimeoutError:
            pass

        return info


async def parse_house_from_2gis(city_url: str, search_query: str) -> Optional[dict]:
    parser = DGisParser(headless=False)
    await parser.start()

    try:
        results, is_direct = await parser.search_addresses(search_query, city_url)

        if is_direct:
            info = await parser.parse_address()
        elif results:
            info = await parser.parse_address(results[0]['url'])
        else:
            info = None

    except Exception as e:
        await parser.stop()
        raise e

    await parser.stop()
    return info



if __name__ == '__main__':
    result = asyncio.run(parse_house_from_2gis(city_url="https://2gis.ru/kazan", search_query="Гаврилова 2"))
    pp(result)
