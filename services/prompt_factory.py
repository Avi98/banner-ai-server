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
            "platform": self.product_info.get("platforms"),
            "tagline": self.product_info.get("name"),
            "main_title_emphasis": self.product_info.get("name"),
            "sales_dates": self.product_info.get("product_sales", "not found"),
            "discount_text": self.product_info.get("offer", "None"),
        }
        return electronics_prompts(**prompt_args)


class FashionPromptGenerator(PromptGenerator):
    def generate_prompt(self) -> str:
        prompt_args = {
            "platform": self.product_info.get("platform"),
            "bg_color": self.product_info.get("bg_color"),
            "prod_color": self.product_info.get("prod_color"),
            "product": self.product_info.get("product"),
            "product_category": self.product_info.get("product_category"),
            "ratings_cpy": self.product_info.get("ratings_cpy"),
            "offer_cpy": self.product_info.get("offer_cpy"),
            "theme": self.product_info.get("theme"),
        }
        return get_fashion_banner(**prompt_args)


class BeautyAndCosmeticsPromptGenerator(PromptGenerator):
    def generate_prompt(self) -> str:
        # TODO: Implement beauty and cosmetics prompt generator
        pass


class FoodAndBeveragePromptGenerator(PromptGenerator):
    def generate_prompt(self) -> str:
        # TODO: Implement food and beverage prompt generator
        pass


class HomeDecorPromptGenerator(PromptGenerator):
    def generate_prompt(self) -> str:
        # TODO: Implement home decor prompt generator
        pass


class StationaryPromptGenerator(PromptGenerator):
    def generate_prompt(self) -> str:
        # TODO: Implement stationary prompt generator
        pass


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
        # generator_class = self._generators.get(ind_type.model_dump().get("category"))
        category_enum = ProductIndustryEnum[ind_type.get("category")]
        generator_class = self._generators.get(category_enum)

        if not generator_class:
            raise ValueError(f"No prompt generator found for industry type: {ind_type}")

        generator = generator_class(self.product_info)
        return generator.generate_prompt()
