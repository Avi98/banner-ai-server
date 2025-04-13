import asyncio
from pyppeteer import launch
import os
import json
import time
from urllib.parse import urlparse, urljoin

from core.utils.logger import Logger
from .js_extractor_fn import (
    EXTRACT_FONTS_JS,
    EXTRACT_THEME_JS,
    EXTRACT_LOGO_JS,
    EXTRACT_PRODUCTS_JS,
    EXTRACT_INVENTORY_JS,
)


class WebScraper:
    def __init__(
        self, url: str, output_dir: str = "scraped_data", timeout: int = 30000
    ):
        self.url = url
        self.output_dir = output_dir
        self.domain = urlparse(url).netloc
        self.timeout = timeout
        self.logger = Logger.get_logger()

        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            os.makedirs(os.path.join(output_dir, "images"))

    async def navigate_with_retry(self, page, url, max_retries=3):
        """Navigate to URL with retry logic"""
        retries = 0
        while retries < max_retries:
            try:
                self.logger.info(
                    f"Navigating to {url} (attempt {retries+1}/{max_retries})"
                )
                response = await page.goto(
                    url,
                    waitUntil=["domcontentloaded"],  # Less strict wait condition
                    timeout=self.timeout,
                )

                # Check if page loaded successfully
                if response and response.ok:
                    # Additional wait for network to settle
                    try:
                        await page.waitForFunction(
                            '() => document.readyState === "complete"',
                            {"timeout": 5000},
                        )
                    except:
                        self.logger.warning("Page loaded but readyState wait timed out")

                    return response
                else:
                    self.logger.warning(
                        f"Navigation returned status: {response.status if response else 'None'}"
                    )

            except Exception as e:
                self.logger.warning(f"Navigation attempt {retries+1} failed: {str(e)}")

            retries += 1
            # Wait between retries with exponential backoff
            await page.waitForTimeout(1000 * (2**retries))

        raise Exception(f"Failed to navigate to {url} after {max_retries} attempts")

    async def scrape(self):
        """Main scraping function for e-commerce stores"""
        self.logger.info(f"Starting scrape of {self.url}")

        browser = await launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-web-security",  # May help with some CORS issues
                "--disable-features=IsolateOrigins,site-per-process",  # May help with frame issues
            ],
            ignoreHTTPSErrors=True,  # Ignore HTTPS errors
            timeout=self.timeout * 2,  # Browser launch timeout
        )

        results = {
            "url": self.url,
            "fonts": {},
            "theme": {},
            "logo": None,
            "products": [],
            # "inventory": {},
        }

        try:
            page = await browser.newPage()

            # Set viewport size
            await page.setViewport({"width": 1920, "height": 1080})

            # Set user agent to a more common one
            await page.setUserAgent(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )

            # Enable JavaScript
            await page.setJavaScriptEnabled(True)

            # Disable timeout
            page.setDefaultNavigationTimeout(0)

            # Navigate with retry logic
            response = await self.navigate_with_retry(page, self.url)

            if not response:
                self.logger.error("Failed to load page: No response")
                results["error"] = "Failed to load page: No response"
                return results

            # Check if we need more time for any animations or lazy loading
            await self.wait_for_content_to_load(page)

            # Extract font styles
            self.logger.info("Extracting font styles")
            results["fonts"] = await page.evaluate(EXTRACT_FONTS_JS)

            # Extract theme colors
            self.logger.info("Extracting theme colors")
            results["theme"] = await page.evaluate(EXTRACT_THEME_JS)

            # Extract logo
            self.logger.info("Extracting logo")
            results["logo"] = await page.evaluate(EXTRACT_LOGO_JS)

            # Extract product images
            self.logger.info("Extracting product images")
            results["products"] = await page.evaluate(EXTRACT_PRODUCTS_JS)

            # Download product images
            # await self.download_product_images(page, results["products"])

            # Extract inventory information
            # self.logger.info("Extracting inventory information")
            # results["inventory"] = await page.evaluate(EXTRACT_INVENTORY_JS)

            # Save the results to a JSON file
            self._save_results(results)

            return results

        except Exception as e:
            self.logger.error(f"An error occurred: {str(e)}", exc_info=True)
            results["error"] = str(e)
            return results
        finally:
            await browser.close()
            self.logger.info("Browser closed")

    async def wait_for_content_to_load(self, page):
        """Wait for dynamic content to load"""
        try:
            # Wait for common web elements to appear
            selectors = [
                "img",
                ".product",
                ".product-card",
                ".product-item",
                "h1",
                "header",
            ]

            for selector in selectors:
                try:
                    # Use a short timeout for each selector to avoid getting stuck
                    await page.waitForSelector(selector, {"timeout": 3000})
                    self.logger.info(f"Found selector: {selector}")
                    # If we find one of these elements, we can assume the page is loaded enough
                    return
                except:
                    continue

            # If no selectors are found, wait a bit more just in case
            await page.waitForTimeout(5000)

        except Exception as e:
            self.logger.warning(f"Error in wait_for_content_to_load: {str(e)}")
            # Continue anyway - this is just an additional wait

    async def safe_download_image(self, page, image_url, save_path):
        """Safely download an image with error handling"""
        if not image_url or image_url.startswith("data:"):
            return None

        try:
            # Make sure URL is absolute
            if not image_url.startswith(("http://", "https://")):
                image_url = urljoin(self.url, image_url)

            # Create a new page for downloading to avoid navigation issues
            download_page = await page.browser.newPage()
            try:
                # Try to fetch the image
                response = await download_page.goto(
                    image_url, waitUntil="networkidle0", timeout=10000
                )

                if response and response.ok:
                    img_buffer = await response.buffer()

                    with open(save_path, "wb") as f:
                        f.write(img_buffer)

                    return save_path
            finally:
                await download_page.close()

        except Exception as e:
            self.logger.error(f"Failed to download image {image_url}: {str(e)}")
            return None

    async def download_product_images(self, page, products):
        """Download product images with limits to avoid timeouts"""
        max_images_to_download = 5
        images_downloaded = 0

        for i, product in enumerate(products):
            if "images" in product and product["images"]:
                for j, image in enumerate(product["images"]):
                    if images_downloaded >= max_images_to_download:
                        image["download_skipped"] = True
                        continue

                    if "url" in image and image["url"]:
                        try:
                            img_filename = f"product_{i}_image_{j}.png"
                            img_path = os.path.join(
                                self.output_dir, "images", img_filename
                            )

                            # Download using our safe method
                            saved_path = await self.safe_download_image(
                                page, image["url"], img_path
                            )
                            if saved_path:
                                image["local_path"] = saved_path
                                images_downloaded += 1

                        except Exception as e:
                            self.logger.error(
                                f"Error downloading product image: {str(e)}"
                            )
                            image["download_error"] = str(e)

        if images_downloaded < len(
            [img for p in products for img in p.get("images", [])]
        ):
            self.logger.info(
                f"Downloaded {images_downloaded} images, skipped the rest to avoid timeouts"
            )

    def _save_results(self, results):
        """Save the results to a JSON file"""
        output_file = os.path.join(self.output_dir, f"{self.domain}_data.json")
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Results saved to {output_file}")
        except Exception as e:
            self.logger.error(f"Error saving results: {str(e)}")


# # Example usage
# async def main():
#     # scraper = WebScraper("https://digistore-uat.mintoak.com/20", "scraped_data", timeout=60000)
#     # scraper = WebScraper("https://tech-with-tim-merch-shop.creator-spring.com/listing/coffee-code-light?product=46&variation=2742", "scraped_data", timeout=60000)
#     # scraper = WebScraper("https://id.vyaparify.com/nxtgen-supermarket", "scraped_data", timeout=60000)
#     scraper = WebScraper(
#         "https://demo.vercel.store/product/acme-geometric-circles-t-shirt",
#         "scraped_data",
#         timeout=60000,
#     )
#     results = await scraper.scrape()
#     print(f"Scraping completed. Found {len(results['products'])} products.")
#     return results


# # Run the scraper
# if __name__ == "__main__":
#     asyncio.get_event_loop().run_until_complete(main())
