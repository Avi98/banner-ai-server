() => {
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
    "[class*='imageContainer']",
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
      const priceEl =
        el.textContent.includes("$") ||
        el.textContent.includes("€") ||
        el.textContent.includes("₹");

      if (
        el.querySelector("img") &&
        (el.textContent.match(/\\d+\\.\\d{2}/) ||
          priceEl ||
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
        url:
          img.src ||
          img.getAttribute("data-src") ||
          img.getAttribute("data-lazy-src"),
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
      "h1",
      "h2",
      "h3",
      "h4",
      ".product-title",
      ".title",
      "[class*='product-name']",
      "[class*='productName']",
      "[class*='ProductTitle']",
      "[itemprop='name']",
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
      ".price",
      ".product-price",
      "[data-price]",
      "[class*='price']",
      "[class*='Price']",
      "[itemprop='price']",
    ];

    for (const selector of priceSelectors) {
      const priceEl = productEl.querySelector(selector);
      if (priceEl) {
        price = priceEl.textContent.trim();
        break;
      }
    }

    if (!price) {
      const potentialProducts = productEl.querySelectorAll("*");
      for (const el of potentialProducts) {
        const priceEl =
          el.textContent.includes("$") ||
          el.textContent.includes("€") ||
          el.textContent.includes("₹");

        if (priceEl) {
          // Extract the element text content
          const textContent = el.textContent.trim();

          // Only add non-empty and reasonable length texts
          if (textContent && textContent.length < 200) {
            price = textContent;
          }
        }
      }
    }

    // Check for sale price
    const salePriceEl = productEl.querySelector(
      ".sale-price, .special-price, [class*='sale'], [class*='Sale']"
    );
    if (salePriceEl) {
      salePrice = salePriceEl.textContent.trim();

      // Look for regular price when sale price exists
      const regularPriceEl = productEl.querySelector(
        ".regular-price, .original-price, .old-price, [class*='regular'], [class*='original']"
      );
      if (regularPriceEl) {
        regularPrice = regularPriceEl.textContent.trim();
      }
    }

    // Extract product description
    let description = "";
    const descSelectors = [
      ".description",
      ".product-description",
      "[itemprop='description']",
      "[class*='description']",
      "[class*='Description']",
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
    const breadcrumbEl = document.querySelector(
      ".breadcrumb, .breadcrumbs, [class*='breadcrumb']"
    );
    if (breadcrumbEl) {
      const breadcrumbLinks = breadcrumbEl.querySelectorAll("a");
      if (breadcrumbLinks.length > 1) {
        category =
          breadcrumbLinks[breadcrumbLinks.length - 2].textContent.trim();
      }
    }

    // Extract SKU / Product ID
    let sku = productEl.dataset.productId || productEl.dataset.sku || "";
    if (!sku) {
      const skuEl = productEl.querySelector(
        "[itemprop='sku'], .sku, [class*='sku'], [class*='SKU']"
      );
      if (skuEl) {
        sku = skuEl.textContent.trim();
      }
    }

    // Extract availability
    let availability = "unknown";
    const availabilityEl = productEl.querySelector(
      "[itemprop='availability'], .availability, .stock, [class*='stock'], [class*='Stock']"
    );
    if (availabilityEl) {
      const availText = availabilityEl.textContent.toLowerCase();
      if (availText.includes("in stock") || availText.includes("available")) {
        availability = "in_stock";
      } else if (
        availText.includes("out of stock") ||
        availText.includes("sold out")
      ) {
        availability = "out_of_stock";
      } else if (
        availText.includes("preorder") ||
        availText.includes("pre-order")
      ) {
        availability = "preorder";
      }
    }

    // Extract product variants if available
    const variants = [];
    const variantSelectors = [
      "select.variant, select[name*='variant'], select.option, select[name*='option']",
    ];
    for (const selector of variantSelectors) {
      const variantEl = productEl.querySelector(selector);
      if (variantEl) {
        const options = variantEl.querySelectorAll("option");
        options.forEach((option) => {
          if (
            option.value &&
            option.value !== "choose" &&
            option.textContent.trim() !== "Select"
          ) {
            variants.push({
              name: variantEl.name || "variant",
              value: option.textContent.trim(),
              id: option.value,
            });
          }
        });
      }
    }

    // Check for color/size swatches
    const swatchContainers = productEl.querySelectorAll(
      ".swatch, .color-swatch, .size-swatch, [class*='swatch'], [class*='Swatch']"
    );
    swatchContainers.forEach((container) => {
      const swatchType = container.className.toLowerCase().includes("color")
        ? "color"
        : "size";
      const swatches = container.querySelectorAll(
        "a, button, [role='button'], input[type='radio']"
      );

      swatches.forEach((swatch) => {
        variants.push({
          name: swatchType,
          value:
            swatch.textContent.trim() ||
            swatch.title ||
            swatch.value ||
            swatch.dataset.value ||
            "",
          id: swatch.value || swatch.dataset.value || "",
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
      images: images.map((img) => img.url),
      url: url ? new URL(url, window.location.origin).href : null,
    };
  });
}