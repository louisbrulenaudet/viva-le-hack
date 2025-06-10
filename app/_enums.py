import enum

__all__: list[str] = [
    "ImageMimeTypes",
    "Models",
    "ErrorCodes",
    "ObjectTypes",
    "Callbacks",
    "DBTableNames",
]


class ImageMimeTypes(enum.StrEnum):
    JPEG = "image/jpeg"
    PNG = "image/png"


class Actions(enum.StrEnum):
    TOOL = "tool"
    CALLBACK = "callback"


class Callbacks(enum.StrEnum):
    REVIEW = "review"
    DB = "db"
    BUCKET = "bucket"


class Models(enum.StrEnum):
    GPT_4_1_MINI = "gpt-4.1-mini"


class SpatialDistributionType(enum.StrEnum):
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


class ColonyOriginHypothesis(enum.StrEnum):
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


class ErrorCodes(enum.StrEnum):
    COMPLETION_ERROR = "COMPLETION_ERROR"
    TOOL_REGISTRY_NOT_FOUND = "TOOL_REGISTRY_NOT_FOUND"
    TOOL_CONFIGURATION_ERROR = "TOOL_CONFIGURATION_ERROR"
    TOOL_INITIALIZATION_ERROR = "TOOL_INITIALIZATION_ERROR"
    TOOL_EXECUTION_ERROR = "TOOL_EXECUTION_ERROR"
    SYSTEM_PROMPT_ERROR = "SYSTEM_PROMPT_ERROR"
    MCP_DATABASE_INITIALIZATION_ERROR = "MCP_DATABASE_INITIALIZATION_ERROR"
    CLIENT_INITIALIZATION_ERROR = "CLIENT_INITIALIZATION_ERROR"


class ObjectTypes(enum.StrEnum):
    LIST = "list"


class DBTableNames(enum.StrEnum):
    TEAM = "team"


class EmailContents(enum.StrEnum):
    REVIEW_REQUEST = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Review Request</title>
</head>
<body>
    <div class="container">
        <h2>Review Request</h2>
        <p>Hello,</p>
        <div class="content">
            <p>We are reaching out to request your review of a recent submission. Your feedback is highly valued and helps us maintain our standards of excellence.</p>
            <div>
                {data}
            </div>
            <p>If you have any questions or need further information, please let us know.</p>
        </div>
        <div class="footer">
            Best regards,<br>
            The Team
        </div>
    </div>
</body>
</html>
"""
