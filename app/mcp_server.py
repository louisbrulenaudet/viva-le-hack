from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Annotated

from cloudflare import Cloudflare
from mcp.server.fastmcp import FastMCP
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app._enums import DBTableNames, MCPDescriptions
from app._exceptions import MCPDatabaseInitializationError
from app.models.models import QueryFilter
from app.utils.sql import SQLiteSQLGenerator


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="allow")

    cloudflare_api_token: str | None = Field(alias="CLOUDFLARE_API_TOKEN")
    cloudflare_db_id: str | None = Field(alias="CLOUDFLARE_DB_ID")
    cloudflare_account_id: str | None = Field(alias="CLOUDFLARE_ACCOUNT_ID")


settings: Settings = Settings()  # type: ignore

mcp: FastMCP = FastMCP("Labs", dependencies=["cloudflare"])


@dataclass
class AppContext:
    db: any  # type: ignore


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle with type-safe context"""
    client: Cloudflare = Cloudflare(
        api_token=settings.cloudflare_api_token,
    )
    try:
        yield AppContext(db=client)
    except Exception as e:
        raise MCPDatabaseInitializationError(details=str(e)) from e


mcp = FastMCP("MCP server for labs", lifespan=app_lifespan)


@mcp.tool(
    description=MCPDescriptions.QUERY_DB,
)
def query_db(
    query: Annotated[
        QueryFilter,
        Field(description="The SQLite query to execute on the Cloudflare D1 database"),
    ],
) -> str:
    """Tool to query the Cloudflare D1 database and return data as a string.

    Args:
        query (QueryFilter): The SQLite query to execute on the Cloudflare D1 database.

    Returns:
        str: The results of the query formatted as a string.
    """
    ctx = mcp.get_context()
    db = ctx.request_context.lifespan_context.db  # type: ignore

    results = (
        db.d1.database.query(
            database_id=settings.cloudflare_db_id,
            account_id=settings.cloudflare_account_id,
            sql=SQLiteSQLGenerator.compile(query),
        )
        .result[0]
        .results
    )

    results_str: str = ""

    for row in results:
        row_data: str = ", ".join(f"{key}: {value}" for key, value in row.items())
        results_str += f"{row_data}\n"

    return results_str.strip()


@mcp.tool(
    description=MCPDescriptions.GET_DATABASE_TABLES,
)
def get_database_tables() -> str:
    """Tool to get the list of tables in the Cloudflare D1 database. This tool should be used before every other database query."""
    ctx = mcp.get_context()
    db = ctx.request_context.lifespan_context.db  # type: ignore

    tables = (
        db.d1.database.query(
            database_id=settings.cloudflare_db_id,
            account_id=settings.cloudflare_account_id,
            sql="""SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name;""",
        )
        .result[0]
        .results
    )

    table_list = [table["name"] for table in tables]

    return ", ".join(table_list)


@mcp.tool(
    description=MCPDescriptions.GET_DATABASE_SCHEMA,
)
def get_database_schema(
    table_name: Annotated[
        DBTableNames, Field(description="The name of the table to get the schema for")
    ],
) -> str:
    """Tool to get the schema of the Cloudflare D1 database. This tool should be used before every other database query."""
    ctx = mcp.get_context()
    db = ctx.request_context.lifespan_context.db  # type: ignore

    schema = (
        db.d1.database.query(
            database_id=settings.cloudflare_db_id,
            account_id=settings.cloudflare_account_id,
            sql=f"""PRAGMA table_info({table_name});""",
        )
        .result[0]
        .results
    )

    return str(schema)


# Run the server
if __name__ == "__main__":
    mcp.run(transport="stdio")
