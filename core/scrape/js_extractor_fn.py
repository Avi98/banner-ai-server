# js_extractors.py

# Function to extract font information
EXTRACT_FONTS_JS = """() => {
    const fontInfo = {};
    
    // Get font from computed styles of common elements
    const elements = {
        'headings': ['h1', 'h2', 'h3'],
        'body': ['p', '.product-description', '.product-details'],
        'buttons': ['button', '.btn', '.button'],
        'prices': ['.price', '.product-price', '.amount']
    };
    
    for (const [key, selectors] of Object.entries(elements)) {
        for (const selector of selectors) {
            const element = document.querySelector(selector);
            if (element) {
                const style = window.getComputedStyle(element);
                fontInfo[key] = {
                    family: style.fontFamily,
                    size: style.fontSize,
                    weight: style.fontWeight,
                    color: style.color
                };
                break;
            }
        }
    }
    
    // Extract all font-family rules from stylesheets
    const allFonts = new Set();
    try {
        for (const sheet of document.styleSheets) {
            try {
                const rules = sheet.cssRules || sheet.rules;
                for (const rule of rules) {
                    if (rule.style && rule.style.fontFamily) {
                        allFonts.add(rule.style.fontFamily);
                    }
                }
            } catch (e) {
                // CORS issues with external stylesheets
                continue;
            }
        }
    } catch (e) {
        console.error("Error extracting fonts from stylesheets:", e);
    }
    
    fontInfo['all_detected_fonts'] = Array.from(allFonts);
    return fontInfo;
}"""

# Function to extract theme colors and styling information
EXTRACT_THEME_JS = """() => {
    const themeInfo = {
        colors: {},
        background: {},
        layout: {}
    };
    
    // Extract background color of main elements
    const bgElements = ['body', 'header', 'footer', '.main-content', '.product-container'];
    for (const selector of bgElements) {
        const element = document.querySelector(selector);
        if (element) {
            const style = window.getComputedStyle(element);
            themeInfo.background[selector] = {
                backgroundColor: style.backgroundColor,
                backgroundImage: style.backgroundImage
            };
        }
    }
    
    // Extract primary colors from buttons, links, headers
    const colorElements = {
        'primary': ['a', '.btn-primary', '.primary-button'],
        'secondary': ['.btn-secondary', '.secondary-button'],
        'accent': ['.accent', '.highlight', '.featured'],
        'text': ['body', 'p', '.description']
    };
    
    for (const [key, selectors] of Object.entries(colorElements)) {
        for (const selector of selectors) {
            const element = document.querySelector(selector);
            if (element) {
                const style = window.getComputedStyle(element);
                themeInfo.colors[key] = {
                    color: style.color,
                    backgroundColor: style.backgroundColor
                };
                break;
            }
        }
    }
    
    // Extract layout information
    const layout = document.querySelector('.main-content, #main, main');
    if (layout) {
        const style = window.getComputedStyle(layout);
        themeInfo.layout = {
            maxWidth: style.maxWidth,
            padding: style.padding,
            margin: style.margin
        };
    }
    
    return themeInfo;
}"""

# Function to extract store logo information
EXTRACT_LOGO_JS = """() => {
    // Common logo selectors
    const logoSelectors = [
        'header img', 
        '.logo img', 
        '#logo img',
        '.site-logo img',
        '.header-logo img',
        '.navbar-brand img',
        '[aria-label="logo"] img',
        '.logo a img'
    ];
    
    for (const selector of logoSelectors) {
        const logoEl = document.querySelector(selector);
        if (logoEl && logoEl.src) {
            return {
                url: logoEl.src,
                alt: logoEl.alt || 'Store logo',
                width: logoEl.width,
                height: logoEl.height
            };
        }
    }
    
    // Try to find SVG logos
    const svgLogo = document.querySelector('.logo svg, #logo svg, header svg');
    if (svgLogo) {
        return {
            type: 'svg',
            outerHTML: svgLogo.outerHTML,
            width: svgLogo.width?.baseVal?.value,
            height: svgLogo.height?.baseVal?.value
        };
    }
    
    return null;
}"""

