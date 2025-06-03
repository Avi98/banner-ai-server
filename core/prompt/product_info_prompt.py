from core.agent.types import ProductIndustryEnum, ProductTemplateEnum


prompt = """You are an eCommerce data extraction assistant. Your task is to extract structured product data from a product screenshot.
Return the result in JSON format. Extract the following fields:

- product_name
- sale_price price after the offer
- regular_price price without offer
- offer 
- currency like INR for "₹", USD for "$" etc
- category (must be one of: {categories})
- description Empty string if not found
- product_features (all features list in bullet point). Empty if not found
- template_type (must be one of: {template_types})
- ratings average rating of product
- stock (number of items left, out_of_stock if items is out of stock, no_inventory_found false if not inventory details is found )

Ensure accurate mapping based on visual layout and text. Only return a valid JSON object."""


def get_product_prompt():
    from langchain_core.prompts import PromptTemplate

    categories_list = [
        ProductIndustryEnum.BEAUTY_AND_COSMETICS,
        ProductIndustryEnum.ELECTRONICS,
        ProductIndustryEnum.FASHION,
        ProductIndustryEnum.FOOD_AND_BEVERAGE,
        ProductIndustryEnum.STATIONARY,
        ProductIndustryEnum.HOME_DECOR,
    ]

    template_list = [
        ProductTemplateEnum.BOLD,
        ProductTemplateEnum.CLASSIC,
        ProductTemplateEnum.ELEGANT,
        ProductTemplateEnum.MINIMALIST,
        ProductTemplateEnum.MODERN,
    ]

    categories_str = "".join([f'"{c}"' for c in categories_list])
    template_str = "".join([f'"{c}"' for c in template_list])

    template = PromptTemplate.from_template(prompt)

    return template.invoke(
        {"categories": categories_str, "template_types": template_str}
    )
