from langchain_openai import ChatOpenAI
from core.agent.types import ProductInfoOutput, ProductMetadata
from core.prompt.banner_prompt import product_metadata_template


def generate_prompt_name(model: ChatOpenAI, prompt: str):
    """Generate marketing prompt that needs to be feed to generating banner image"""
    return model.invoke(prompt)


def generate_product_info(
    model: ChatOpenAI, product_info: ProductMetadata
) -> ProductInfoOutput:
    """Generate product information based on the provided metadata."""

    prompt = product_metadata_template.format(
        product_description=product_info.get("product_description"),
        product_price=product_info.get("product_price"),
        product_imgs=product_info.get("product_imgs"),
    )
    structured_chain = model.with_structured_output(
        ProductInfoOutput, method="json_schema"
    )
    response = structured_chain.invoke(prompt)

    return response
