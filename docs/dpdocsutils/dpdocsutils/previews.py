import os
import shutil
import asyncio
import nest_asyncio
from pyppeteer import launch
from IPython.display import IFrame, display, HTML
from pathlib import Path


nest_asyncio.apply()


async def screenshot_html(report_path, image_path, width, height):
    # Pyppeteer doesn't package an M1 version of Chromium for MacOS yet, allow for using the system package.
    # 'chromium' is for MacOS, 'chromium-browser' is for Fedora.
    chromium_path = shutil.which('chromium') or shutil.which('chromium-browser')  # or None

    browser = await launch(headless=True, executablePath=chromium_path)
    page = await browser.newPage()
    await page.goto(
        f"file://{os. getcwd()}/{report_path}",
        {"waitUntil": "networkidle0", "timeout": 60000},
    )
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


def embed_local_report(report_path, width, height, iframe=False):
    if iframe:
        return IFrame(report_path, width=width, height=height)
    else:
        width = 700
        report_filename = Path(report_path).name
        image_filename = report_filename.replace(".html", "-preview.png")
        report_to_image(report_filename, image_filename, width, height)

        image_path = report_path.replace(".html", "-preview.png")
        return display(HTML(f'<a href="{report_path}"><img src="{image_path}"></a>'))
