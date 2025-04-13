from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
from typing import Any, Dict, List, Optional, Mapping, Union, Tuple
import json
import requests
import io
import os
import base64
import re
import tempfile
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from pydantic import BaseModel, Field, root_validator


class BannerGenerationLLM(LLM):
    """
    Enhanced custom LLM that generates sales banners incorporating logos,
    product images, and theme colors from the provided data.
    """

    endpoint_url: str = Field(
        description="URL of the text-to-image diffusion model API"
    )
    api_key: str = Field(description="API key for the text-to-image model")
    output_dir: str = Field(
        default="generated_banners", description="Directory to save generated banners"
    )

    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True

    @property
    def _llm_type(self) -> str:
        return "banner-generation-llm"

    def _create_directory(self) -> None:
        """Create output directory if it doesn't exist."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def _get_social_media_sizes(self) -> Dict[str, Dict[str, Any]]:
        """Define common social media banner sizes with templates."""
        return {
            "facebook_post": {
                "size": (1200, 630),
                "logo_position": (50, 50),
                "logo_size": (150, 150),
                "product_position": (700, 200),
                "product_size": (400, 400),
                "text_position": (50, 400),
            },
            "instagram_post": {
                "size": (1080, 1080),
                "logo_position": (50, 50),
                "logo_size": (150, 150),
                "product_position": (650, 400),
                "product_size": (400, 400),
                "text_position": (50, 700),
            },
            "twitter_post": {
                "size": (1200, 675),
                "logo_position": (50, 50),
                "logo_size": (120, 120),
                "product_position": (800, 200),
                "product_size": (350, 350),
                "text_position": (50, 450),
            },
            "linkedin_banner": {
                "size": (1584, 396),
                "logo_position": (50, 50),
                "logo_size": (100, 100),
                "product_position": (1200, 100),
                "product_size": (300, 300),
                "text_position": (50, 200),
            },
        }

    def _enhance_prompt_for_banner(
        self, prompt: str, platform: str, theme_colors: Dict[str, str]
    ) -> str:
        """Enhance the prompt specifically for banner generation with brand colors."""
        # Extract color information
        primary_color = self._extract_color(
            theme_colors.get("primary", {}).get("color", "")
        )
        background_color = self._extract_color(
            theme_colors.get("primary", {}).get("backgroundColor", "")
        )
        text_color = self._extract_color(theme_colors.get("text", {}).get("color", ""))

        color_desc = ""
        if primary_color:
            color_desc += f"primary color {primary_color}, "
        if background_color and background_color != "rgba(0, 0, 0, 0)":
            color_desc += f"background color {background_color}, "
        if text_color:
            color_desc += f"text color {text_color}, "

        if not color_desc:
            color_desc = "professional color scheme, "

        platform_specific_enhancements = {
            "facebook_post": "professional, eye-catching Facebook sales banner with clear messaging and prominent product display",
            "instagram_post": "visually striking Instagram sales post with vibrant colors and central product focus",
            "twitter_post": "clean, minimalist Twitter sales banner with concise visual message and product highlight",
            "linkedin_banner": "professional LinkedIn sales header with corporate aesthetic and subtle product placement",
        }

        enhancement = platform_specific_enhancements.get(
            platform, "high-quality sales banner"
        )
        enhanced_prompt = f"{prompt}. Create a {enhancement}, with {color_desc}balanced composition, well-integrated text and visuals. Design for a sales promotion with special offer look and feel. Ensure any text is readable and the overall design is cohesive."

        return enhanced_prompt

    def _extract_color(self, color_str: str) -> str:
        """Extract simple color information from CSS color strings."""
        if not color_str or color_str == "rgba(0, 0, 0, 0)":
            return ""

        # Extract RGB values from rgb(r, g, b) or rgba(r, g, b, a)
        rgb_match = re.search(r"rgb\((\d+),\s*(\d+),\s*(\d+)\)", color_str)
        if rgb_match:
            r, g, b = map(int, rgb_match.groups())
            # Determine closest basic color name
            return self._get_color_name(r, g, b)

        rgba_match = re.search(
            r"rgba\((\d+),\s*(\d+),\s*(\d+),\s*([\d.]+)\)", color_str
        )
        if rgba_match:
            r, g, b = map(int, rgba_match.groups()[:3])
            return self._get_color_name(r, g, b)

        # Return as is if no match
        return color_str

    def _get_color_name(self, r: int, g: int, b: int) -> str:
        """Get a simple color name based on RGB values."""
        # Simple color naming for diffusion model understanding
        if r > 200 and g > 200 and b > 200:
            return "white"
        elif r < 50 and g < 50 and b < 50:
            return "black"
        elif r > 200 and g < 100 and b < 100:
            return "red"
        elif r < 100 and g > 150 and b < 100:
            return "green"
        elif r < 100 and g < 100 and b > 200:
            return "blue"
        elif r > 200 and g > 150 and b < 100:
            return "yellow"
        elif r > 200 and g < 150 and b > 200:
            return "purple"
        elif r < 100 and g > 150 and b > 150:
            return "teal"
        else:
            return f"rgb({r},{g},{b})"

    def _download_image(self, url: str) -> Optional[Image.Image]:
        """Download image from URL and return PIL Image object."""
        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                return Image.open(io.BytesIO(response.content))
            else:
                print(f"Failed to download image: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error downloading image: {str(e)}")
            return None

    def _resize_image(self, image: Image.Image, size: Tuple[int, int]) -> Image.Image:
        """Resize image while preserving aspect ratio."""
        if not image:
            return None

        # Calculate aspect ratio
        width, height = image.size
        aspect = width / height

        target_width, target_height = size
        target_aspect = target_width / target_height

        if aspect > target_aspect:
            # Image is wider than target
            new_width = target_width
            new_height = int(target_width / aspect)
        else:
            # Image is taller than target
            new_height = target_height
            new_width = int(target_height * aspect)

        return image.resize((new_width, new_height), Image.LANCZOS)

    def _generate_base_banner(
        self,
        prompt: str,
        platform: str,
        size: Tuple[int, int],
        theme_colors: Dict[str, Dict[str, str]],
    ) -> Optional[Image.Image]:
        """Generate a base banner using the text-to-image model."""
        try:
            enhanced_prompt = self._enhance_prompt_for_banner(
                prompt, platform, theme_colors
            )

            # Prepare the payload for the diffusion model
            payload = {
                "inputs": enhanced_prompt,
                "parameters": {
                    "width": size[0],
                    "height": size[1],
                    "num_inference_steps": 30,
                    "guidance_scale": 7.5,
                },
            }

            # Set up headers
            headers = {
                "Accept": "image/png",
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            # Make the API call
            response = requests.post(self.endpoint_url, headers=headers, json=payload)

            if response.status_code == 200:
                # Convert response content to PIL Image
                image = Image.open(io.BytesIO(response.content))
                return image
            else:
                print(
                    f"Error generating banner for {platform}: {response.status_code} - {response.text}"
                )
                return None

        except Exception as e:
            print(f"Error generating banner for {platform}: {str(e)}")
            return None

    def _compose_final_banner(
        self,
        base_banner: Image.Image,
        logo_image: Optional[Image.Image],
        product_image: Optional[Image.Image],
        platform: str,
        template: Dict[str, Any],
    ) -> Image.Image:
        """Compose final banner by overlaying logo and product images on base banner."""
        if not base_banner:
            return None

        # Create a copy of the base banner
        final_banner = base_banner.copy()

        # Add logo if available
        if logo_image:
            # Resize logo
            resized_logo = self._resize_image(logo_image, template["logo_size"])
            if resized_logo:
                # Create logo with transparency
                logo_with_alpha = resized_logo.convert("RGBA")

                # Calculate position to paste logo
                logo_position = template["logo_position"]

                # Paste logo onto banner
                final_banner.paste(
                    logo_with_alpha,
                    logo_position,
                    logo_with_alpha if logo_with_alpha.mode == "RGBA" else None,
                )

        # Add product image if available
        if product_image:
            # Resize product image
            resized_product = self._resize_image(
                product_image, template["product_size"]
            )
            if resized_product:
                # Create product image with transparency
                product_with_alpha = resized_product.convert("RGBA")

                # Calculate position to paste product
                product_position = template["product_position"]

                # Paste product onto banner
                final_banner.paste(
                    product_with_alpha,
                    product_position,
                    product_with_alpha if product_with_alpha.mode == "RGBA" else None,
                )

        return final_banner

    def _save_image(self, image: Image.Image, platform: str) -> str:
        """Save generated image to file and return the path."""
        self._create_directory()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{platform}_sales_{timestamp}.png"
        filepath = os.path.join(self.output_dir, filename)

        image.save(filepath)
        return filepath

    def _image_to_base64(self, image: Image.Image) -> str:
        """Convert PIL Image to base64 string."""
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    def _extract_image_urls(self, json_data: Dict) -> Dict[str, List[str]]:
        """Extract logo and product image URLs from JSON data."""
        image_urls = {"logo": [], "product": []}

        # Extract logo URLs
        if "banner" in json_data:
            # Try to find logo in the banner
            if "logo" in json_data["banner"] and json_data["banner"]["logo"]:
                image_urls["logo"].append(json_data["banner"]["logo"])

        # Extract product image URLs
        if "banner" in json_data and "products" in json_data["banner"]:
            for product in json_data["banner"]["products"]:
                if "images" in product and product["images"]:
                    # Add first product image
                    for img_url in product["images"]:
                        if (
                            img_url
                            and isinstance(img_url, str)
                            and (
                                img_url.startswith("http")
                                or img_url.startswith("https")
                            )
                        ):
                            image_urls["product"].append(img_url)
                            break

        return image_urls

    def _extract_theme_colors(self, json_data: Dict) -> Dict[str, Dict[str, str]]:
        """Extract theme colors from JSON data."""
        theme_colors = {
            "primary": {"color": "", "backgroundColor": ""},
            "text": {"color": "", "backgroundColor": ""},
        }

        if "banner" in json_data and "theme" in json_data["banner"]:
            theme = json_data["banner"]["theme"]
            if "colors" in theme:
                colors = theme["colors"]

                if "primary" in colors:
                    theme_colors["primary"] = colors["primary"]

                if "text" in colors:
                    theme_colors["text"] = colors["text"]

        return theme_colors

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Generate multiple sales banners based on the marketing prompt."""
        try:
            # Parse input
            original_json = None
            try:
                # Try parsing as JSON
                parsed_input = json.loads(prompt)

                # Check if it's from the previous processor
                if "prompt" in parsed_input:
                    marketing_prompt = parsed_input["prompt"]
                    if "original_json" in parsed_input:
                        original_json = parsed_input["original_json"]
                elif "marketing_copy" in parsed_input:
                    marketing_prompt = parsed_input["marketing_copy"]
                    if "original_json" in parsed_input:
                        original_json = parsed_input["original_json"]
                else:
                    # Assume this is the original JSON
                    original_json = parsed_input
                    # Extract a basic prompt
                    if "banner" in original_json and "title" in original_json["banner"]:
                        marketing_prompt = f"Create a sales banner for {original_json['banner']['title']}"
                    else:
                        marketing_prompt = "Create a professional sales banner"
            except json.JSONDecodeError:
                # Use input directly as prompt
                marketing_prompt = prompt

            # Get social media templates
            social_media_templates = self._get_social_media_sizes()

            # Extract image URLs and theme colors
            image_urls = {"logo": [], "product": []}
            theme_colors = {
                "primary": {"color": "", "backgroundColor": ""},
                "text": {"color": "", "backgroundColor": ""},
            }

            if original_json:
                image_urls = self._extract_image_urls(original_json)
                theme_colors = self._extract_theme_colors(original_json)

            # Download images
            logo_image = None
            if image_urls["logo"]:
                logo_image = self._download_image(image_urls["logo"][0])

            product_image = None
            if image_urls["product"]:
                product_image = self._download_image(image_urls["product"][0])

            # Generate banners for each platform
            results = {}
            banners_info = []

            for platform, template in social_media_templates.items():
                # Generate base banner
                base_banner = self._generate_base_banner(
                    marketing_prompt, platform, template["size"], theme_colors
                )

                if base_banner:
                    # Compose final banner with logo and product image
                    final_banner = self._compose_final_banner(
                        base_banner, logo_image, product_image, platform, template
                    )

                    # Save banner
                    filepath = self._save_image(final_banner, platform)

                    # Store information
                    banner_info = {
                        "platform": platform,
                        "size": f"{template['size'][0]}x{template['size'][1]}",
                        "filepath": filepath,
                        "base64": self._image_to_base64(final_banner)[:100]
                        + "...",  # Truncated for response size
                    }
                    banners_info.append(banner_info)

                    results[platform] = {
                        "status": "success",
                        "filepath": filepath,
                        "size": template["size"],
                    }
                else:
                    results[platform] = {
                        "status": "error",
                        "message": f"Failed to generate banner for {platform}",
                    }

            # Create response
            response = {
                "original_prompt": marketing_prompt,
                "used_logo": bool(logo_image),
                "used_product_image": bool(product_image),
                "used_theme_colors": any(v.get("color") for v in theme_colors.values()),
                "banners_generated": len(banners_info),
                "banners": banners_info,
                "detailed_results": results,
            }

            return json.dumps(response, indent=2)

        except Exception as e:
            return json.dumps({"error": str(e), "banners_generated": 0, "banners": []})

    def chain_from_json_processor(self, json_processor_output: str) -> str:
        """Chain from JSON processor output directly."""
        # Parse the JSON processor output
        try:
            content = json.loads(json_processor_output)

            # Add original JSON data for image extraction
            if hasattr(self, "_original_json") and self._original_json:
                content["original_json"] = self._original_json

            return self._call(json.dumps(content))
        except:
            return self._call(json_processor_output)


