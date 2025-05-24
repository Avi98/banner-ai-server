from calendar import c
from langchain_core.prompts import ChatPromptTemplate

copy_text_prompt = """
    You are a copywriter. 
    You will be given product information and you need to generate a marketing prompt that will be used for generating a banner image.
    The prompt should include the following product information: {product_description}.
    Make it visually descriptive, appealing, and suitable for a banner.
"""

product_prompt = """
    Generate product industry (i.e. fashion, electronics, home_decor, stationary, beauty and cosmetics, food and beverage)
    and product template (i.e. modern, minimalist, elegant, bold):

    Product Description: {product_description}
    Product Price: {product_price}
    Product Images: {product_imgs}

    Respond in JSON format with the following fields:
    product_industry, product_template
"""

product_metadata_template = ChatPromptTemplate.from_messages(
    [("system", copy_text_prompt), ("system", product_prompt)]
)
