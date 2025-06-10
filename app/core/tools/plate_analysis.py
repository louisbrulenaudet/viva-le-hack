import json
import math

__all__: list[str] = [
    "analyze_colony_distribution",
    "average_colony_rgb",
    "infer_origin_hypothesis",
    "compute_shannon_index",
]


def analyze_colony_distribution(distribution: str) -> str:
    """Mock analysis of colony distribution on a plate image."""
    return json.dumps({"distribution": distribution.value})


def average_colony_rgb(color: str) -> str:
    """Return a mocked average RGB value for colonies on the plate."""
    return json.dumps(
        {
            "color": color,
        }
    )


def infer_origin_hypothesis(origin: str) -> str:
    """Infer colony origin hypothesis from distribution and morphotype."""
    return json.dumps(
        {
            "origin_hypothesis": origin.value,
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
