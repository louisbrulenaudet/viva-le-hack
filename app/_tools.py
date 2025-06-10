from app._enums import ColonyColor, ColonyOriginHypothesis, SpatialDistributionType

tools = [
    {
        "type": "function",
        "function": {
            "name": "analyze_colony_distribution",
            "description": "Detect spatial distribution pattern from the plate image.",
            "parameters": {
                "type": "object",
                "properties": {
                    "distribution": {
                        "type": "string",
                        "enum": [d.value for d in SpatialDistributionType],
                        "description": f"The distribution of colonies on the plate. Can be one of: {', '.join([d.value for d in SpatialDistributionType])}.",
                    },
                },
                "required": ["distribution"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "average_colony_rgb",
            "description": "Get average RGB pigment value of dominant colonies.",
            "parameters": {
                "type": "object",
                "properties": {
                    "color": {
                        "type": "string",
                        "enum": [c.value for c in ColonyColor],
                        "description": "The RGB color value to analyze. Can be  one of: "
                        + ", ".join([c.value for c in ColonyColor]),
                    },
                },
                "required": ["color"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "infer_origin_hypothesis",
            "description": "Suggest origin hypothesis based on distribution and morphotype.",
            "parameters": {
                "type": "object",
                "properties": {
                    "origin": {
                        "type": "string",
                        "enum": [d.value for d in ColonyOriginHypothesis],
                        "description": "Observed colony origin hypothesis. Can be one of: "
                        + ", ".join([d.value for d in ColonyOriginHypothesis]),
                    },
                },
                "required": ["origin"],
            },
        },
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
                                "count": {"type": "integer"},
                            },
                            "required": ["morphotype", "count"],
                        },
                    }
                },
                "required": ["colony_groups"],
            },
        },
    },
]