# # Example of how to create a complete chain
# class MarketingBannerChain:
#     """
#     A complete chain that processes JSON data and generates sales banners with branding.
#     """

#     def __init__(
#         self,
#         json_processor_endpoint: str,
#         json_processor_api_key: str,
#         image_generator_endpoint: str,
#         image_generator_api_key: str,
#         output_dir: str = "generated_banners",
#     ):
#         # Import here to avoid circular imports
#         from your_module import JSONProcessorLLM

#         self.json_processor = JSONProcessorLLM(
#             endpoint_url=json_processor_endpoint, api_key=json_processor_api_key
#         )

#         self.banner_generator = BannerGenerationLLM(
#             endpoint_url=image_generator_endpoint,
#             api_key=image_generator_api_key,
#             output_dir=output_dir,
#         )

#     def process(self, json_input: str) -> Dict:
#         """Process JSON input and generate sales banners with branding."""
#         # Store original JSON for later image extraction
#         original_json = json.loads(json_input)

#         # Process JSON and generate marketing content
#         processed_content = self.json_processor(json_input)

#         # Parse the processed content
#         try:
#             content_dict = json.loads(processed_content)
#             # Add original JSON for image extraction
#             content_dict["original_json"] = original_json
#             processed_content_with_json = json.dumps(content_dict)
#         except:
#             # If can't parse, just pass the original content
#             processed_content_with_json = processed_content

