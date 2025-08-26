import asyncio
import base64
import io
from typing import Any, List, Optional, Tuple
from dataclasses import dataclass, field
from importlib import resources
from playwright.async_api import (
    async_playwright,
    Browser as PlaywrightBrowser,
    Page,
    Playwright,
    BrowserContext,
    CDPSession,
)
from PIL import Image
from core.browser.utils import scale_b64_image
from core.utils.logger import Logger
from global_type.types import HeadingDict, PageMeta


@dataclass
class ViewportSize:
    width: int
    height: int


# ViewportSize(width=1920, height=1080)
@dataclass
class BrowserConfig:
    viewport_size: Tuple[int, int] = field(default_factory=lambda: (1920, 1080))
    detector: Optional[List[str]] = field(default=None)
    headless: bool = True
    browser_type: str = "chromium"
    ignoreHTTPSErrors: bool = True
    timeout: int = 30000


EXTRACT_METADATA_SCRIPT = resources.read_text(
    "core.browser.js", "extract_metadata.js"
)
EXTRACT_HEADERS_SCRIPT = resources.read_text(
    "core.browser.js", "extract_headers.js"
)
EXTRACT_PRODUCT_INFO_SCRIPT = resources.read_text(
    "core.browser.js", "extract_product_info.js"
)


class Browser:
    def __init__(self, config: BrowserConfig) -> None:
        logger = Logger.get_logger(name="browser", level="DEBUG")

        logger.info("Initializing browser")
        self.config = config
        self.logger = logger
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[PlaywrightBrowser] = None
        self.page: Optional[Page] = None
        self._cdp_session: Optional[CDPSession] = None
        self.context: Optional[BrowserContext] = None
        self.screenshot_scale_factor: Optional[float] = None

    async def __aenter__(self) -> "Browser":
        """Initialize the browser and return the instance."""
        await self._init_browser()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Close the browser."""
        await self._close_browser()

    async def _init_browser(self) -> None:
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

        viewport_width, viewport_height = self.config.viewport_size

        self.page = await self.browser.new_page(
            viewport={"width": viewport_width, "height": viewport_height},
            java_script_enabled=True,
            ignore_https_errors=self.config.ignoreHTTPSErrors,
        )

        self.context = self.browser.contexts[0]
        self._cdp_session = await self.browser.new_browser_cdp_session()
        await self.page.set_extra_http_headers(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        )

    async def _close_browser(self) -> None:
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

    async def navigate_with_retry(self, url: str, max_retries: int = 3) -> None:
        """Navigate to a URL with retry logic."""
        for attempt in range(max_retries):
            try:
                self.logger.info(
                    f"Attempting to navigate to {url} (Attempt {attempt + 1})"
                )

                assert self.page is not None

                response = await self.page.goto(
                    url,
                    # wait_untille",
                    wait_until="load",
                    timeout=self.config.timeout,
                )

                assert response
                assert response.ok is not None, f"Error while fetching response {response.status}"

                if response.ok:
                    break
                # Wait for a second to allow the page to load
                await asyncio.sleep(1.5)

            except Exception as e:
                self.logger.error(f"Error navigating to {url}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2**attempt)

    async def has_content_loaded(
        self,
    ) -> bool:
        """Check if the content has loaded."""
        try:

            assert self.page
            assert self.page.wait_for_selector is not None, f"Error while fetching wait for selector {self.page}"

            await self.page.wait_for_selector("body", timeout=self.config.timeout)
            self.logger.info("Content loaded successfully.")
            return True
        except Exception as e:
            self.logger.error(f"Error waiting for content to load: {e}")
            return False

    async def extract_headers(self) -> Optional[dict[str, str]]:
        """Extract headers from the page."""
        self.logger.info("Extracting headers from the page.")
        assert self.page is not None
        try:
            headers = await self.page.evaluate(EXTRACT_HEADERS_SCRIPT)
            return headers  # type: ignore
        except Exception as e:
            self.logger.error(f"Error extracting headers: {e}")
            return None

    async def extract_product_info(self) -> Optional[HeadingDict]:
        """Extract product information from the page."""
        self.logger.info("Extracting product information from the page.")
        assert self.page is not None
        try:
            product_info: HeadingDict = await self.page.evaluate(EXTRACT_PRODUCT_INFO_SCRIPT)
            return product_info
        except Exception as e:
            self.logger.error(f"Error extracting product information: {e}")
            return None

    async def extract_metadata(self) -> Optional[PageMeta]:
        """Extract metadata from the page."""
        self.logger.info("Extracting metadata and title from the page.")
        assert self.page is not None
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

    async def get_cdp_session(self) -> CDPSession:
        """Get or create cdp session"""
        assert self.context is not None
        assert self.page is not None
        if self._cdp_session is None:
            self._cdp_session = await self.context.new_cdp_session(self.page)
        return self._cdp_session

    async def get_screenshot(self) -> Optional[str]:
        """Returns base64 encoded screenshot of the current page"""
        assert self.page is not None
        await self.page.wait_for_load_state("load")

        cdp_session = await self.get_cdp_session()
        screenshot_params = {
            "format": "png",
            "fromSurface": True,
            "captureBeyondViewPort": False,
        }
        try:
            screenshot_data =   await cdp_session.send(
                "Page.captureScreenshot", screenshot_params
            )
            screenshot_b64 = screenshot_data["data"]
        except Exception as e:
            self.logger.warning(
                f"CDP screenshot failed: {e}, using Playwright API."
            )
            try:
                screenshot_bytes = await self.page.screenshot(type="png")
                screenshot_b64 = base64.b64encode(screenshot_bytes).decode()
            except Exception as e2:
                self.logger.error(f"Playwright screenshot also failed: {e2}")
                return None

        if self.screenshot_scale_factor is None:
            test_img_data = base64.b64decode(screenshot_b64)
            test_img = Image.open(io.BytesIO(test_img_data))
            self.logger.info(f"Test image size: {test_img.size}")
            self.screenshot_scale_factor = 1024 / test_img.size[0]
            self.logger.info(
                f"Screenshot scale factor: {self.screenshot_scale_factor}"
            )

        screenshot_b64 = scale_b64_image(
            screenshot_b64, self.screenshot_scale_factor
        )
        return screenshot_b64