import base64
import json
import math
import os
from datetime import datetime
from enum import StrEnum

import openai
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# === OpenAI API Key ===
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise RuntimeError("OPENAI_API_KEY environment variable is not set")

# === ENUMS ===

class SpatialDistributionType(StrEnum):
    ISOLATED = "isolated"
    CLUSTERED = "clustered"
    CONFLUENT = "confluent"
    CENTRALLY_LOCATED = "centrally_located"
    PERIPHERAL = "peripheral"
    EVENLY_DISTRIBUTED = "evenly_distributed"
    RADIAL = "radial"
    SPOT_INOCULATED = "spot_inoculated"
    SWARMING = "swarming"
    ZONAL = "zonal"
    TRAILING = "trailing"
    DISCONTINUOUS = "discontinuous"
    PUNCTATE = "punctate"
    FILAMENTOUS_EDGE = "filamentous_edge"
    SPREADING = "spreading"
    LAYERED = "layered"
    INHIBITION_ZONE = "inhibition_zone"
    BIAXIAL = "biaxial"

class ColonyOriginHypothesis(StrEnum):
    DIRECT_INOCULATION = "direct_inoculation"
    AIRBORNE_CONTAMINATION = "airborne_contamination"
    MOTILE_SPREAD = "motile_spread"
    EDGE_EFFECT = "edge_effect"
    CONTACT_TRANSFER = "contact_transfer"
    LIQUID_OVERSPILL = "liquid_overspill"
    DROPLET_IMPACT = "droplet_impact"
    BIOFILM_FRAGMENT = "biofilm_fragment"
    OVERNIGHT_SWARM = "overnight_swarm"
    ANTIBIOTIC_INHIBITION = "antibiotic_inhibition"
    MIXED_INOCULUM = "mixed_inoculum"
    RESIDUAL_MEDIA_EFFECT = "residual_media_effect"
    CONDENSATION_ARTIFACT = "condensation_artifact"
    FUNGAL_OVERGROWTH = "fungal_overgrowth"
    TECHNICAL_ERROR = "technical_error"

# === Tools for Function Calling ===

