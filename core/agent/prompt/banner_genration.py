import json
import re
import webcolors


def closest_color(requested_color):
    min_colors = {}
    for name, hex_code in webcolors.CSS3_NAMES_TO_HEX.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(hex_code)
        rd = (r_c - requested_color[0]) ** 2
        gd = (g_c - requested_color[1]) ** 2
        bd = (b_c - requested_color[2]) ** 2
        min_colors[(rd + gd + bd)] = name
    return min_colors[min(min_colors.keys())]


def get_color_name(color_code: str) -> str:
    try:
        if color_code.startswith("rgb"):
            rgb = tuple(map(int, re.findall(r"\d+", color_code)))
        if color_code.startswith("rgba"):
            rgb = tuple(map(int, re.findall(r"\d+", color_code)))[:3]
        elif color_code.startswith("#"):
            rgb = webcolors.hex_to_rgb(color_code)
        else:
            return color_code  # fallback
        try:
            return webcolors.rgb_to_name(rgb)
        except ValueError:
            return closest_color(rgb)
    except Exception:
        return color_code


def extract_product_descriptions(json_input: str) -> str:
    raw_data = json.loads(json_input)
    banner_data = raw_data["banner"]

    products = banner_data.get("products", [])
    descriptions = []

    for product in products:
        desc = product.get("description", "").strip()
        title = product.get("title", "").strip()

        if desc:
            descriptions.append(desc)
        elif title:
            descriptions.append(f"Product titled '{title}'")

    if not descriptions:
        return "general supermarket products like school supplies, pencil boxes, and DIY kits"

    return ", ".join(descriptions)


def generate_banner_prompt(json_input: str) -> str:
    raw_data = json.loads(json_input)
    banner_data = raw_data["banner"]

    title = banner_data.get("title", "")
    description = banner_data.get("metadata", {}).get("description", "")
    keywords = banner_data.get("metadata", {}).get("keywords", "")
    font = (
        banner_data.get("fonts", {})
        .get("headings", {})
        .get("family", "")
        .replace("\\", "")
        .replace('"', "")
    )
    font_color_code = (
        banner_data.get("theme", {}).get("colors", {}).get("text", {}).get("color", "")
    )
    background_color_code = (
        banner_data.get("theme", {})
        .get("background", {})
        .get("body", {})
        .get("backgroundColor", "")
    )

    font_color_name = get_color_name(font_color_code)
    background_color_name = get_color_name(background_color_code)

    product_desc = extract_product_descriptions(json_input)

    prompt = f"""
Design a visually engaging social media sales banner for the brand:

Store Name: {title}
Brand Vibe: Clean and modern with a supermarket feel
Font Style: {font}, color {font_color_name}
Background Color: {background_color_name}
Store Description: {description}
Keywords: {keywords}
Featured Products: {product_desc}

Incorporate graphical illustrations of the featured products.
Avoid using real product images or URLs. Make the banner suitable for Instagram and Facebook.
"""
    return prompt.strip()


# Example usage:
# prompt = generate_banner_prompt(your_json_string_here)
# print(prompt)
