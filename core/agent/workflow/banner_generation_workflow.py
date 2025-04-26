import json
from huggingface_hub import InferenceClient
from typing import Dict, Any, Tuple
from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime
from io import BytesIO
import base64
from config.env_variables import settings
import logging

from core.agent.utils.get_color_by_rgb import ColorName
from core.utils.logger import Logger


class BannerGenerationWorkflow:
    def __init__(
        self,
        hf_token: str,
        model_endpoint: str,
        sd_endpoint: str,
        output_dir: str = "generated_banners",
        log_file: str = "banner_generation.log",
    ):
        self.hf_token = hf_token
        self.model_endpoint = model_endpoint
        self.sd_endpoint = sd_endpoint
        self.output_dir = output_dir
        self.client = InferenceClient(token=hf_token)
        self.font_path = "fonts/BerkshireSwash-Regular.ttf"  # Path to your font file
        self.default_background_color = (
            "#FFD700"  # Default yellow color (can be changed)
        )
        self.logger = Logger.get_logger(name="banner_generation", level=logging.DEBUG)

        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            self.logger.info(f"Creating output directory: {self.output_dir}")
            os.makedirs(self.output_dir)

        self.logger.info("BannerGenerationWorkflow initialized")

    def _extract_banner_info(self, json_data: Dict) -> Dict[str, Any]:
        """Extract relevant information from the scrapped data"""
        self.logger.debug("Extracting banner information from JSON data")

        banner_data = json_data.get("banner", {})
        title = banner_data.get("title", "")

        if not title:
            self.logger.warning("No title found in banner data")

        banner_info = {
            "title": title,
            "description": banner_data.get("metadata", {}).get("description", ""),
            "keywords": banner_data.get("metadata", {}).get("keywords", ""),
            "background_color": banner_data.get("theme", {})
            .get("background", {})
            .get("body", {})
            .get("backgroundColor", self.default_background_color),
            "text_color": "#000000",  # Default black text
            "products": banner_data.get("products", []),
        }

        self.logger.debug(
            f"Banner info extracted: title='{title}', keywords count={len(banner_info['keywords'].split(',')) if banner_info['keywords'] else 0}"
        )
        return banner_info

    def _generate_short_copy(self, banner_info: Dict[str, Any]) -> str:
        """Generate short copy text (3-4 words) using LLM"""
        self.logger.info("Generating short copy text using LLM")

        prompt = f"""Create a short, impactful marketing phrase for:
        
        Business: {banner_info['title']}
        Description: {banner_info['description']}
        Keywords: {banner_info['keywords']}
        
        The copy should be VERY SHORT (3-4 words maximum), catchy, and instantly convey value.
        Examples: "SPECIAL OFFER", "LIMITED TIME DEAL", "FLASH SALE TODAY", "PREMIUM QUALITY"
        
        Generate ONLY the phrase, nothing else."""

        try:
            self.logger.debug(f"Sending prompt to LLM: length={len(prompt)} chars")

            response = self.client.chat_completion(
                model=settings.qwen_model_endpoint,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=20,  # Keep it short
            )
            copy_text = response.choices[0].message.content.strip()

            # Ensure it's short (3-4 words)
            words = copy_text.split()
            if len(words) > 4:
                self.logger.debug(
                    f"Generated copy too long ({len(words)} words). Truncating to 4 words."
                )
                copy_text = " ".join(words[:4])

            formatted_copy = copy_text.upper()  # Return in uppercase for emphasis
            self.logger.info(f"Generated copy text: '{formatted_copy}'")
            return formatted_copy

        except Exception as e:
            self.logger.error(f"Error generating copy text: {str(e)}", exc_info=True)
            self.logger.info("Using default fallback copy text")
            return "SPECIAL OFFER"  # Default fallback

    def _generate_background(
        self, color_code: str, width: int = 800, height: int = 600
    ) -> Image.Image:
        """Generate background image using Stable Diffusion"""

        fake_color_code = "Electric Blue"
        self.logger.info(
            # f"Generating background with color: {color_code}, dimensions: {width}x{height}"
            f"Generating background with color: {fake_color_code}, dimensions: {width}x{height}"
        )

        prompt = f"""Create a simple, clean abstract background with {fake_color_code} color.
        The background should:
        - Have subtle gradients or patterns
        - Be suitable for text overlay
        - Look professional and modern
        """
        # - Have a speech bubble or announcement shape

        try:
            self.logger.debug(
                f"Sending image generation prompt to Stable Diffusion: length={len(prompt)} chars"
            )

            response = self.client.text_to_image(
                prompt=prompt,
                model=settings.stable_diffusion_endpoint,
                negative_prompt="text, logos, symbols, busy designs, dark shadows",
                num_inference_steps=30,
                guidance_scale=7.5,
            )

            self.logger.debug(
                f"Background image generated. Original size: {response.width}x{response.height}"
            )

            # Resize to desired dimensions
            background = response.resize((width, height), Image.LANCZOS)

            # Enhance background with color overlay
            # Light Charcoal
            return background

        except Exception as e:
            self.logger.error(f"Error generating background: {str(e)}", exc_info=True)
            self.logger.info("Using fallback gradient background")

            # Fallback: Create a simple gradient background
            background = Image.new("RGB", (width, height), color_code)
            return background

    def generate_illustration(self, color: str, secondary_color: str) -> Image.Image:
        """Generate an illustration with specified colors"""

        # prompt = f"""Flat vector-style illustration of a back-to-school scene with a {color} and {secondary_color} color palette. Includes a backpack, globe, stack of books, pencils, apple, clock, paperclips, and a plant on a desk. Clean minimalistic layout with soft sparkles in the background. Vector-style, modern and playful."""
        prompt = f"""A flat vector-style illustration of stylish stationery pouches in blue and pink tones. Pouches are zippered or buttoned cases, neatly arranged or stacked, Visible contents include colorful pencils, pens, markers, erasers, rulers, and paperclips. Modern, minimalistic style with a playful, no background. Designed for back-to-school or stationery product branding."""

        response = self.client.text_to_image(
            prompt=prompt,
            model=settings.stable_diffusion_endpoint,
            negative_prompt="text, logos, symbols, busy designs, dark shadows",
            num_inference_steps=30,
            guidance_scale=7.5,
        )

        self.logger.debug(f"Illustration image generated.")

    def _add_text_to_background(
        self,
        background: Image.Image,
        text: str,
        font_path: str = None,
        text_color: str = "#000000",
        position: Tuple[int, int] = None,
    ) -> Image.Image:
        """Add text to the background image with the specified font"""
        self.logger.info(f"Adding text to background: '{text}'")

        if font_path is None:
            font_path = self.font_path

        # Create a copy of the background
        banner = background.copy()
        draw = ImageDraw.Draw(banner)

        # Calculate text size for proper positioning
        font_size = int(banner.width * 0.1)  # Adaptive font size
        try:
            self.logger.debug(f"Loading font: {font_path} with size {font_size}")
            font = ImageFont.truetype(font_path, font_size)
        except Exception as e:
            self.logger.warning(
                f"Font {font_path} not found, using default font: {str(e)}"
            )
            font = ImageFont.load_default()

        # Calculate text size
        # For PIL version compatibility
        try:
            self.logger.debug("Calculating text dimensions using textbbox")
            text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:]
        except Exception as e:
            # Fallback for older PIL versions
            self.logger.debug(
                f"textbbox not available, falling back to textsize: {str(e)}"
            )
            text_width, text_height = draw.textsize(text, font=font)

        # Center the text if position not specified
        if position is None:
            position = (
                (banner.width - text_width) // 2,
                (banner.height - text_height) // 2,
            )
            self.logger.debug(f"Text will be centered at position {position}")

        # Add text shadow for better visibility
        shadow_color = "#555555"
        shadow_offset = (2, 2)

        # Draw shadow
        self.logger.debug(f"Drawing text shadow at offset {shadow_offset}")
        draw.text(
            (position[0] + shadow_offset[0], position[1] + shadow_offset[1]),
            text,
            font=font,
            fill=shadow_color,
        )

        # Draw main text
        self.logger.debug(f"Drawing main text with color {text_color}")
        draw.text(position, text, font=font, fill=text_color)

        self.logger.info("Text added to background successfully")
        return banner

    def _generate_banner_prompt(self, title: str) -> str:
        """Generate a prompt for the banner background based on the title"""
        self.logger.info(f"Generating banner prompt based on title: '{title}'")

        prompt = f"""Given the business title "{title}", suggest a specific, descriptive prompt for 
        generating a background image for a marketing banner.
        
        The prompt should:
        1. Describe the type of business or product category
        2. Include relevant items or objects that represent the business
        3. Be specific enough for an image generation model
        
        For example, if the title is "Little Heroes Kids Store", the prompt might be:
        "Create a background for a children's clothing store with colorful toys, superhero figures, and children's clothing items arranged neatly."
        
        Provide ONLY the prompt, nothing else."""

        try:
            self.logger.debug(
                f"Sending prompt generation request to LLM: length={len(prompt)} chars"
            )

            response = self.client.chat_completion(
                model=settings.qwen_model_endpoint,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=100,
            )
            generated_prompt = response.choices[0].message.content.strip()
            self.logger.info(f"Generated banner prompt: '{generated_prompt[:50]}...'")
            return generated_prompt

        except Exception as e:
            self.logger.error(
                f"Error generating banner prompt: {str(e)}", exc_info=True
            )
            fallback_prompt = f"Create a background for {title} with relevant items and a professional appearance."
            self.logger.info(f"Using fallback prompt: '{fallback_prompt}'")
            return fallback_prompt

    def _save_banner(self, banner: Image.Image) -> Tuple[str, str]:
        """Save banner and return the path and base64 representation"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        banner_path = os.path.join(self.output_dir, f"banner_{timestamp}.png")

        self.logger.info(f"Saving banner to: {banner_path}")
        banner.save(banner_path)

        # Convert to base64 for API response
        buffered = BytesIO()
        banner.save(buffered, format="PNG")
        banner_base64 = base64.b64encode(buffered.getvalue()).decode()
        self.logger.debug(f"Banner converted to base64 (length: {len(banner_base64)})")

        return banner_path, banner_base64

    async def generate(self, scrape_data: str) -> Dict[str, Any]:
        """Main workflow to generate banner"""
        self.logger.info("Starting banner generation workflow")

        try:
            # Parse input data
            self.logger.debug("Parsing JSON scrape data")
            json_data = json.loads(scrape_data)
            banner_info = self._extract_banner_info(json_data)

            # 1. Generate short copy text
            self.logger.info("Generating short copy text")
            copy_text = self._generate_short_copy(banner_info)

            # 2. Generate background with specified color
            self.logger.info("Generating banner bg image")

            bg_color = ColorName().get_color_by_rgb(banner_info["background_color"])

            self.logger.debug(f"Using background color: {bg_color}")
            background = self._generate_background(bg_color)

            self.logger.debug(f"generate artifacts for banner: {bg_color}")
            background = self.generate_illustration(
                color="blue", secondary_color="pink"
            )

            # 3. Add text with Berkshire Swash font
            self.logger.info("Step 3: Adding text to background")
            banner = self._add_text_to_background(
                background,
                copy_text,
                self.font_path,
                banner_info.get("text_color", "#000000"),
            )

            # 4. Save the banner
            self.logger.info("Step 4: Saving banner")
            banner_path, banner_base64 = self._save_banner(banner)

            # 5. Generate background prompt based on title
            self.logger.info("Step 5: Generating background prompt")
            background_prompt = self._generate_banner_prompt(banner_info["title"])

            self.logger.info("Banner generation workflow completed successfully")
            return {
                "status": "success",
                "copy_text": copy_text,
                "banner_path": banner_path,
                "banner_base64": banner_base64,
                "background_prompt": background_prompt,
                "metadata": banner_info,
            }

        except Exception as e:
            self.logger.error(
                f"Error in banner generation workflow: {str(e)}", exc_info=True
            )
            return {"status": "error", "error": str(e)}

    async def generate_full_banner(
        self, scrape_data: str, use_generated_prompt: bool = True
    ) -> Dict[str, Any]:
        """Generate a complete banner with background and text based on prompt"""
        self.logger.info(
            f"Starting full banner generation. Use generated prompt: {use_generated_prompt}"
        )

        try:
            # Parse input data and generate basic banner first
            self.logger.debug("Generating basic banner first")
            result = await self.generate(scrape_data)

            if result["status"] == "error":
                self.logger.error(f"Basic banner generation failed: {result['error']}")
                return result

            # If user wants to use the generated prompt for a full banner
            if use_generated_prompt:
                self.logger.info(
                    "Generating full banner with custom background based on prompt"
                )
                json_data = json.loads(scrape_data)
                banner_info = self._extract_banner_info(json_data)
                background_prompt = result["background_prompt"]

                # Generate a new background based on the prompt
                try:
                    self.logger.info(
                        f"Generating custom background with prompt: '{background_prompt[:50]}...'"
                    )
                    new_background = self.client.text_to_image(
                        prompt=background_prompt,
                        model=settings.stable_diffusion_endpoint,
                        negative_prompt="text, logos, watermarks, blurry, low quality",
                        num_inference_steps=40,
                        guidance_scale=7.5,
                    )

                    # Add the same text to this new background
                    self.logger.info("Adding text to custom background")
                    full_banner = self._add_text_to_background(
                        new_background,
                        result["copy_text"],
                        self.font_path,
                        banner_info.get("text_color", "#000000"),
                    )

                    # Save the full banner
                    self.logger.info("Saving full banner")
                    full_banner_path, full_banner_base64 = self._save_banner(
                        full_banner
                    )

                    # Add full banner info to the result
                    result["full_banner_path"] = full_banner_path
                    result["full_banner_base64"] = full_banner_base64
                    self.logger.info("Full banner generated successfully")

                except Exception as e:
                    self.logger.error(
                        f"Error generating full banner: {str(e)}", exc_info=True
                    )
                    result["full_banner_error"] = str(e)

            return result

        except Exception as e:
            self.logger.error(
                f"Error in full banner generation: {str(e)}", exc_info=True
            )
            return {"status": "error", "error": str(e)}
