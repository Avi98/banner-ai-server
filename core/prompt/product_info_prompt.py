from global_type.product_base import ProductIndustryEnum, ProductTemplateEnum


prompt = """You are an eCommerce data extraction assistant. Your task is to extract structured product data from a product screenshot.
Return the result in JSON format. Extract the following fields:

- name short clear name for the product that should not be more than 3 words
- sale_price price after the offer
- regular_price price without offer
- offer 
- currency like INR for "₹", USD for "$" etc
- category (must be one of: {categories})
- description Empty string if not found
- template_type (must be one of: {template_types})
- ratings average rating of product
- stock (number of items left, out_of_stock if items is out of stock, no_inventory_found false if not inventory details is found )


**Video Ad Metadata Fields:**

- platform  like Facebook, Instagram, Whatsapp
- feature_1  - product_features (all features list in bullet point). Empty if not found
- feature_2  - product_features (all features list in bullet point). Empty if not found 
- feature_3  - product_features (all features list in bullet point). Empty if not found
- feature_4  - product_features (all features list in bullet point). Empty if not found
- feature_5  - product_features (all features list in bullet point). Empty if not found
- color_palette  - color palette based on the theme and color of the product
- style         
- lighting  
- ambiance  
- cta_text  
- aspect_ratio defaults to 9:16 
- duration  max 8 sec

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
