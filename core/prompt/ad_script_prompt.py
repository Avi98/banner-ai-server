from langchain.prompts import PromptTemplate


def get_ad_script_banner(**kwargs):
    prompt = """
You are a creative video scriptwriter for AI-generated promotional videos.

Using the inputs below, generate a descriptive and vivid video script prompt that will be used as input to a text-to-video generation model like Veo or Sora. The prompt should describe how the animation unfolds and what is shown — in a stylish, ad-ready, emotionally engaging way.

Use storytelling elements (scene, lighting, product animations, music, angles, ambiance) and make it suitable for a modern, vertical 3D animated ad video.

Inputs:
- Platform: {platform}
- Products: {product_list}
- Feature Highlights:
  1. {feature_1}
  2. {feature_2}
  3. {feature_3}
  4. {feature_4}
  5. {feature_5}
- Color Palette: {color_palette}
- Style: {style}
- Lighting: {lighting}
- Ambiance: {ambiance}
- CTA Text: {cta_text}
- Aspect Ratio: {aspect_ratio}
- Duration: {duration}
- Target Platform: {target_platform}

"""

    template = PromptTemplate(
        input_variables=[
            "platform",
            "feature_1",
            "feature_2",
            "feature_3",
            "feature_4",
            "feature_5",
            "color_palette",
            "style",
            "lighting",
            "ambiance",
            "cta_text",
            "aspect_ratio",
            "duration",
            "target_platform",
        ],
        template=prompt,
    )

    return template.invoke(input=kwargs)
