import asyncio
from pyppeteer import launch, page
import os
import json
import time
from urllib.parse import urlparse, urljoin

from core.utils.logger import Logger
from .js_extractor_fn import (
    EXTRACT_CURRENCY_JS,
    EXTRACT_FONTS_JS,
    EXTRACT_THEME_JS,
    EXTRACT_LOGO_JS,
    EXTRACT_CONTACT_INFO_JS,
    EXTRACT_METADATA_JS,
    EXTRACT_NAVIGATION_JS,
    EXTRACT_CATEGORIES_JS,
    EXTRACT_PRODUCTS_WITH_METADATA_JS,
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

    async def navigate_with_retry(self, page: page.Page, url, max_retries=3):
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
        """Enhanced scraping function for e-commerce stores that extracts metadata, title, and product categories"""
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
            "title": None,
            "metadata": {
                "description": None,
                "keywords": None,
                "author": None,
                "canonical": None,
                "og_tags": {},
                "twitter_tags": {},
                "schema_org": None,
            },
            "platform": None,  # E-commerce platform (Shopify, WooCommerce, etc.)
            "fonts": {},
            "theme": {},
            "logo": None,
            "products": [],
            "categories": [],
            "navigation": [],
            "contact_info": {
                "email": None,
                "phone": None,
                "address": None,
                "social_media": {},
            },
            "currency": None,
        }

        try:
            page = await browser.newPage()

            # Configure page settings
            await page.setViewport({"width": 1920, "height": 1080})
            await page.setUserAgent(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
            await page.setJavaScriptEnabled(True)
            page.setDefaultNavigationTimeout(0)

            # Set request interception to block unnecessary resources
            # await page.setRequestInterception(True)

            # @page.on("request")
            # async def intercept_request(request):
            #     # Block unnecessary resource types to improve performance
            #     if request.resourceType in ["image", "media", "font"]:
            #         await request.abort()
            #     else:
            #         await request.continue_()

            # Navigate with retry logic
            response = await self.navigate_with_retry(page, self.url)
            if not response:
                self.logger.error("Failed to load page: No response")
                results["error"] = "Failed to load page: No response"
                return results

            # Wait for content to load
            await self.wait_for_content_to_load(page)

            # Extract page title
            self.logger.info("Extracting page title")
            results["title"] = await page.title()

            # Extract metadata
            self.logger.info("Extracting metadata")
            results["metadata"] = await page.evaluate(EXTRACT_METADATA_JS)

            # Detect e-commerce platform
            self.logger.info("Detecting e-commerce platform")
            results["platform"] = await page.evaluate(
                """() => {
                // Common platform signatures
                if (window.Shopify) return 'Shopify';
                if (document.querySelector('meta[name="generator"][content*="WooCommerce"]')) return 'WooCommerce';
                if (document.querySelector('meta[name="generator"][content*="Magento"]')) return 'Magento';
                if (document.querySelector('link[href*="shopifycdn"]')) return 'Shopify';
                if (document.querySelector('script[src*="bigcommerce.com"]')) return 'BigCommerce';
                if (document.querySelector('script[src*="squarespace.com"]')) return 'Squarespace';
                if (document.querySelector('script[src*="wix.com"]')) return 'Wix';
                
                // Check for common script/link patterns
                const scripts = Array.from(document.getElementsByTagName('script'));
                const links = Array.from(document.getElementsByTagName('link'));
                
                for (const script of scripts) {
                    const src = script.src || '';
                    const content = script.textContent || '';
                    
                    if (src.includes('prestashop') || content.includes('prestashop')) return 'PrestaShop';
                    if (src.includes('opencart') || content.includes('opencart')) return 'OpenCart';
                    if (content.includes('Drupal.settings') || content.includes('drupal')) return 'Drupal Commerce';
                    if (content.includes('jQuery(document).ready(function(jQuery)') && content.includes('wc_')) return 'WooCommerce';
                }
                
                for (const link of links) {
                    const href = link.href || '';
                    if (href.includes('wp-content/themes')) return 'WordPress';
                }
                
                return 'Unknown';
            }"""
            )

            # Extract font styles
            self.logger.info("Extracting font styles")
            results["fonts"] = await page.evaluate(EXTRACT_FONTS_JS)

            # Extract theme colors
            self.logger.info("Extracting theme colors")
            results["theme"] = await page.evaluate(EXTRACT_THEME_JS)

            # Extract logo
            self.logger.info("Extracting logo")
            results["logo"] = await page.evaluate(EXTRACT_LOGO_JS)

            # Extract currency
            self.logger.info("Extracting currency")
            results["currency"] = await page.evaluate(EXTRACT_CURRENCY_JS)

            # Extract product categories
            self.logger.info("Extracting product categories")
            results["categories"] = await page.evaluate(EXTRACT_CATEGORIES_JS)

            # Extract navigation structure
            self.logger.info("Extracting navigation structure")
            results["navigation"] = await page.evaluate(EXTRACT_NAVIGATION_JS)

            # Extract contact information
            self.logger.info("Extracting contact information")
            results["contact_info"] = await page.evaluate(EXTRACT_CONTACT_INFO_JS)

            # Extract product information with enhanced metadata
            self.logger.info("Extracting products with metadata")

            # Extract products with enhanced metadata
            results["products"] = await page.evaluate(EXTRACT_PRODUCTS_WITH_METADATA_JS)

            # Save the results to a JSON file
            # self._save_results(results)
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
                            # saved_path = await self.safe_download_image(
                            # page, image["url"], img_path
                            # )
                            # if saved_path:
                            #     image["local_path"] = saved_path
                            #     images_downloaded += 1

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
#     # scraper = WebScraper("https://id.vyaparify.com/nxtgen-supermarket/product/pouch-with-avenger-theme-for-boys", "scraped_data", timeout=60000)
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
