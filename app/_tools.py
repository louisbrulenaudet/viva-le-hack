from app._enums import SpatialDistributionType

tools = [
    {
        "type": "function",
        "function": {
            "name": "analyze_colony_distribution",
            "description": "Detect spatial distribution pattern from the plate image.",
            "parameters": {
                "type": "object",
                "properties": {
                    "image_url": {
                        "type": "string",
                        "description": "The URL of the image to analyze.",
                    },
                    "context_for_distribution": {
                        "type": "string",
                        "description": "Brief context or aspect of distribution to focus on.",
                    },
                },
                "required": ["image_url", "context_for_distribution"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "detect_swarming_behavior",
            "description": "Detect swarming behavior on the plate.",
            "parameters": {
                "type": "object",
                "properties": {
                    "image_url": {
                        "type": "string",
                        "description": "The URL of the image to analyze.",
                    }
                },
                "required": ["image_url"],
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
                    "image_url": {
                        "type": "string",
                        "description": "The URL of the image to analyze.",
                    },
                    "colony_area_description": {
                        "type": "string",
                        "description": "Description of the colony area to analyze.",
                    },
                },
                "required": ["image_url", "colony_area_description"],
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
                    "distribution_type": {
                        "type": "string",
                        "enum": [d.value for d in SpatialDistributionType],
                        "description": "Observed spatial distribution type.",
                    },
                    "morphotype_description": {
                        "type": "string",
                        "description": "Description of dominant colony morphotype.",
                    },
                },
                "required": ["distribution_type", "morphotype_description"],
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
