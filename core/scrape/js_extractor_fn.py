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
