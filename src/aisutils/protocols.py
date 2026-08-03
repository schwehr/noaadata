"""Structural Protocols for Database Bridges and GIS Exporters."""

from typing import Any, Protocol, TextIO, runtime_checkable


@runtime_checkable
class DatabaseBridge(Protocol):
    """Protocol for database connection and schema export bridges."""

    def sql_create_table(
        self,
        outfile: TextIO,
        db_type: str = "sqlite",
        table_name: str | None = None,
    ) -> None:
        """Generate SQL CREATE TABLE DDL statements."""
        ...

    def sql_insert(
        self,
        params: dict[str, Any],
        outfile: TextIO,
        table_name: str | None = None,
    ) -> None:
        """Generate SQL INSERT DML statements."""
        ...


@runtime_checkable
class GISExporter(Protocol):
    """Protocol for exporting spatial position data to GIS formats (KML, WKT, GeoJSON)."""

    def export(self, records: list[dict[str, Any]], outfile: TextIO) -> None:
        """Export spatial records to the target GIS format."""
        ...
