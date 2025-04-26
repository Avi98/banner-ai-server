import asyncio
from typing import List
from dataclasses import dataclass, field
from importlib import resources
from cv2 import log
from pyppeteer import launch

from core.utils.logger import Logger

logger = Logger.get_logger(name="browser", level="DEBUG")


@dataclass
class ViewportSize:
    width: int
    height: int


@dataclass
class BrowserConfig:
    viewport_size: ViewportSize = field(default=ViewportSize(width=1920, height=1080))
    detector: List[str] = None
    headless: bool = True
    browser_type: str = "chrome"
    ignoreHTTPSErrors: bool = True
    timeout: int = 30000


EXTRACT_METADATA_SCRIPT = resources.read_text("core.browser.js", "extract_metadata.js")


class Browser:
    def __init__(self, config: BrowserConfig):
        logger.info(f"Initializing browser.")
        self.config = config
        self.logger = logger

    async def __aenter__(self):
        """Initialize the browser and return the instance."""
        await self._init_browser()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close the browser."""
        await self._close_browser()

    async def _init_browser(self):
        """Initialize the browser."""
        self.browser = await launch(
            headless=self.config.headless,
            ignoreHTTPSErrors=self.config.ignoreHTTPSErrors,
            timeout=self.config.timeout,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-web-security",  # May help with some CORS issues
                "--disable-features=IsolateOrigins,site-per-process",  # May help with frame issues
            ],
        )
        self.page = await self.browser.newPage()
        await self.page.setViewport(self.config.viewport_size.__dict__)
        await self.page.setUserAgent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        await self.page.setJavaScriptEnabled(True)
        self.page.setDefaultNavigationTimeout(0)

    async def _close_browser(self):
        """Close the browser."""
        if self.browser:
            await self.browser.close()

            self.logger.info("Browser closed.")
        else:
            self.logger.warning("Browser was not initialized.")
        self.browser = None
        self.page = None
        self.logger = None

    async def navigate_with_retry(self, url: str, max_retries: int = 3):
        """Navigate to a URL with retry logic."""
        for attempt in range(max_retries):
            try:
                self.logger.info(
                    f"Attempting to navigate to {url} (Attempt {attempt + 1})"
                )
                response = await self.page.goto(
                    url,
                    waitUntil=["networkidle2", "domcontentloaded"],
                    timeout=self.config.timeout,
                )
                # logger.info(f"Page response: {pageresponse.status}")
                if response.status == 200:
                    break

                await asyncio.sleep(1.5)  # Wait for a second to allow the page to load

            except Exception as e:
                self.logger.error(f"Error navigating to {url}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2**attempt)

    async def has_content_loaded(self, detector: List[str] = None):
        """Check if the content has loaded."""
        try:
            # await self.page.wait_for_content_loaded(page=self.page)
            await self.page.waitForSelector("img", {"visible": True})
            await self.page.waitForSelector("body", timeout=self.config.timeout)
            self.logger.info("Content loaded successfully.")
            return True
        except Exception as e:
            self.logger.error(f"Error waiting for content to load: {e}")
            return False

    async def extract_metadata(self):
        """Extract metadata from the page."""
        self.logger.info("Extracting metadata and title from the page.")

        try:
            title = await self.page.evaluate("document.title")
            description = await self.page.evaluate(
                "document.querySelector('meta[name=\"description\"]').content"
            )
            # keywords = await self.page.evaluate(
            #     "document.querySelector('meta[name=\"keywords\"]').content"
            # )
            metadata = await self.page.evaluate(EXTRACT_METADATA_SCRIPT)
            return {
                "title": title,
                "description": description,
                "keywords": "",
                "metadata": metadata,
            }
        except Exception as e:
            self.logger.error(f"Error extracting metadata: {e}")
            return None
