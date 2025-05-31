import asyncio
import base64
from turtle import width
from typing import List
from dataclasses import dataclass, field
from importlib import resources
from playwright.async_api import async_playwright, Browser as PlaywrightBrowser, Page
from PIL import Image
from core.browser.utils import scale_b64_image
from core.utils.logger import Logger

logger = Logger.get_logger(name="browser", level="DEBUG")


@dataclass
class ViewportSize:
    width: int
    height: int


# ViewportSize(width=1920, height=1080)
@dataclass
class BrowserConfig:
    viewport_size: tuple[int, int] = field(default_factory=lambda: (1920, 1080))
    detector: List[str] = None
    headless: bool = True
    browser_type: str = "chromium"
    ignoreHTTPSErrors: bool = True
    timeout: int = 30000


EXTRACT_METADATA_SCRIPT = resources.read_text("core.browser.js", "extract_metadata.js")
EXTRACT_HEADERS_SCRIPT = resources.read_text("core.browser.js", "extract_headers.js")
EXTRACT_PRODUCT_INFO_SCRIPT = resources.read_text(
    "core.browser.js", "extract_product_info.js"
)


class Browser:
    def __init__(self, config: BrowserConfig):
        logger.info(f"Initializing browser.")
        self.config = config
        self.logger = logger
        self.playwright = None
        self.browser: PlaywrightBrowser = None
        self.page: Page = None
        self._cdp_session = None

    async def __aenter__(self):
        """Initialize the browser and return the instance."""
        await self._init_browser()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close the browser."""
        await self._close_browser()

    async def _init_browser(self):
        """Initialize the browser."""
        self.playwright = await async_playwright().start()

        # browser_context = getattr(self.playwright, self.config.browser_type)
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=[
                "--disable-gpu",
                "--disable-web-security",  # May help with some CORS issues
                "--disable-features=IsolateOrigins,site-per-process",  # May help with frame issues
            ],
        )

        viewport_height, viewport_width = self.config.viewport_size

        self.page = await self.browser.new_page(
            viewport={"width": viewport_width, "height": viewport_height},
            java_script_enabled=True,
            ignore_https_errors=self.config.ignoreHTTPSErrors,
        )

        self._cdp_session = await self.browser.new_browser_cdp_session()
        await self.page.set_extra_http_headers(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        )

    async def _close_browser(self):
        """Close the browser."""
        if self.page:
            await self.page.close()
            self.page = None

        if self.browser:
            await self.browser.close()
            self.browser = None

        if self.playwright:
            await self.playwright.stop()
            self.playwright = None

        self.logger.info("Browser closed.")
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
                    wait_until="networkidle",
                    timeout=self.config.timeout,
                )
                if response.ok:
                    break
                await asyncio.sleep(1.5)  # Wait for a second to allow the page to load

            except Exception as e:
                self.logger.error(f"Error navigating to {url}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2**attempt)

    async def has_content_loaded(self, detector: List[str] = None):
        """Check if the content has loaded."""
        try:
            await self.page.wait_for_selector("img", state="visible")
            await self.page.wait_for_selector("body", timeout=self.config.timeout)
            self.logger.info("Content loaded successfully.")
            return True
        except Exception as e:
            self.logger.error(f"Error waiting for content to load: {e}")
            return False

    async def extract_headers(self):
        """Extract headers from the page."""
        self.logger.info("Extracting headers from the page.")

        try:
            headers = await self.page.evaluate(EXTRACT_HEADERS_SCRIPT)
            return headers
        except Exception as e:
            self.logger.error(f"Error extracting headers: {e}")
            return None

    async def extract_product_info(self):
        """Extract product information from the page."""
        self.logger.info("Extracting product information from the page.")

        try:
            product_info = await self.page.evaluate(EXTRACT_PRODUCT_INFO_SCRIPT)
            return product_info
        except Exception as e:
            self.logger.error(f"Error extracting product information: {e}")
            return None

    async def extract_metadata(self):
        """Extract metadata from the page."""
        self.logger.info("Extracting metadata and title from the page.")

        try:
            title = await self.page.title()
            metadata = await self.page.evaluate(EXTRACT_METADATA_SCRIPT)
            return {
                "title": title,
                "description": metadata.get("description", ""),
                "keywords": "",
                "metadata": metadata,
            }
        except Exception as e:
            self.logger.error(f"Error extracting metadata: {e}")
            return None

    async def get_cdp_session(self):
        """Get or create cdp session"""

        if (
            self._cdp_session is None
            or not hasattr(self._cdp_session, "_page")
            or self._cdp_session._page != self.current_page
        ):
            self._cdp_session = await self.context.new_cdp_session(self.current_page)
            # Store reference to the page this session belongs to
            self._cdp_session._page = self.current_page
        return self._cdp_session

    async def get_screenshot(self):
        """Returns base64 encoded screenshot of the current page"""

        cdp_session = await self.get_cdp_session()
        screenshot_params = {
            "format": "png",
            "fromSurface": False,
            "captureBeyondViewPort": False,
        }

        screenshot_data = await cdp_session.send(
            "Page.captureScreenshot", screenshot_params
        )
        screenshot_b64 = screenshot_data["data"]
        if self.screenshot_scale_factor is None:

            test_img_data = base64.b64decode(screenshot_b64)
            test_img = Image.open(io.BytesIO(test_img_data))
            logger.info(f"Test image size: {test_img.size}")
            self.screenshot_scale_factor = 1024 / test_img.size[0]
            logger.info(f"Screenshot scale factor: {self.screenshot_scale_factor}")

        screenshot_b64 = scale_b64_image(screenshot_b64, self.screenshot_scale_factor)
        return screenshot_b64
