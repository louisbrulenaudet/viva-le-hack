import json
from datetime import datetime
from typing import Any

import openai
from PIL import Image

from app.models import models
from app.utils.encoders import ImageEncoder


def analyze_bacterial_plate(image: Image.Image) -> models.BacterialPlateAnalysis:
    """Analyze a bacterial plate image using OpenAI vision and predefined tools."""
    image_b64 = ImageEncoder.encode_image_to_base64(image)

    schema_fields = models.BacterialPlateAnalysis.model_json_schema()[
        "properties"
    ].keys()
    schema_description = "\n".join(
        [
            f"- {field}: {models.BacterialPlateAnalysis.model_fields[field].description or 'provide value'}"
            for field in schema_fields
            if field != "tool_interactions"
        ]
    )

    prompt_text = (
        "You are an expert microbiologist analyzing an agar plate image. "
        "Provide a comprehensive analysis in JSON format according to the following schema. "
        "Use tools if needed. Final response must be a single JSON object.\n\n"
        f"Schema:\n{schema_description}"
    )

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt_text},
                {"type": "image_url", "image_url": {"url": image_b64}},
            ],
        }
    ]

    response = openai.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=messages,
        tools=models.tools,
        tool_choice="auto",
        max_tokens=2000,
        temperature=0.2,
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    recorded_tool_interactions: list[dict[str, Any]] = []

    if tool_calls:
        messages.append(response_message)
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_response_content = models.execute_tool_call(tool_call, image_b64)
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response_content,
                }
            )
            recorded_tool_interactions.append(
                {
                    "tool_call_id": tool_call.id,
                    "function_name": function_name,
                    "arguments": json.loads(tool_call.function.arguments),
                    "response": json.loads(function_response_content),
                }
            )

        second_response = openai.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=messages,
            max_tokens=2000,
            temperature=0.2,
        )
        final_response_content = second_response.choices[0].message.content
    else:
        final_response_content = response_message.content

    if final_response_content.strip().startswith("```json"):
        final_response_content = final_response_content.strip()[7:-3].strip()
    elif final_response_content.strip().startswith("```"):
        final_response_content = final_response_content.strip()[3:-3].strip()

    parsed_json = json.loads(final_response_content)

    if recorded_tool_interactions:
        parsed_json["tool_interactions"] = recorded_tool_interactions

    colony_groups_data = parsed_json.get("cfu_analysis", {}).get("colony_groups", [])
    if colony_groups_data:
        shannon_tool_args = {
            "colony_groups": [
                {"morphotype": g["morphotype"], "count": g["count"]}
                for g in colony_groups_data
                if g.get("count", 0) > 0
            ]
        }
        shannon_tool_call = {
            "function": {
                "name": "compute_shannon_index",
                "arguments": json.dumps(shannon_tool_args),
            }
        }
        shannon_response = models.execute_tool_call(shannon_tool_call, image_b64)
        parsed_shannon = json.loads(shannon_response)
        parsed_json["shannon_diversity_index"] = parsed_shannon.get("shannon_index")
        recorded_tool_interactions.append(
            {
                "function_name": "compute_shannon_index",
                "arguments": shannon_tool_args,
                "response": parsed_shannon,
            }
        )

    if "image_id" not in parsed_json or not parsed_json["image_id"]:
        parsed_json["image_id"] = f"img_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    if "analysis_timestamp" not in parsed_json or not parsed_json["analysis_timestamp"]:
        parsed_json["analysis_timestamp"] = datetime.now().isoformat()
    for key in [
        "spatial_distribution_assessment",
        "origin_hypothesis_assessment",
        "swarming_detected",
        "dominant_colony_average_rgb",
    ]:
        if key not in parsed_json:
            parsed_json[key] = None

    return models.BacterialPlateAnalysis(**parsed_json)
