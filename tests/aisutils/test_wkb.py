"""Unit tests for WKB conversion utilities in aisutils.wkb."""

from unittest.mock import MagicMock

import pytest

from aisutils import wkb


def test_wkb_module_metadata() -> None:
    """Test module metadata attributes."""
    assert hasattr(wkb, "__author__")
    assert hasattr(wkb, "__version__")
    assert hasattr(wkb, "__revision__")
    assert hasattr(wkb, "__date__")
    assert hasattr(wkb, "__copyright__")
    assert hasattr(wkb, "__license__")
    assert wkb.__license__ == "Apache 2.0"


def test_convert_without_geotypes(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test convert class when GeoTypes module is missing."""
    monkeypatch.setattr(wkb, "GeoTypes", None)
    with pytest.raises(ImportError, match="GeoTypes module is not available"):
        wkb.convert()

    # Test decode direct call scenario if instance existed
    instance = object.__new__(wkb.convert)
    with pytest.raises(ImportError, match="GeoTypes module is not available"):
        instance.decode("0020000001000010E6C051D30925D1DA0B4044A79AE924F228")


def test_convert_init_and_decode(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test convert initialization and decoding with mocked GeoTypes."""
    mock_factory_instance = MagicMock()
    mock_parser_instance = MagicMock()
    mock_geometry = MagicMock()

    mock_factory_cls = MagicMock(return_value=mock_factory_instance)
    mock_parser_cls = MagicMock(return_value=mock_parser_instance)
    mock_factory_instance.getGeometry.return_value = mock_geometry

    mock_geotypes = MagicMock()
    mock_geotypes.OGGeoTypeFactory = mock_factory_cls
    mock_geotypes.HEXEWKBParser = mock_parser_cls

    monkeypatch.setattr(wkb, "GeoTypes", mock_geotypes)

    converter = wkb.convert()

    mock_factory_cls.assert_called_once()
    mock_parser_cls.assert_called_once_with(mock_factory_instance)

    sample_wkbhex = "0020000001000010E6C051D30925D1DA0B4044A79AE924F228"
    result = converter.decode(sample_wkbhex)

    mock_parser_instance.parseGeometry.assert_called_once_with(sample_wkbhex)
    mock_factory_instance.getGeometry.assert_called_once()
    assert result == mock_geometry


def test_convert_decode_multiple_calls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test multiple decode calls on the same convert instance."""
    mock_factory_instance = MagicMock()
    mock_parser_instance = MagicMock()
    geom1 = MagicMock(name="geom1")
    geom2 = MagicMock(name="geom2")
    mock_factory_instance.getGeometry.side_effect = [geom1, geom2]

    mock_geotypes = MagicMock()
    mock_geotypes.OGGeoTypeFactory.return_value = mock_factory_instance
    mock_geotypes.HEXEWKBParser.return_value = mock_parser_instance

    monkeypatch.setattr(wkb, "GeoTypes", mock_geotypes)

    converter = wkb.convert()

    hex1 = "0020000001000010E6C051D30925D1DA0B4044A79AE924F228"
    hex2 = "0101000000000000000000F03F0000000000000040"

    res1 = converter.decode(hex1)
    res2 = converter.decode(hex2)

    assert res1 == geom1
    assert res2 == geom2
    mock_parser_instance.parseGeometry.assert_any_call(hex1)
    mock_parser_instance.parseGeometry.assert_any_call(hex2)


def test_convert_decode_error_propagation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that decode propagates parser exceptions properly."""
    mock_factory_instance = MagicMock()
    mock_parser_instance = MagicMock()
    mock_parser_instance.parseGeometry.side_effect = ValueError("Invalid WKB Hex")

    mock_geotypes = MagicMock()
    mock_geotypes.OGGeoTypeFactory.return_value = mock_factory_instance
    mock_geotypes.HEXEWKBParser.return_value = mock_parser_instance

    monkeypatch.setattr(wkb, "GeoTypes", mock_geotypes)

    converter = wkb.convert()
    with pytest.raises(ValueError, match="Invalid WKB Hex"):
        converter.decode("INVALID_HEX")