#         # Generate banners based on marketing content
#         banners_result = self.banner_generator(processed_content_with_json)

#         # Parse the result back to dictionary
#         return json.loads(banners_result)


# # Example usage
# if __name__ == "__main__":
#     # Initialize the banner generator
#     banner_generator = BannerGenerationLLM(
#         endpoint_url="https://w8ifbuxsvvz477wc.us-east-1.aws.endpoints.huggingface.cloud",
#         api_key="hf_XXXXX",  # Replace with actual API key
#         output_dir="generated_banners",
#     )

#     # Example input (could be the raw JSON or from the JSONProcessorLLM)
#     with open("sample_json.json", "r") as f:
#         json_input = f.read()

#     # Generate banners directly from raw JSON
#     result = banner_generator(json_input)
#     print(result)

#     # Alternatively, create and use the complete chain
#     chain = MarketingBannerChain(
#         json_processor_endpoint="https://zu3b6gl83cdhnhoq.us-east-1.aws.endpoints.huggingface.cloud/v1/chat/completions",
#         json_processor_api_key="hf_XXXXX",  # Replace with actual API key
#         image_generator_endpoint="https://w8ifbuxsvvz477wc.us-east-1.aws.endpoints.huggingface.cloud",
#         image_generator_api_key="hf_XXXXX",  # Replace with actual API key
#         output_dir="generated_banners",
#     )

#     complete_result = chain.process(json_input)
#     print(json.dumps(complete_result, indent=2))
