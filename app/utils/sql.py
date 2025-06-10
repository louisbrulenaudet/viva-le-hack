import re

from app.models.models import FilterElement, QueryFilter

__all__: list[str] = [
    "SQLiteSQLGenerator",
]


class SQLiteSQLGenerator:
    """
    SQL query builder targeting SQLite dialect.
    Converts strongly typed QueryFilter objects to validated SQL statements.
    """

    @staticmethod
    def quote_identifier(identifier: str) -> str:
        """
        Escapes and quotes SQL identifiers to prevent injection.

        Args:
            identifier (str): A column or table name.

        Returns:
            str: A safely quoted identifier.
        """
        if not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", identifier):
            raise ValueError(f"Unsafe identifier: {identifier}")
        return f'"{identifier}"'

    @staticmethod
    def qualify(field: str, default_table: str | None) -> str:
        """
        Qualify field with its table name unless already qualified.

        Args:
            field (str): Field name, optionally with dot notation.
            default_table (Optional[str]): Table or alias to prefix if needed.

        Returns:
            str: Fully qualified field.
        """
        if "." in field:
            table, col = field.split(".", 1)
            return f"{SQLiteSQLGenerator.quote_identifier(table)}.{SQLiteSQLGenerator.quote_identifier(col)}"
        elif default_table:
            return f"{SQLiteSQLGenerator.quote_identifier(default_table)}.{SQLiteSQLGenerator.quote_identifier(field)}"
        else:
            return SQLiteSQLGenerator.quote_identifier(field)

    @staticmethod
    def format_literal(
        value: str | int | float | bool | None | list[str | int | float | bool | None],
    ) -> str:
        """
        Formats Python values into SQL literals.

        Args:
            value: The value to format (None, bool, str, int, float, list).

        Returns:
            str: SQL-safe literal.
        """
        if value is None:
            return "NULL"
        elif isinstance(value, bool):
            return "1" if value else "0"
        elif isinstance(value, int | float):
            return str(value)
        elif isinstance(value, str):
            return "'" + value.replace("'", "''") + "'"
        else:
            raise ValueError(f"Unsupported literal: {value}")

    @staticmethod
    def compile_filter(f: FilterElement, default_table: str | None) -> str:
        """
        Compiles a FilterElement to a SQL WHERE or ON clause.

        Args:
            f (FilterElement): Filter specification.
            default_table (Optional[str]): Table/alias for unqualified fields.

        Returns:
            str: SQL condition expression.
        """
        field = SQLiteSQLGenerator.qualify(f.field, default_table)
        op = f.operator.upper()
        val = f.value

        if op == "IN":
            if not isinstance(val, list):
                raise ValueError("IN operator requires a list value.")
            formatted = ", ".join(SQLiteSQLGenerator.format_literal(v) for v in val)
            return f"{field} IN ({formatted})"

        elif val is None:
            if op in ("=", "IS"):
                return f"{field} IS NULL"
            elif op in ("!=", "<>", "IS NOT"):
                return f"{field} IS NOT NULL"
            else:
                raise ValueError(f"NULL used with unsupported operator: {op}")

        elif op in {"=", "!=", "<>", ">", "<", ">=", "<=", "LIKE"}:
            return f"{field} {op} {SQLiteSQLGenerator.format_literal(val)}"

        else:
            raise ValueError(f"Unsupported operator: {op}")

    @staticmethod
    def compile(query: QueryFilter) -> str:
        """
        Compiles a full SQL SELECT query from a QueryFilter instance.

        Args:
            query (QueryFilter): Query definition.

        Returns:
            str: A fully rendered SQL SELECT statement.
        """
        base = SQLiteSQLGenerator.quote_identifier(query.base_table)
        base_alias = (
            SQLiteSQLGenerator.quote_identifier(query.base_alias)
            if query.base_alias
            else base
        )
        from_clause = f"{base} AS {base_alias}" if query.base_alias else base

        join_clauses = []
        for join in query.joins:
            join_table = SQLiteSQLGenerator.quote_identifier(join.table)
            join_alias = (
                SQLiteSQLGenerator.quote_identifier(join.alias)
                if join.alias
                else join_table
            )
            join_type = join.join_type.upper()
            if join_type not in {"INNER", "LEFT"}:
                raise ValueError(f"Unsupported join type: {join_type}")
            on_clause = " AND ".join(
                SQLiteSQLGenerator.compile_filter(f, join.alias or join.table)
                for f in join.on
            )
            join_clauses.append(
                f"{join_type} JOIN {join_table} AS {join_alias} ON {on_clause}"
            )

        fields = ", ".join(
            SQLiteSQLGenerator.qualify(f, query.base_alias or query.base_table)
            if "." not in f
            else SQLiteSQLGenerator.qualify(f, None)
            for f in query.fields  # type: ignore
        )

        select_clause = "SELECT DISTINCT" if query.distinct else "SELECT"
        sql = f"{select_clause} {fields} FROM {from_clause}"

        if join_clauses:
            sql += " " + " ".join(join_clauses)

        if query.filters:
            where_clause = " AND ".join(
                SQLiteSQLGenerator.compile_filter(
                    f, query.base_alias or query.base_table
                )
                for f in query.filters
            )
            sql += f" WHERE {where_clause}"

        if query.group_by:
            grouped_fields = ", ".join(
                SQLiteSQLGenerator.qualify(f, None) for f in query.group_by
            )
            sql += f" GROUP BY {grouped_fields}"

        if query.order_by:
            sql += f" ORDER BY {SQLiteSQLGenerator.qualify(query.order_by, None)}"

        if query.limit is not None:
            sql += f" LIMIT {int(query.limit)}"

        return sql + ";"
