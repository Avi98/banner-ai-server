import base64
from io import BytesIO
from PIL import Image


def scale_b64_image(image_b64: str, scale_factor: float) -> str:
    """
    Scale down a base64 encoded image using Pillow.

    Args:
        image_b64: Base64 encoded image string
        scale_factor: Factor to scale the image by (0.5 = half size)

    Returns:
        Base64 encoded scaled image
    """
    try:
        # Decode base64 to PIL Image
        image_data = base64.b64decode(image_b64)
        image = Image.open(BytesIO(image_data))

        if image is None:
            return image_b64

        # Get original dimensions
        width, height = image.size

        # Calculate new dimensions
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)

        # Resize the image using high quality resampling
        resized_image = image.resize((new_width, new_height), Image.LANCZOS)

        # Convert back to base64
        buffer = BytesIO()
        resized_image.save(buffer, format="PNG")
        resized_image_b64 = base64.b64encode(buffer.getvalue()).decode()

        return resized_image_b64

    except Exception:
        return image_b64
