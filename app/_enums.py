import enum

from app.models.models import QueryFilter

__all__: list[str] = [
    "ImageMimeTypes",
    "Models",
    "ErrorCodes",
    "ObjectTypes",
    "Callbacks",
    "DBTableNames",
    "MCPDescriptions",
]


class ImageMimeTypes(enum.StrEnum):
    JPEG = "image/jpeg"
    PNG = "image/png"


class Callbacks(enum.StrEnum):
    REVIEW = "review"
    DB = "db"
    BUCKET = "bucket"


class Models(enum.StrEnum):
    GPT_4_TURBO = "gpt-4-turbo"


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


class MCPDescriptions(enum.StrEnum):
    QUERY_DB = f"""Query the Cloudflare D1 database and return data as a string. Use this tool after getting the list of tables or schema. The request should adhere to the pydantic schema below. {QueryFilter.model_json_schema()}"""
    GET_DATABASE_TABLES = """Get the list of tables in the Cloudflare D1 database. Use this tool before querying the database."""
    GET_DATABASE_SCHEMA = """Get the schema of a specific table in the Cloudflare D1 database. Use this tool before querying the database."""


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
