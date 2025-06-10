from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app._enums import (
    Actions,
    Callbacks,
    ColonyOriginHypothesis,
    SpatialDistributionType,
)

__all__: list[str] = [
    "Completion",
    "SignDetector",
    "CallBackExecutionResult",
    "FilterElement",
    "Join",
    "QueryFilter",
]


class Completion(BaseModel):
    data: str | list[Any] | dict[str, Any] | None = Field(
        default=None,
        description="The generated content from the model, which can be text or structured data.",
    )


class CallBackExecutionResult(BaseModel):
    data: str | list[Any] | dict[str, Any] | None = Field(
        default=None,
        description="The result data produced by the callback.",
    )


class FilterElement(BaseModel):
    field: str
    operator: str
    value: str | int | float | bool | None | list[str | int | float | bool | None]


class Join(BaseModel):
    table: str
    alias: str | None = None
    join_type: str = "INNER"
    on: list[FilterElement]


class QueryFilter(BaseModel):
    base_table: str
    base_alias: str | None = None
    fields: list[str] | None = Field(default_factory=lambda: ["*"])
    filters: list[FilterElement] = Field(default_factory=list)
    joins: list[Join] = Field(default_factory=list)
    order_by: str | None = None
    limit: int | None = None
    distinct: bool = False
    group_by: list[str] = Field(default_factory=list)


class SignDetector(BaseModel):
    """Model returned by the SignDetector prompt."""

    type: Actions = Field(description="Type of the detected object: callback or tools")
    name: Callbacks = Field(description="First line inside the shape")
    parameters: dict[str, str] = Field(
        default_factory=dict, description="Key/value pairs from the remaining lines"
    )


class SignDetectors(BaseModel):
    signs: list[SignDetector]


class AnalysisResult(BaseModel):
    analysis: dict


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
