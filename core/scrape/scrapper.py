import asyncio
from pyppeteer import launch, page
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

    async def navigate_with_retry(self, page: page.Page, url, max_retries=3):
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
            results["metadata"] = await page.evaluate(
                """() => {
                const metadata = {
                    description: document.querySelector('meta[name="description"]')?.content || null,
                    keywords: document.querySelector('meta[name="keywords"]')?.content || null,
                    author: document.querySelector('meta[name="author"]')?.content || null,
                    canonical: document.querySelector('link[rel="canonical"]')?.href || null,
                    og_tags: {},
                    twitter_tags: {},
                    schema_org: null
                };
                
                // Extract Open Graph tags
                const ogTags = document.querySelectorAll('meta[property^="og:"]');
                ogTags.forEach(tag => {
                    const property = tag.getAttribute('property').substring(3);
                    metadata.og_tags[property] = tag.content;
                });
                
                // Extract Twitter tags
                const twitterTags = document.querySelectorAll('meta[name^="twitter:"]');
                twitterTags.forEach(tag => {
                    const property = tag.getAttribute('name').substring(8);
                    metadata.twitter_tags[property] = tag.content;
                });
                
                // Extract Schema.org structured data
                const schemaScripts = document.querySelectorAll('script[type="application/ld+json"]');
                if (schemaScripts.length > 0) {
                    try {
                        const schemaData = [];
                        schemaScripts.forEach(script => {
                            try {
                                schemaData.push(JSON.parse(script.textContent));
                            } catch (e) {
                                // Skip invalid JSON
                            }
                        });
                        metadata.schema_org = schemaData;
                    } catch (e) {
                        // Failed to parse JSON
                    }
                }
                
                return metadata;
            }"""
            )

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
            results["currency"] = await page.evaluate(
                """() => {
                // Check for currency in meta tags first
                const currencyMeta = document.querySelector('meta[property="og:price:currency"]');
                if (currencyMeta) return currencyMeta.content;
                
                // Look for currency symbols in price elements
                const priceElements = document.querySelectorAll('.price, [class*="price"], .amount, .currency');
                const currencySymbols = {
                    '$': 'USD', '£': 'GBP', '€': 'EUR', '¥': 'JPY', '₹': 'INR',
                    '₽': 'RUB', '₩': 'KRW', '₿': 'BTC', 'A$': 'AUD', 'C$': 'CAD'
                };
                
                for (const el of priceElements) {
                    const text = el.textContent.trim();
                    for (const symbol in currencySymbols) {
                        if (text.includes(symbol)) {
                            return currencySymbols[symbol];
                        }
                    }
                    
                    // Check for currency codes
                    const currencyCodes = ['USD', 'EUR', 'GBP', 'JPY', 'CAD'];
                    for (const code of currencyCodes) {
                        if (text.includes(code)) {
                            return code;
                        }
                    }
                }
                
                return null;
            }"""
            )

            # Extract product categories
            self.logger.info("Extracting product categories")
            results["categories"] = await page.evaluate(
                """() => {
                const categories = [];
                
                // Check for category navigation
                const potentialCategoryContainers = [
                    'nav', '.nav', '.navigation', '.categories', '.menu', '.navbar',
                    '[class*="category"]', '[class*="categories"]', '[class*="menu"]', '[class*="nav"]',
                    'header', 'aside', '.sidebar'
                ];
                
                for (const selector of potentialCategoryContainers) {
                    const containers = document.querySelectorAll(selector);
                    for (const container of containers) {
                        // Look for links that might be categories
                        const links = container.querySelectorAll('a');
                        
                        if (links.length > 0) {
                            // Check if these might be category links (more than 2 but fewer than 20)
                            if (links.length >= 2 && links.length < 20) {
                                for (const link of links) {
                                    const href = link.getAttribute('href') || '';
                                    const text = link.textContent.trim();
                                    
                                    // Skip empty, login, cart, and other utility links
                                    if (!text || text.length < 2) continue;
                                    if (/login|sign|cart|checkout|account|search|contact|about/i.test(text)) continue;
                                    
                                    // Check for category URL patterns
                                    if (href && (href.includes('/category/') || 
                                            href.includes('/collections/') ||
                                            href.includes('/product-category/') ||
                                            href.match(/\/c\/[\\w-]+\/?$/))) {
                                        categories.push({
                                            name: text,
                                            url: new URL(href, window.location.origin).href
                                        });
                                        continue;
                                    }
                                    
                                    // Include if it looks like a category (no symbols, not too long)
                                    if (text && text.length < 25 && !/[\\d\\W]/.test(text)) {
                                        categories.push({
                                            name: text,
                                            url: new URL(href, window.location.origin).href
                                        });
                                    }
                                }
                                
                                // If we found categories, stop looking
                                if (categories.length > 0) break;
                            }
                        }
                    }
                    
                    if (categories.length > 0) break;
                }
                
                // If no categories found via navigation, check breadcrumbs
                if (categories.length === 0) {
                    const breadcrumbs = document.querySelectorAll('.breadcrumb, .breadcrumbs, [class*="breadcrumb"]');
                    for (const breadcrumb of breadcrumbs) {
                        const links = breadcrumb.querySelectorAll('a');
                        for (const link of links) {
                            const text = link.textContent.trim();
                            if (text && text !== 'Home' && text !== 'Main') {
                                categories.push({
                                    name: text,
                                    url: new URL(link.getAttribute('href'), window.location.origin).href
                                });
                            }
                        }
                    }
                }
                
                // Check for Schema.org breadcrumb markup
                const breadcrumbSchema = document.querySelector('script[type="application/ld+json"]');
                if (breadcrumbSchema) {
                    try {
                        const data = JSON.parse(breadcrumbSchema.textContent);
                        if (data && data['@type'] === 'BreadcrumbList') {
                            const items = data.itemListElement || [];
                            for (const item of items) {
                                if (item.name && item.name !== 'Home') {
                                    categories.push({
                                        name: item.name,
                                        url: item.item || ''
                                    });
                                }
                            }
                        }
                    } catch (e) {
                        // JSON parse error, ignore
                    }
                }
                
                return categories;
            }"""
            )

            # Extract navigation structure
            self.logger.info("Extracting navigation structure")
            results["navigation"] = await page.evaluate(
                """() => {
                const nav = [];
                const mainNav = document.querySelector('nav, .nav, .main-nav, header nav, #nav, #main-nav');
                
                if (mainNav) {
                    const links = mainNav.querySelectorAll('a');
                    for (const link of links) {
                        const href = link.getAttribute('href');
                        const text = link.textContent.trim();
                        
                        if (href && text && !href.startsWith('javascript:')) {
                            nav.push({
                                text: text,
                                url: new URL(href, window.location.origin).href
                            });
                        }
                    }
                }
                
                return nav;
            }"""
            )

            # Extract contact information
            self.logger.info("Extracting contact information")
            results["contact_info"] = await page.evaluate(
                """() => {
                const contactInfo = {
                    email: null,
                    phone: null,
                    address: null,
                    social_media: {}
                };
                
                // Extract email
                const emailRegex = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}/;
                const pageText = document.body.innerText;
                const emailMatch = pageText.match(emailRegex);
                if (emailMatch) {
                    contactInfo.email = emailMatch[0];
                }
                
                // Extract phone number
                const phoneRegex = /(?:(?:\\+|00)[1-9][0-9]{0,2}[\\s.-]?)?(?:(?:\\(\\d{1,4}\\)|\\d{1,4})[\\s.-]?)?\\d{3}[\\s.-]?\\d{3,4}[\\s.-]?\\d{0,4}/;
                const phoneMatch = pageText.match(phoneRegex);
                if (phoneMatch) {
                    contactInfo.phone = phoneMatch[0];
                }
                
                // Extract address from footer or contact section
                const footerOrContact = document.querySelector('footer, .footer, #footer, .contact, #contact');
                if (footerOrContact) {
                    const addressElements = footerOrContact.querySelectorAll('address, .address, [itemtype*="PostalAddress"]');
                    if (addressElements.length > 0) {
                        contactInfo.address = addressElements[0].textContent.trim();
                    }
                }
                
                // Extract social media links
                const socialPlatforms = {
                    'facebook.com': 'facebook',
                    'twitter.com': 'twitter',
                    'instagram.com': 'instagram',
                    'linkedin.com': 'linkedin',
                    'pinterest.com': 'pinterest',
                    'youtube.com': 'youtube',
                    'tiktok.com': 'tiktok'
                };
                
                const socialLinks = document.querySelectorAll('a[href*="facebook"], a[href*="twitter"], a[href*="instagram"], a[href*="linkedin"], a[href*="pinterest"], a[href*="youtube"], a[href*="tiktok"]');
                
                socialLinks.forEach(link => {
                    const href = link.href;
                    for (const [domain, platform] of Object.entries(socialPlatforms)) {
                        if (href.includes(domain)) {
                            contactInfo.social_media[platform] = href;
                            break;
                        }
                    }
                });
                
                return contactInfo;
            }"""
            )

            # Extract product information with enhanced metadata
            self.logger.info("Extracting products with metadata")

            # Define the enhanced product extraction script
            EXTRACT_PRODUCTS_WITH_METADATA_JS = """() => {
                // Common product container selectors
                const productSelectors = [
                    ".product",
                    ".product-card",
                    ".product-item",
                    ".product-container",
                    "[data-product-id]",
                    ".item-product",
                    "Product",
                    "[class*='ProductImage']", 
                    "[class*='product-image']",
                    "[class*='productImage']",
                    "[class*='imageContainer']"
                ];
                
                let productElements = [];
                
                // Try each selector until we find products
                for (const selector of productSelectors) {
                    const elements = document.querySelectorAll(selector);
                    if (elements.length > 0) {
                        productElements = Array.from(elements);
                        break;
                    }
                }
                
                // If no products found with common selectors, try to find by structure
                if (productElements.length === 0) {
                    // Look for elements with images and prices (common product structure)
                    const potentialProducts = document.querySelectorAll("*");
                    for (const el of potentialProducts) {
                        if (
                            el.querySelector("img") &&
                            (el.textContent.includes("$") ||
                            el.textContent.match(/\\d+\\.\\d{2}/) ||
                            el.querySelector(".price"))
                        ) {
                            productElements.push(el);
                        }
                    }
                }
                
                // Process products with enhanced metadata
                return productElements.slice(0, 20).map((productEl, index) => {
                    // Extract product images
                    const imgElements = productEl.querySelectorAll("img");
                    const images = Array.from(imgElements)
                        .map((img) => ({
                            url: img.src || img.getAttribute('data-src') || img.getAttribute('data-lazy-src'),
                            alt: img.alt || `Product image ${index}`,
                            width: img.width,
                            height: img.height,
                        }))
                        .filter(
                            (img) => img.url && !img.url.includes("placeholder") && img.width > 50
                        );
                    
                    // Extract product title
                    let title = "";
                    const titleSelectors = [
                        "h1", "h2", "h3", "h4", ".product-title", ".title", 
                        "[class*='product-name']", "[class*='productName']", "[class*='ProductTitle']",
                        "[itemprop='name']"
                    ];
                    
                    for (const selector of titleSelectors) {
                        const titleEl = productEl.querySelector(selector);
                        if (titleEl) {
                            title = titleEl.textContent.trim();
                            break;
                        }
                    }
                    
                    // Extract price
                    let price = "";
                    let salePrice = null;
                    let regularPrice = null;
                    
                    const priceSelectors = [
                        ".price", ".product-price", "[data-price]", 
                        "[class*='price']", "[class*='Price']",
                        "[itemprop='price']"
                    ];
                    
                    for (const selector of priceSelectors) {
                        const priceEl = productEl.querySelector(selector);
                        if (priceEl) {
                            price = priceEl.textContent.trim();
                            break;
                        }
                    }
                    
                    // Check for sale price
                    const salePriceEl = productEl.querySelector(".sale-price, .special-price, [class*='sale'], [class*='Sale']");
                    if (salePriceEl) {
                        salePrice = salePriceEl.textContent.trim();
                        
                        // Look for regular price when sale price exists
                        const regularPriceEl = productEl.querySelector(".regular-price, .original-price, .old-price, [class*='regular'], [class*='original']");
                        if (regularPriceEl) {
                            regularPrice = regularPriceEl.textContent.trim();
                        }
                    }
                    
                    // Extract product description
                    let description = "";
                    const descSelectors = [
                        ".description", ".product-description", "[itemprop='description']",
                        "[class*='description']", "[class*='Description']"
                    ];
                    
                    for (const selector of descSelectors) {
                        const descEl = productEl.querySelector(selector);
                        if (descEl) {
                            description = descEl.textContent.trim();
                            break;
                        }
                    }
                    
                    // Extract product category
                    let category = "";
                    const breadcrumbEl = document.querySelector(".breadcrumb, .breadcrumbs, [class*='breadcrumb']");
                    if (breadcrumbEl) {
                        const breadcrumbLinks = breadcrumbEl.querySelectorAll("a");
                        if (breadcrumbLinks.length > 1) {
                            category = breadcrumbLinks[breadcrumbLinks.length - 2].textContent.trim();
                        }
                    }
                    
                    // Extract SKU / Product ID
                    let sku = productEl.dataset.productId || productEl.dataset.sku || "";
                    if (!sku) {
                        const skuEl = productEl.querySelector("[itemprop='sku'], .sku, [class*='sku'], [class*='SKU']");
                        if (skuEl) {
                            sku = skuEl.textContent.trim();
                        }
                    }
                    
                    // Extract availability
                    let availability = "unknown";
                    const availabilityEl = productEl.querySelector("[itemprop='availability'], .availability, .stock, [class*='stock'], [class*='Stock']");
                    if (availabilityEl) {
                        const availText = availabilityEl.textContent.toLowerCase();
                        if (availText.includes("in stock") || availText.includes("available")) {
                            availability = "in_stock";
                        } else if (availText.includes("out of stock") || availText.includes("sold out")) {
                            availability = "out_of_stock";
                        } else if (availText.includes("preorder") || availText.includes("pre-order")) {
                            availability = "preorder";
                        }
                    }
                    
                    // Extract product variants if available
                    const variants = [];
                    const variantSelectors = ["select.variant, select[name*='variant'], select.option, select[name*='option']"];
                    for (const selector of variantSelectors) {
                        const variantEl = productEl.querySelector(selector);
                        if (variantEl) {
                            const options = variantEl.querySelectorAll("option");
                            options.forEach(option => {
                                if (option.value && option.value !== "choose" && option.textContent.trim() !== "Select") {
                                    variants.push({
                                        name: variantEl.name || "variant",
                                        value: option.textContent.trim(),
                                        id: option.value
                                    });
                                }
                            });
                        }
                    }
                    
                    // Check for color/size swatches
                    const swatchContainers = productEl.querySelectorAll(".swatch, .color-swatch, .size-swatch, [class*='swatch'], [class*='Swatch']");
                    swatchContainers.forEach(container => {
                        const swatchType = container.className.toLowerCase().includes('color') ? 'color' : 'size';
                        const swatches = container.querySelectorAll("a, button, [role='button'], input[type='radio']");
                        
                        swatches.forEach(swatch => {
                            variants.push({
                                name: swatchType,
                                value: swatch.textContent.trim() || swatch.title || swatch.value || swatch.dataset.value || "",
                                id: swatch.value || swatch.dataset.value || ""
                            });
                        });
                    });
                    
                    // Extract product URL
                    let url = productEl.querySelector("a")?.href || null;
                    if (!url && productEl.tagName === "A") {
                        url = productEl.href;
                    }
                    
                    return {
                        id: sku || productEl.dataset.productId || `product-${index}`,
                        title: title || "Unknown Product",
                        price: price || "N/A",
                        sale_price: salePrice,
                        regular_price: regularPrice,
                        description: description,
                        category: category,
                        availability: availability,
                        variants: variants.length > 0 ? variants : null,
                        images: images.map(img => img.url),
                        url: url ? new URL(url, window.location.origin).href : null,
                    };
                });
            }"""

            # Extract products with enhanced metadata
            results["products"] = await page.evaluate(EXTRACT_PRODUCTS_WITH_METADATA_JS)

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
