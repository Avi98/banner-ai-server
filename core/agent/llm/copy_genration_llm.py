from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
from typing import Any, Dict, List, Optional, Mapping
import json
import requests
from pydantic import BaseModel, Field, root_validator


class JSONProcessorLLM(LLM):
    """
    Custom LLM that processes JSON data to extract relevant information
    and generate prompts and marketing copy.
    """

    endpoint_url: str = Field(description="URL of the text generation model API")
    api_key: str = Field(description="API key for the text generation model")

    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True

    @property
    def _llm_type(self) -> str:
        return "json-processor-llm"

    def _extract_relevant_info(self, json_data: Dict) -> Dict:
        """Extract relevant information from the JSON data."""
        relevant_info = {}

        # Extract banner information
        if "banner" in json_data:
            banner = json_data["banner"]

            # Title and description
            relevant_info["title"] = banner.get("title", "")

            if "metadata" in banner:
                relevant_info["description"] = banner["metadata"].get("description", "")
                relevant_info["keywords"] = banner["metadata"].get("keywords", "")

            # Theme and fonts
            if "fonts" in banner:
                relevant_info["fonts"] = {
                    "headings": banner["fonts"].get("headings", {}),
                    "body": banner["fonts"].get("body", {}),
                }

            if "theme" in banner:
                if "colors" in banner["theme"]:
                    relevant_info["colors"] = banner["theme"]["colors"]

            # Products
            if "products" in banner and banner["products"]:
                products = []
                for product in banner["products"]:
                    products.append(
                        {
                            "title": product.get("title", ""),
                            "description": product.get("description", ""),
                        }
                    )
                relevant_info["products"] = products

            # Contact info
            if "contact_info" in banner:
                relevant_info["contact_info"] = {
                    "email": banner["contact_info"].get("email", ""),
                    "phone": banner["contact_info"].get("phone", ""),
                }

        return relevant_info

    def _generate_content(self, relevant_info: Dict) -> Dict:
        """Generate prompt and marketing copy based on the extracted information."""
        # Create a prompt for the next LLM
        prompt = f"""Generate compelling marketing content for a business with the following details:
Business Name: {relevant_info.get('title', 'Unknown Business')}
Business Description: {relevant_info.get('description', 'No description available')}
Keywords: {relevant_info.get('keywords', 'No keywords available')}

The business offers the following products or services:
{self._format_products(relevant_info.get('products', []))}

The business has the following aesthetic:
- Font style for headings: {self._format_font(relevant_info.get('fonts', {}).get('headings', {}))}
- Font style for body: {self._format_font(relevant_info.get('fonts', {}).get('body', {}))}
- Primary colors: {self._format_colors(relevant_info.get('colors', {}).get('primary', {}))}
- Text colors: {self._format_colors(relevant_info.get('colors', {}).get('text', {}))}

Create a marketing copy that highlights the unique value proposition, target audience, 
and main benefits of the products or services.
"""

        # Generate a basic marketing copy based on available information
        marketing_copy = self._create_marketing_copy(relevant_info)

        return {"prompt": prompt, "marketing_copy": marketing_copy}

    def _format_products(self, products: List[Dict]) -> str:
        """Format product information as a string."""
        if not products:
            return "No product information available"

        result = ""
        for i, product in enumerate(products):
            result += f"Product {i+1}: {product.get('title', 'Unnamed Product')}\n"
            if product.get("description"):
                result += f"Description: {product.get('description')}\n"
            result += "\n"

        return result

    def _format_font(self, font_info: Dict) -> str:
        """Format font information as a string."""
        if not font_info:
            return "No font information available"

        result = ""
        if font_info.get("family"):
            result += f"Family: {font_info.get('family')} "
        if font_info.get("size"):
            result += f"Size: {font_info.get('size')} "
        if font_info.get("weight"):
            result += f"Weight: {font_info.get('weight')} "
        if font_info.get("color"):
            result += f"Color: {font_info.get('color')}"

        return result.strip()

    def _format_colors(self, color_info: Dict) -> str:
        """Format color information as a string."""
        if not color_info:
            return "No color information available"

        result = ""
        if color_info.get("color"):
            result += f"Color: {color_info.get('color')} "
        if color_info.get("backgroundColor"):
            result += f"Background: {color_info.get('backgroundColor')}"

        return result.strip()

    def _create_marketing_copy(self, info: Dict) -> str:
        """Create a basic marketing copy based on the available information."""
        title = info.get("title", "Our Business")
        description = info.get("description", "")
        keywords = info.get("keywords", "").split(",")

        # Extract relevant keywords for use in the copy
        relevant_keywords = [kw.strip() for kw in keywords if kw.strip()][:5]

        marketing_copy = f"# {title}\n\n"

        if description:
            marketing_copy += f"{description}\n\n"

        if relevant_keywords:
            marketing_copy += "## What We Offer\n\n"
            for keyword in relevant_keywords:
                marketing_copy += f"- {keyword.title()}\n"

        products = info.get("products", [])
        if products:
            marketing_copy += "\n## Our Products\n\n"
            for product in products:
                marketing_copy += f"### {product.get('title', 'Product')}\n"
                if product.get("description"):
                    marketing_copy += f"{product.get('description')}\n\n"

        contact_info = info.get("contact_info", {})
        if contact_info:
            marketing_copy += "\n## Contact Us\n\n"
            if contact_info.get("email"):
                marketing_copy += f"Email: {contact_info.get('email')}\n"
            if contact_info.get("phone"):
                marketing_copy += f"Phone: {contact_info.get('phone')}\n"

        return marketing_copy

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Process JSON input and generate content."""
        try:
            # Parse JSON from the prompt
            json_data = json.loads(prompt)

            # Extract relevant information
            relevant_info = self._extract_relevant_info(json_data)

            # Generate content based on extracted information
            content = self._generate_content(relevant_info)

            # Return content as JSON string
            return json.dumps(content, indent=2)

        except json.JSONDecodeError:
            return json.dumps(
                {"error": "Invalid JSON input", "prompt": "", "marketing_copy": ""}
            )
        except Exception as e:
            return json.dumps({"error": str(e), "prompt": "", "marketing_copy": ""})

    async def chain_to_text_model(self, content: Dict) -> str:
        """Send the generated prompt to the text generation model."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        data = {
            "model": "bartowski/Qwen2.5-Coder-32B-Instruct-GGUF",
            "messages": [{"role": "user", "content": content["prompt"]}],
            "max_tokens": 500,
            "stream": False,
        }

        try:
            response = requests.post(self.endpoint_url, headers=headers, json=data)

            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                return f"Error: {response.status_code} - {response.text}"

        except Exception as e:
            return f"Error connecting to text model API: {str(e)}"


# # Example usage
# if __name__ == "__main__":
#     # Initialize the custom LLM
#     json_processor = JSONProcessorLLM(
#         endpoint_url="https://zu3b6gl83cdhnhoq.us-east-1.aws.endpoints.huggingface.cloud/v1/chat/completions",
#         api_key="hf_XXXXX",  # Replace with actual API key
#     )

#     # Sample JSON input (you would typically pass this as a string)
#     with open("sample_json.json", "r") as f:
#         json_input = f.read()

#     # Process the JSON input
#     result = json_processor(json_input)
#     print(result)

#     # If you want to chain the result to the text model:
#     content = json.loads(result)
#     text_response = json_processor.chain_to_text_model(content)
#     print("\nText Model Response:")
#     print(text_response)
