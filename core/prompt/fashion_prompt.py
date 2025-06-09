from langchain_core.prompts import PromptTemplate

from global_type.product_base import Platform


def get_fashion_banner(
    platform: Platform,
    bg_color: str,
    prod_color: str,
    product: str,
    product_category: str,
    ratings_cpy: str,
    offer_cpy: str,
    theme: str,
):
    prompt = """Design a modern and bold eCommerce banner for a limited-time fashion product campaign.

**Platform:** {platform} Ads
**Image Size:** 1200x628 pixels (under 8MB)

### Style & Background:
- Use a two-tone background with a {bg_color} left panel and a {right_panel_color} right panel.
- Incorporate smooth gradients, diagonal arrows, and geometric accents for visual movement.
- Keep the layout sleek, energetic, and eye-catching with contrast between product and text zones.

### Product Layout:
- Feature a single {product_color} {product} (image 1) on the right side.
- The {product_category} should appear floating with realistic shadows and angled for a dynamic look.
- Add a label or tag below the {product_category} that says “Reasonable Price” with a small icon.

### Text Content (on the left side):
- Top Tagline: "New {product_category}"
- Highlighted Main Title:
- "Collection" (in large white bold text)
- "Offer for a limited time only" (subheading in all caps)

- Review Bar: "{ratings_cpy}"
- Discount Message: "{offer_copy}" (in a {offer_copy} circular badge near the product)

### Branding:
- Leave space for company logo at the top-left corner.
- No website or brand name required unless space allows in the footer.

Ensure the banner is sharp, exciting,Design a modern eCommerce promotional banner in a horizontal layout.

	- Product featured: {product}
	- Dominant theme color: {theme_color}
	- Style: Bold, sleek, product-focused with high contrast and clean design
	- Include text: "{offer_copy}"
	- Include a button with "Shop Now"
	- Include a rating section (e.g., stars and review count)
	- Tagline section for "Reasonable Price"
	- Visual: Show the product prominently with shadows or depth
	- Background should have gradient or dynamic shapes to enhance energy
	- Typography should be clear and stylish — emphasis on words like "Collection" or "New"
	- Placement: Product should float or pop out on one side, with text and CTA on the other
	- Add discount badge like "Up to 70% Off"
	- Leave space for company logo at the top left
	- Overall tone: eye-catching, professional, and conversion-optimized

	Do not include any brand names or copyrighted logos. and visually balanced for high-converting {platform} ad campaigns.

"""
    prompt_template = PromptTemplate.from_template(prompt)
    variables = {
        "platform": platform,
        "bg_color": bg_color,
        "product_color": prod_color,
        "product": product,
        "product_category": product_category,
        "ratings_cpy": ratings_cpy,
        "offer_copy": offer_cpy,
        "theme_color": theme,
    }
    return prompt_template.invoke(variables).to_string()