# Function to extract product information including images
EXTRACT_PRODUCTS_JS = """() => {
  // Common product container selectors with support for dynamic class names
  const productSelectors = [
    ".product",
    ".product-card",
    ".product-item",
    ".product-container",
    "[data-product-id]",
    ".item-product",
    "Product",
    "[class*='ProductImage']", // Match any class containing 'ProductImage'
    "[class*='product-image']",
    "[class*='productImage']",
    "[class*='imageContainer']", // Match any class containing 'imageContainer'
    "[class*='image-container']"
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
  
  // Find all product image containers with regex pattern matching
  if (productElements.length === 0) {
    const allElements = document.querySelectorAll('*');
    for (const el of allElements) {
      if (el.className && typeof el.className === 'string') {
        if (
          el.className.match(/product.*image/i) || 
          el.className.match(/image.*container/i) || 
          el.className.match(/product.*container/i)
        ) {
          productElements.push(el);
        }
      }
    }
  }
  
  // Find all images with product-related alt text
  function getImagesByAltPattern() {
    const allImages = document.getElementsByTagName("img");
    const images = [];
    const productRelatedTerms = ['product', 'item', 'merchandise', 'goods'];
    
    for (let i = 0; i < allImages.length; i++) {
      const img = allImages[i];
      const alt = (img.alt || '').toLowerCase();
      
      // Check if alt text contains any product-related terms
      if (productRelatedTerms.some(term => alt.includes(term))) {
        images.push(img);
      }
      // Also include images that are likely product images based on path
      else if (
        img.src && 
        (img.src.includes('/product') || 
         img.src.includes('/products') || 
         img.src.includes('/images/product'))
      ) {
        images.push(img);
      }
    }
    return images;
  }
  
  const altImages = getImagesByAltPattern();
  if (altImages.length > 0) {
    altImages.forEach(img => {
      if (img.currentSrc && !productElements.includes(img)) {
        productElements.push(img);
      }
    });
  }
  
  // If productElements already contains product images
  if (
    productElements.length !== 0 &&
    productElements.every(el => el.tagName === "IMG")
  ) {
    const images = Array.from(productElements);
    const validImages = images
      .map((img, index) => ({
        url: img.src || img.currentSrc,
        alt: img.alt || `Product image ${index}`,
        width: img.width,
        height: img.height,
      }))
      .filter(
        img => img.url && !img.url.includes("placeholder") && img.width > 50
      );
    
    return {
      id: `product-dynamic`,
      title: "Product Title",
      price: "2000",
      images: validImages.map(img => img.url),
    };
  }
  
  // For container elements, find nested images
  const processedProducts = [];
  for (const productEl of productElements) {
    // Try to find all images within this container
    const imgElements = productEl.querySelectorAll("img");
    
    // If no direct images, look for picture elements or background images
    if (imgElements.length === 0) {
      // Check for picture elements
      const pictureElements = productEl.querySelectorAll("picture source");
      if (pictureElements.length > 0) {
        Array.from(pictureElements).forEach((source, index) => {
          processedProducts.push({
            id: productEl.dataset?.productId || `product-${processedProducts.length}`,
            title: "Product Title",
            price: "N/A",
            images: [source.srcset.split(' ')[0]],
            url: null
          });
        });
        continue;
      }
      
      // Check for elements with background image
      const allNestedElements = productEl.querySelectorAll("*");
      const elementsWithBgImage = Array.from(allNestedElements).filter(el => {
        const style = window.getComputedStyle(el);
        return style.backgroundImage && style.backgroundImage !== 'none';
      });
      
      if (elementsWithBgImage.length > 0) {
        const bgImages = elementsWithBgImage.map(el => {
          const bgImage = window.getComputedStyle(el).backgroundImage;
          return bgImage.replace(/url\(['"]?(.*?)['"]?\)/i, '$1');
        }).filter(url => url && !url.includes('placeholder'));
        
        if (bgImages.length > 0) {
          processedProducts.push({
            id: productEl.dataset?.productId || `product-${processedProducts.length}`,
            title: "Product Title",
            price: "N/A",
            images: bgImages,
            url: null
          });
        }
        continue;
      }
    }
    
    const images = Array.from(imgElements)
      .map((img, idx) => ({
        url: img.src || img.currentSrc,
        alt: img.alt || `Product image ${idx}`,
        width: img.width,
        height: img.height,
      }))
      .filter(
        img => img.url && !img.url.includes("placeholder") && img.width > 50
      );
    
    // Extract product title
    let title = "";
    const titleSelectors = [
      "h2", "h3", "h4", ".product-title", ".title", 
      "[class*='product-name']", "[class*='productName']", "[class*='ProductTitle']"
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
    const priceSelectors = [
      ".price", ".product-price", "[data-price]", 
      "[class*='price']", "[class*='Price']"
    ];
    
    for (const selector of priceSelectors) {
      const priceEl = productEl.querySelector(selector);
      if (priceEl) {
        price = priceEl.textContent.trim();
        break;
      }
    }
    
    if (!price) {
      // Try to find price in text
      const text = productEl.textContent;
      const priceMatch = text.match(/\$\s?\d+(\.\d{2})?/);
      if (priceMatch) {
        price = priceMatch[0];
      }
    }
    
    processedProducts.push({
      id: productEl.dataset?.productId || `product-${processedProducts.length}`,
      title: title || "Product Title",
      price: price || "N/A",
      images: images.map(img => img.url),
      url: productEl.querySelector("a")?.href || null,
    });
  }
  
  // If we couldn't find any products, try a last-resort approach
  if (processedProducts.length === 0) {
    // Look for all images of sufficient size that might be product images
    const allImages = document.querySelectorAll('img');
    const potentialProductImages = Array.from(allImages)
      .filter(img => {
        const src = img.src || img.currentSrc;
        return (
          src && 
          !src.includes('placeholder') && 
          !src.includes('logo') &&
          !src.includes('icon') &&
          img.width > 100 && 
          img.height > 100
        );
      });
    
    if (potentialProductImages.length > 0) {
      potentialProductImages.forEach((img, index) => {
        processedProducts.push({
          id: `product-${index}`,
          title: img.alt || "Product Title",
          price: "N/A",
          images: [img.src || img.currentSrc],
          url: null
        });
      });
    }
  }
  
  return processedProducts.slice(0, 20);
}"""

