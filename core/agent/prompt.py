from calendar import c
from langchain_core.prompts import PromptTemplate

copy_text_prompt = PromptTemplate.from_template(
    "You are a copywriter. You will be given product information and you need to generate a marketing prompt that will be used for generating a banner image.The prompt should include the following product information: {productInfo}.Make it visually descriptive, appealing, and suitable for a banner."
)
