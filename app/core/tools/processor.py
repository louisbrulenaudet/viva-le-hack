import json

from app.core.tools import (
    analyze_colony_distribution,
    average_colony_rgb,
    compute_shannon_index,
    detect_swarming_behavior,
    infer_origin_hypothesis,
)


class ToolProcessor:
    @staticmethod
    def execute_tool_call(tool_call: dict[str, object], image_url: str) -> object:
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
            return json.dumps(
                {"error": "Unknown function", "function_name": function_name}
            )
