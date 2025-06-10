import enum

from app.models.models import QueryFilter

__all__: list[str] = [
    "MCPDescriptions",
]


class MCPDescriptions(enum.StrEnum):
    QUERY_DB = f"""Query the Cloudflare D1 database and return data as a string. Use this tool after getting the list of tables or schema. The request should adhere to the pydantic schema below. {QueryFilter.model_json_schema()}"""
    GET_DATABASE_TABLES = """Get the list of tables in the Cloudflare D1 database. Use this tool before querying the database."""
    GET_DATABASE_SCHEMA = """Get the schema of a specific table in the Cloudflare D1 database. Use this tool before querying the database."""
