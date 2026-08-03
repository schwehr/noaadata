"""Unit tests for SQL query builder utilities."""

from aisutils import sqlhelp


def test_sec2timestamp() -> None:
    timestamp = sqlhelp.sec2timestamp(1169703371)
    assert timestamp == "2007-01-25 05:36:11"


def test_select_query_builder() -> None:
    q = sqlhelp.select(dbType="postgres")
    q.addfield("MMSI")
    q.addfrom("position_reports")
    q.addwhere("mmsi = 366998390")
    q.setlimit(10)

    sql_str = str(q)
    assert "SELECT mmsi" in sql_str
    assert "FROM position_reports" in sql_str
    assert "WHERE mmsi = 366998390" in sql_str
    assert "LIMIT 10;" in sql_str
