import os
import subprocess
import asyncio
import nest_asyncio
from pyppeteer import launch
from IPython.display import IFrame

nest_asyncio.apply()


async def screenshot_html(report_path, image_path, width, height):
    chromium_path = (
        subprocess.check_output("which chromium", shell=True).decode().strip()
    )
    browser = await launch(headless=True, executablePath=chromium_path)
    page = await browser.newPage()
    await page.goto(f"file://{os. getcwd()}/{report_path}")
    await page.setViewport({"deviceScaleFactor": 2, "width": width, "height": height})
    await page.screenshot(
        {
            "path": image_path,
        }
    )
    await browser.close()


def report_to_image(report_path, image_path, width, height):
    asyncio.get_event_loop().run_until_complete(
        screenshot_html(report_path, image_path, width, height)
    )


def embed_local_report(report_path, width, height):
    return IFrame(report_path, width=width, height=height)
