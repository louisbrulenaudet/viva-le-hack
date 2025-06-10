import enum
from io import BytesIO

import gradio as gr
import requests
from PIL import Image
from pydantic_settings import BaseSettings


class ImageFormats(enum.StrEnum):
    JPEG = "JPEG"
    PNG = "PNG"


class Settings(BaseSettings):
    api_url: str = "http://localhost:8000/api/v1/completion"
    image_format: ImageFormats = ImageFormats.JPEG
    mime_type: str = "image/jpeg"
    image_filename: str = "capture.jpg"


settings = Settings()


def send_image_to_api(image: Image.Image) -> dict:
    # Convert PIL image to JPEG bytes
    buffered = BytesIO()
    image.save(buffered, format=settings.image_format)
    buffered.seek(0)

    # Create multipart/form-data payload
    files: dict[str, tuple[str, BytesIO, str]] = {
        "file": (settings.image_filename, buffered, settings.mime_type)
    }
    response = requests.post(settings.api_url, files=files)

    try:
        result_json = response.json()
        return result_json

    except Exception as e:
        return {
            "message": f"Error in API call: {str(e)}",
        }


example_images: list[str] = [
    "https://pub-6c7e4dfe67f8438aaf1ccba97c8a82be.r2.dev/colonies/7000b769-7fcc-4336-83a0-5e4567121f9f.jpg"
]

iface: gr.Interface = gr.Interface(
    fn=send_image_to_api,
    inputs=gr.Image(
        sources="webcam", label="Capture culture plate", streaming=False, type="pil"
    ),
    examples=example_images,
    outputs=[
        gr.JSON(label="Structured result"),
    ],
    title="Bacterial Culture Analyzer",
    live=False,
)

if __name__ == "__main__":
    iface.launch()