# Function to extract inventory information
EXTRACT_INVENTORY_JS = """() => {
    const inventoryInfo = {};
    
    // Common inventory indicators
    const inventorySelectors = [
        '.stock', 
        '.inventory', 
        '.availability',
        '.quantity',
        '[data-stock]',
        '.in-stock',
        '.out-of-stock'
    ];
    
    // Try each selector
    for (const selector of inventorySelectors) {
        const elements = document.querySelectorAll(selector);
        if (elements.length > 0) {
            Array.from(elements).forEach((el, index) => {
                // Extract product ID if available
                let productId = el.closest('[data-product-id]')?.dataset.productId;
                if (!productId) {
                    productId = `product-${index}`;
                }
                
                // Extract inventory text
                const inventoryText = el.textContent.trim();
                
                // Try to find if it contains quantity information
                const quantityMatch = inventoryText.match(/(\\d+)\\s*(left|remaining|in stock)/i);
                if (quantityMatch) {
                    inventoryInfo[productId] = {
                        quantity: parseInt(quantityMatch[1]),
                        text: inventoryText,
                        status: 'in_stock'
                    };
                } else if (
                    inventoryText.match(/out of stock|sold out/i)
                ) {
                    inventoryInfo[productId] = {
                        quantity: 0,
                        text: inventoryText,
                        status: 'out_of_stock'
                    };
                } else if (
                    inventoryText.match(/in stock|available/i)
                ) {
                    inventoryInfo[productId] = {
                        quantity: null,  // Unknown quantity
                        text: inventoryText,
                        status: 'in_stock'
                    };
                } else {
                    inventoryInfo[productId] = {
                        text: inventoryText,
                        status: 'unknown'
                    };
                }
            });
            break;
        }
    }
    
    return inventoryInfo;
}"""

# Function to extract contact information
EXTRACT_CONTACT_INFO_JS = """() => {
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

# Function to extract metadata
EXTRACT_METADATA_JS = """() => {
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

# Function to extract navigation structure
EXTRACT_NAVIGATION_JS = """() => {
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

# Function to extract categories
EXTRACT_CATEGORIES_JS = """() => {
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
    
    return categories;
}"""

# Function to extract metadata
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

# Function to extract currency
EXTRACT_CURRENCY_JS = """() => {
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
