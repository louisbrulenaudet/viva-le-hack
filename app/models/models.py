from typing import Any

from pydantic import BaseModel, Field

__all__: list[str] = [
    "Completion",
    "RoutingResponse",
    "AgentExecutionResult",
]


class RoutingResponse(BaseModel):
    types: list[str]
    subtypes: list[str]


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
