import base64
import io
import time

from aiocache import cached
from fastapi import APIRouter, File, HTTPException, UploadFile
from PIL import Image

from app._enums import Actions, Callbacks, ImageMimeTypes
from app._tools import tools
from app.core.callbacks import ReviewCallback
from app.core.completion import CompletionModel
from app.core.config import settings
from app.models.models import SignDetectors
from app.utils.image_processing import correct_inversion

router = APIRouter(tags=["sync"])


CALLBACKS: dict[Callbacks, ReviewCallback] = {
    Callbacks.REVIEW: ReviewCallback(),
}


@router.get("/ping", response_model=dict, tags=["Health"])
async def ping() -> dict:
    """
    Health check endpoint for readiness/liveness probes.
    """
    now: int = int(time.time())
    uptime: int = now - int(settings.service_start_time)
    return {
        "status": "ok",
        "version": settings.version,
        "uptime": uptime,
        "timestamp": now,
    }


@router.post(
    "/completion",
    tags=["completion", "llm", "sync", "model", "text"],
    description="Endpoint to generate text completions for a given input using a registered model.",
)
@cached(ttl=60)
async def completion(file: UploadFile = File(...)) -> dict:
    """
    Endpoint to generate text completions for a given input using a registered model.

    This endpoint allows clients to send input data, and returns the corresponding completions generated by the specified system.

    Args:
        data (UploadFile): The input data containing the model name and input text.

    Returns:
        CompletionResponse: A response object containing the model name, description, queries, and answers generated by the model.
    """
    if file.content_type not in [
        ImageMimeTypes.JPEG,
        ImageMimeTypes.PNG,
        ImageMimeTypes.PNG,
    ]:
        raise HTTPException(status_code=400, detail="Image format not supported.")

    contents = await file.read()
    image = Image.open(io.BytesIO(contents))
    image, _ = correct_inversion(image)

    buf = io.BytesIO()
    image.save(buf, format="PNG")
    image_b64 = base64.b64encode(buf.getvalue()).decode()

    model = CompletionModel(token=settings.openai_api_key)
    analysis = model.generate(
        "",
        images=[f"data:{file.content_type};base64,{image_b64}"],
        system_instruction="Use the following tools to analyze the bacterial plate.",
        tools=tools,
    )

    analysis = model.generate(
        "Write a detailed report about the bacterial plate analysis.",
        images=[f"data:{file.content_type};base64,{image_b64}"],
        system_instruction=settings.get_rendered_prompt(
            "colony_analyzer",
            context={
                "tool_results": str(analysis.data),
            },
        ),
    )

    analysis_to_markdown = model.generate(
        f"Write a detailed report about the bacterial plate analysis. This is the analysis result: {analysis.data}",
        images=[f"data:{file.content_type};base64,{image_b64}"],
        system_instruction=settings.get_rendered_prompt(
            "colony_report_writer",
        ),
    )

    prompt = settings.get_rendered_prompt("sign_detector")

    model = CompletionModel(token=settings.openai_api_key)
    callbacks_or_tools = model.generate(
        "",
        images=[f"data:{file.content_type};base64,{image_b64}"],
        response_format=SignDetectors,
        system_instruction=prompt,
    )

    for element in callbacks_or_tools.data.get("signs", []):
        if isinstance(element, dict) and element.get("type") == Actions.CALLBACK:
            callback_name = element.get("name")
            if callback_name in CALLBACKS:
                parameters = element.get("parameters", {})
                parameters.update({"data": analysis_to_markdown.data})

                callback = CALLBACKS[callback_name]
                _ = callback.execute(**parameters)
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Callback {callback_name} not found.",
                )
        else:
            # Optionally log or skip non-dict elements
            continue

    return {"data": analysis_to_markdown.data}