tools = [
    {
        "type": "function",
        "function": {
            "name": "analyze_colony_distribution",
            "description": "Detect spatial distribution pattern from the plate image.",
            "parameters": {
                "type": "object",
                "properties": {
                    "image_url": {"type": "string", "description": "The URL of the image to analyze."},
                    "context_for_distribution": {"type": "string", "description": "Brief context or aspect of distribution to focus on."}
                },
                "required": ["image_url", "context_for_distribution"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "detect_swarming_behavior",
            "description": "Detect swarming behavior on the plate.",
            "parameters": {
                "type": "object",
                "properties": {
                    "image_url": {"type": "string", "description": "The URL of the image to analyze."}
                },
                "required": ["image_url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "average_colony_rgb",
            "description": "Get average RGB pigment value of dominant colonies.",
            "parameters": {
                "type": "object",
                "properties": {
                    "image_url": {"type": "string", "description": "The URL of the image to analyze."},
                    "colony_area_description": {"type": "string", "description": "Description of the colony area to analyze."}
                },
                "required": ["image_url", "colony_area_description"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "infer_origin_hypothesis",
            "description": "Suggest origin hypothesis based on distribution and morphotype.",
            "parameters": {
                "type": "object",
                "properties": {
                    "distribution_type": {
                        "type": "string",
                        "enum": [d.value for d in SpatialDistributionType],
                        "description": "Observed spatial distribution type."
                    },
                    "morphotype_description": {
                        "type": "string",
                        "description": "Description of dominant colony morphotype."
                    }
                },
                "required": ["distribution_type", "morphotype_description"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "compute_shannon_index",
            "description": "Calculate the Shannon diversity index from colony group distribution.",
            "parameters": {
                "type": "object",
                "properties": {
                    "colony_groups": {
                        "type": "array",
                        "description": "List of colony groups with counts.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "morphotype": {"type": "string"},
                                "count": {"type": "integer"}
                            },
                            "required": ["morphotype", "count"]
                        }
                    }
                },
                "required": ["colony_groups"]
            }
        }
    }
]

# === Pydantic Models ===

class ColonyGroup(BaseModel):
    morphotype: str
    count: int
    probable_identity: str | None = None
    pigment: str | None = None
    diameter_range_mm: tuple[float, float] | None = None

class SampleInfo(BaseModel):
    substrate: str
    origin: str
    incubation_hours: int
    camera_distance_cm: float

class CFUAnalysis(BaseModel):
    estimated_total_cfu: int
    cfu_per_ml: float | None = None
    detection_confidence: float
    colony_groups: list[ColonyGroup] = Field(default_factory=list)

class ReportQuality(BaseModel):
    image_quality_score: float
    lighting_conditions: str
    detection_completeness: str

class Metadata(BaseModel):
    model_version: str
    processed_by: str
    review_recommended: bool

class BacterialPlateAnalysis(BaseModel):
    image_id: str
    analysis_timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    sample_info: SampleInfo
    cfu_analysis: CFUAnalysis
    diagnostic_hint: str
    report_quality: ReportQuality
    metadata: Metadata
    spatial_distribution_assessment: SpatialDistributionType | None = None
    origin_hypothesis_assessment: ColonyOriginHypothesis | None = None
    swarming_detected: bool | None = None
    dominant_colony_average_rgb: tuple[int, int, int] | None = None
    shannon_diversity_index: float | None = None
    tool_interactions: list[dict] | None = None

# === FastAPI Setup ===

app = FastAPI(title="Bacterial Analysis API with Function Calling", version="1.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Tool Functions ===

def analyze_colony_distribution(
    image_url: str, context_for_distribution: str
) -> str:
    """Mock analysis of colony distribution on a plate image."""
    determined_distribution = SpatialDistributionType.CLUSTERED
    return json.dumps(
        {
            "image_url_processed": image_url,
            "distribution_type": determined_distribution.value,
            "comment": f"Distribution assessed as {determined_distribution.value}",
        }
    )


def detect_swarming_behavior(image_url: str) -> str:
    """Mock detection of swarming behavior."""
    return json.dumps(
        {
            "image_url_processed": image_url,
            "is_swarming": True,
            "confidence": 0.85,
        }
    )


def average_colony_rgb(image_url: str, colony_area_description: str) -> str:
    """Return a mocked average RGB value for colonies on the plate."""
    avg_rgb = (210, 180, 140)
    return json.dumps(
        {
            "image_url_processed": image_url,
            "colony_area_analyzed": colony_area_description,
            "average_rgb": avg_rgb,
        }
    )


def infer_origin_hypothesis(
    distribution_type: str, morphotype_description: str
) -> str:
    """Infer colony origin hypothesis from distribution and morphotype."""
    hypothesis = ColonyOriginHypothesis.DIRECT_INOCULATION
    if (
        distribution_type == SpatialDistributionType.CLUSTERED
        and "mucoid" in morphotype_description
    ):
        hypothesis = ColonyOriginHypothesis.MIXED_INOCULUM
    return json.dumps(
        {
            "distribution_input": distribution_type,
            "morphotype_input": morphotype_description,
            "origin_hypothesis": hypothesis.value,
        }
    )


def compute_shannon_index(colony_groups: list[dict]) -> str:
    """Compute Shannon diversity index from colony groups."""
    total = sum(group.get("count", 0) for group in colony_groups)
    if total == 0:
        shannon_index = 0.0
    else:
        shannon_index = -sum(
            (group["count"] / total) * math.log(group["count"] / total)
            for group in colony_groups
            if group.get("count", 0) > 0
        )
    return json.dumps(
        {
            "shannon_index": round(shannon_index, 4),
            "total_colonies": total,
            "group_count": len(colony_groups),
        }
    )

# === Tool Execution Logic (Mocked) ===

def execute_tool_call(tool_call, image_url):
    function_name = tool_call["function"]["name"]
    function_args = json.loads(tool_call["function"]["arguments"])

    if function_name == "analyze_colony_distribution":
        return analyze_colony_distribution(
            function_args.get("image_url"),
            function_args.get("context_for_distribution"),
        )
    elif function_name == "detect_swarming_behavior":
        return detect_swarming_behavior(function_args.get("image_url"))
    elif function_name == "average_colony_rgb":
        return average_colony_rgb(
            function_args.get("image_url"),
            function_args.get("colony_area_description"),
        )
    elif function_name == "infer_origin_hypothesis":
        return infer_origin_hypothesis(
            function_args.get("distribution_type"),
            function_args.get("morphotype_description"),
        )
    elif function_name == "compute_shannon_index":
        return compute_shannon_index(function_args.get("colony_groups", []))
    else:
        return json.dumps({"error": "Unknown function", "function_name": function_name})

# === Endpoint ===

@app.post("/analyze", response_model=BacterialPlateAnalysis)
async def analyze_image_endpoint(file: UploadFile = File(...)):
    image_bytes = await file.read()
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
    image_url = f"data:image/jpeg;base64,{image_b64}"

    schema_fields = BacterialPlateAnalysis.model_json_schema()["properties"].keys()
    schema_description = "\n".join(
        [f"- {field}: {BacterialPlateAnalysis.model_fields[field].description or 'provide value'}"
         for field in schema_fields if field != "tool_interactions"]
    )

    prompt_text = (
        "You are an expert microbiologist analyzing an agar plate image. "
        "Provide a comprehensive analysis in JSON format according to the following schema. "
        "Use tools if needed. Final response must be a single JSON object.\n\n"
        f"Schema:\n{schema_description}"
    )

    messages = [{
        "role": "user",
        "content": [
            {"type": "text", "text": prompt_text},
            {"type": "image_url", "image_url": {"url": image_url}}
        ]
    }]

    try:
        response = openai.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=messages,
            tools=tools,
            tool_choice="auto",
            max_tokens=2000,
            temperature=0.2
        )
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        recorded_tool_interactions = []

        if tool_calls:
            messages.append(response_message)
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_response_content = execute_tool_call(tool_call, image_url)
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response_content,
                })
                recorded_tool_interactions.append({
                    "tool_call_id": tool_call.id,
                    "function_name": function_name,
                    "arguments": json.loads(tool_call.function.arguments),
                    "response": json.loads(function_response_content)
                })

            second_response = openai.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=messages,
                max_tokens=2000,
                temperature=0.2
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

        # Shannon Index Tool Call (manual trigger)
        colony_groups_data = parsed_json.get("cfu_analysis", {}).get("colony_groups", [])
        if colony_groups_data:
            shannon_tool_args = {"colony_groups": [
                {"morphotype": g["morphotype"], "count": g["count"]}
                for g in colony_groups_data if g.get("count", 0) > 0
            ]}
            shannon_tool_call = {"function": {"name": "compute_shannon_index", "arguments": json.dumps(shannon_tool_args)}}
            shannon_response = execute_tool_call(shannon_tool_call, image_url)
            parsed_shannon = json.loads(shannon_response)
            parsed_json["shannon_diversity_index"] = parsed_shannon.get("shannon_index")
            recorded_tool_interactions.append({
                "function_name": "compute_shannon_index",
                "arguments": shannon_tool_args,
                "response": parsed_shannon
            })

        if "image_id" not in parsed_json or not parsed_json["image_id"]:
            parsed_json["image_id"] = f"img_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        if "analysis_timestamp" not in parsed_json or not parsed_json["analysis_timestamp"]:
            parsed_json["analysis_timestamp"] = datetime.now().isoformat()
        for key in ["spatial_distribution_assessment", "origin_hypothesis_assessment", "swarming_detected", "dominant_colony_average_rgb"]:
            if key not in parsed_json:
                parsed_json[key] = None

        return BacterialPlateAnalysis(**parsed_json)

    except json.JSONDecodeError as e:
        return JSONResponse(status_code=500, content={"error": f"Failed to parse JSON: {e}", "raw_gpt_output": final_response_content})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI server with Uvicorn on http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)