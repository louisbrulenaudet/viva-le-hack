from __future__ import annotations

from typing import Any

from app.core.config import settings
from app.models.models import QueryFilter
from app.utils.sql import SQLiteSQLGenerator

__all__ = ["levenshtein_distance", "fuzzy_find_team_member"]


def levenshtein_distance(a: str, b: str) -> int:
    """Compute Levenshtein distance between two strings."""
    if a == b:
        return 0
    if len(a) < len(b):
        a, b = b, a
    previous_row = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        current_row = [i]
        for j, cb in enumerate(b, start=1):
            insertions = previous_row[j] + 1
            deletions = current_row[j - 1] + 1
            substitutions = previous_row[j - 1] + (ca != cb)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]


def fuzzy_find_team_member(name: str) -> dict[str, Any] | None:
    """Return the team member whose username best matches ``name``."""
    if settings.cloudflare_client is None:
        raise RuntimeError("Cloudflare client is not configured")

    query = QueryFilter(base_table="team", fields=["username", "email"])
    results = (
        settings.cloudflare_client.d1.database.query(
            database_id=settings.cloudflare_db_id,
            account_id=settings.cloudflare_account_id,
            sql=SQLiteSQLGenerator.compile(query),
        )
        .result[0]
        .results
    )

    best_match: dict[str, Any] | None = None
    best_distance = float("inf")

    for row in results:
        username = row.get("username", "")
        distance = levenshtein_distance(name, username)
        if distance < best_distance:
            best_distance = distance
            best_match = row
    return best_match
