import logging
from contextlib import asynccontextmanager
from typing import Optional, AsyncIterator, Union, List, Literal, Tuple

from playwright.async_api import Playwright, Browser, async_playwright, Error, Page

_browser: Optional[Browser] = None
_playwright: Optional[Playwright] = None

log = logging.getLogger(__name__)


async def init(**kwargs) -> Browser:
    global _browser
    global _playwright
    _playwright = await async_playwright().start()
    try:
        _browser = await launch_browser(**kwargs)
    except Error:
        await install_browser()
        _browser = await launch_browser(**kwargs)
    return _browser


async def launch_browser(**kwargs) -> Browser:
    assert _playwright is not None, "Playwright is not initialized"
    return await _playwright.chromium.launch(**kwargs)


async def get_browser(**kwargs) -> Browser:
    return _browser or await init(**kwargs)


@asynccontextmanager
async def get_new_page(**kwargs) -> AsyncIterator[Page]:
    browser = await get_browser()
    page = await browser.new_page(**kwargs)
    try:
        yield page
    finally:
        await page.close()


async def screenshot(url: str,
                     *,
                     elements: Optional[Union[List[str]]] = None,
                     timeout: Optional[float] = 100000,
                     wait_until: Literal["domcontentloaded", "load", "networkidle", "load", "commit"] = "networkidle",
                     viewport_size: Tuple[int, int] = (1920, 1080),
                     full_page=True,
                     **kwargs):
    if not url.startswith(('https://', 'http://')):
        url = f'https://{url}'
    viewport_size = {'width': viewport_size[0], 'height': viewport_size[1]}
    browser = await get_browser()
    page = await browser.new_page(
        viewport=viewport_size,
        **kwargs)
    try:
        await page.goto(url, wait_until=wait_until, timeout=timeout)
        assert page
        if not elements:
            return await page.screenshot(timeout=timeout, full_page=full_page)

        for e in elements:
            card = await page.wait_for_selector(e, timeout=timeout, state='visible')
            assert card
            clip = await card.bounding_box()
        return await page.screenshot(clip=clip, timeout=timeout, full_page=full_page, path='Temp/post_screenshot.png')
    except Exception as e:
        raise e
    finally:
        await page.close()


async def shutdown_browser():
    if _browser:
        await _browser.close()
    if _playwright:
        await _playwright.stop()  # type: ignore


async def install_browser():
    import sys
    import os

    from playwright.__main__ import main
    log.info("正在安装 chromium")
    sys.argv = ["", "install", "chromium"]
    try:
        log.info("正在安装依赖")
        os.system("playwright install-deps")
        main()
    except SystemExit:
        pass
