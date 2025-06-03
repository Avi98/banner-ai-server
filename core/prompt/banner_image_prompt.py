from langchain_core.prompts import PromptTemplate

from core.agent.types import Platform


def electronics_prompts(
    platform: Platform,
    tagline: str,
    main_title_emphasis: str,
    sales_dates: str,
    discount_text: str,
):
    electronics_prompt_without_logo = """
	Design and create a modern and clean eCommerce sale banner image for a promotional electronics event.

	**Platforms:** {platform}
	**Image Size:** 1200x628 pixels (under 8MB)

	### Style & Background:
	- Use a smooth, gradient blue background with abstract shapes, waves, and clean modern design elements.
	- Place a curved yellow accent on the left and right sides to add vibrance.
	- Keep the design minimal, friendly, and professional.

	### Product Layout:
	- Display multiple electronic appliances (image 1) prominently on the right side: refrigerator, TV, tablet, camera, printer, remote, and air cooler.
	- Arrange the products in a group, slightly overlapping with subtle shadows.
	- Make sure image 1 blends seamlessly into the scene.

	### Text Content (on the left side):
	- Top Tagline: "{tagline}"
	- Highlighted Main Title:
	- "{main_title_emphasis}" (in white bold caps with yellow background)
	- "{main_title_rest}" (in blue bold caps)
	- Sale Dates: "{sale_dates}"
	- Discount Message: "{discount_text}" (bold and circular layout near bottom left)
	- Use clean, bold fonts; align text vertically with good spacing.

	### Branding:
	- No specific logo required
	- Website or brand name can be added at the bottom if space allows.

	Ensure the banner is professional, engaging, and ready for {platform} ad campaigns.
"""

    prompt_template = PromptTemplate.from_template(electronics_prompt_without_logo)
    variables = {
        "platform": platform,
        "tagline": tagline,
        "main_title_emphasis": main_title_emphasis,
        "sale_dates": sales_dates,
        "discount_text": discount_text,
        "main_title_rest": "",
    }
    return prompt_template.invoke(variables).to_string()
