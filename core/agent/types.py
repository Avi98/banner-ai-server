from pydantic import BaseModel, ConfigDict, Field

from global_type.product_base import (
    ProductBase,
    ProductIndustryEnum,
    ProductTemplateEnum,
)


class ProductAgentResponseType(ProductBase):
    pass
