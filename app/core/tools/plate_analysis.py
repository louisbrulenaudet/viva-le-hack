import json
import math

from app._enums import ColonyOriginHypothesis, SpatialDistributionType

__all__: list[str] = [
    "analyze_colony_distribution",
    "detect_swarming_behavior",
    "average_colony_rgb",
    "infer_origin_hypothesis",
    "compute_shannon_index",
]


def analyze_colony_distribution(image_url: str, context_for_distribution: str) -> str:
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


def infer_origin_hypothesis(distribution_type: str, morphotype_description: str) -> str:
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
