import io
import random
from typing import List
from PIL import Image, ImageEnhance, ImageFilter


class BannerVariantService:
    def __init__(self):
        self.style_variations = {"subtle", "vibrant", "muted"}
        self.variation_dict = {
            "subtle": {
                "brightness": 1,
                "contrast": 1.1,
                "saturation": 1.05,
                "sharpness": 1.1,
                "smoothness": 0,
            },
            "vibrant": {
                "brightness": 1.1,
                "contrast": 1.2,
                "saturation": 1.3,
                "sharpness": 1.2,
                "smoothness": 0,
            },
            "muted": {
                "brightness": 0.95,
                "contrast": 0.9,
                "saturation": 0.8,
                "sharpness": 0,
                "smoothness": 0.5,
            },
        }
        self.layout_variations = {}

    def generate_variants(self, base_img: bytes, num_variant: int = 3) -> List[bytes]:
        base_pil = Image.open(io.BytesIO(base_img))

        variants = []

        variants.append(base_img)

        for _ in range(num_variant - 1):
            style = random.choice(self.style_variations)
            seed = random.random()

            enhanced = self._enhance_img(base_pil, style, seed)

            buffer = io.BytesIO()
            enhanced.save(buffer, format="PNG")
            variants.append(buffer.getvalue())
        return variants

    def _enhance_img(self, base_pil: Image.Image, style, seed):
        """enhance image while preserving original content"""

        params = self._get_style_params(style)
        enhanced = base_pil.copy()

        enhanced = ImageEnhance.Brightness(enhanced).enhance(params["brightness"])
        enhanced = ImageEnhance.Contrast(enhanced).enhance(params["contrast"])
        enhanced = ImageEnhance.Color(enhanced).enhance(params["saturation"])

        if params["sharpness"] > 0:
            enhanced = ImageEnhance.Sharpness(enhanced).enhance(params["sharpness"])

        if params["smoothness"] > 0:
            enhanced = enhanced.filter(ImageFilter.GaussianBlur(params["smoothness"]))

        return enhanced

    def _get_style_params(self, style):
        """returns random variant style"""

        def_style = self.variation_dict["subtle"]
        return self.variation_dict.get(style, def_style)
