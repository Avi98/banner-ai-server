from abc import ABC, abstractmethod
from typing import Any
from core.agent.types import ProductBase, ProductIndustryEnum
from core.prompt.fashion_prompt import get_fashion_banner
from core.prompt.banner_image_prompt import electronics_prompts


class PromptGenerator(ABC):
    def __init__(self, product_info: ProductBase):
        self.product_info = product_info

    @abstractmethod
    def generate_prompt(self) -> str:
        pass


class ElectronicsPromptGenerator(PromptGenerator):
    def generate_prompt(self) -> str:
        prompt_args = {
            "platform": self.product_info.platform,
            "tagline": self.product_info.name,
            "main_title_emphasis": self.product_info.name,
            "sales_dates": None,  # product_sales does not exist
            "discount_text": self.product_info.offer,
        }
        return electronics_prompts(**prompt_args)


class FashionPromptGenerator(PromptGenerator):
    def generate_prompt(self) -> str:
        prompt_args = {
            "platform": self.product_info.platform,
            "bg_color": None,  # bg_color does not exist
            "prod_color": None,  # prod_color does not exist
            "product": self.product_info.name,
            "product_category": self.product_info.category,
            "ratings_cpy": self.product_info.ratings,
            "offer_cpy": self.product_info.offer,
            "theme": self.product_info.template_type,
        }
        return get_fashion_banner(**prompt_args)


class BeautyAndCosmeticsPromptGenerator(PromptGenerator):
    def generate_prompt(self) -> str:
        raise NotImplementedError("Beauty and cosmetics prompt generator is not implemented")


class FoodAndBeveragePromptGenerator(PromptGenerator):
    def generate_prompt(self) -> str:
        raise NotImplementedError("Food and beverage prompt generator is not implemented")


class HomeDecorPromptGenerator(PromptGenerator):
    def generate_prompt(self) -> str:
        raise NotImplementedError("Home decor prompt generator is not implemented")


class StationaryPromptGenerator(PromptGenerator):
    def generate_prompt(self) -> str:
        raise NotImplementedError("Stationary prompt generator is not implemented")


class IndustryPromptFactory:
    def __init__(self, product_info: ProductBase):
        self.product_info = product_info
        self._generators = {
            ProductIndustryEnum.ELECTRONICS: ElectronicsPromptGenerator,
            ProductIndustryEnum.FASHION: FashionPromptGenerator,
            ProductIndustryEnum.BEAUTY_AND_COSMETICS: BeautyAndCosmeticsPromptGenerator,
            ProductIndustryEnum.FOOD_AND_BEVERAGE: FoodAndBeveragePromptGenerator,
            ProductIndustryEnum.HOME_DECOR: HomeDecorPromptGenerator,
            ProductIndustryEnum.STATIONARY: StationaryPromptGenerator,
        }

    @staticmethod
    def validate_product_info(product_info: dict[str, Any]) -> ProductBase:
        return ProductBase.model_validate(obj=product_info, strict=False)

    def get_prompt(self, ind_type: ProductBase) -> str:
        """Get prompt for the given industry type using appropriate prompt generator"""
        category_enum = ProductIndustryEnum[ind_type.category]
        generator_class = self._generators.get(category_enum)

        if not generator_class:
            raise ValueError(f"No prompt generator found for industry type: {ind_type}")

        generator = generator_class(self.product_info)
        return generator.generate_prompt()