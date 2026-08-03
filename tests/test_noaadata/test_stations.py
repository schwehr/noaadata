"""Unit tests for NOAA CO-OPS station parsing utilities."""

from noaadata import stations


def test_lonlat_text_to_decimal_north() -> None:
    val = stations.lonlatText2decimal("21 57.3 N")
    assert abs(val - 21.955) < 1e-4


def test_lonlat_text_to_decimal_west() -> None:
    val = stations.lonlatText2decimal("159 21.4 W")
    assert abs(val - (-159.3566666)) < 1e-4


def test_strip_namespaces() -> None:
    xml_input = '<test xmlns="http://example.com" XMLSchema-instance" rest>data</test>'
    result = stations.stripNameSpaces(xml_input)
    assert "xmlns" not in result
