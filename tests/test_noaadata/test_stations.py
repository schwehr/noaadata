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


def test_station_initialization() -> None:
    from lxml import etree

    xml_str = """
    <station name="Test Station" ID="123456">
        <metadata>
            <location>
                <lat>21 57.3 N</lat>
                <long>159 21.4 W</long>
                <state>HI</state>
            </location>
        </metadata>
        <parameter name="Water Level" sensorID="A1" DCP="1" status="1"/>
        <parameter name="Air Temp" sensorID="A2" DCP="2" status="0"/>
    </station>
    """
    root = etree.fromstring(xml_str)
    station = stations.Station(root)

    assert station.getName() == "Test Station"
    assert station.getID() == "123456"
    assert abs(station.getLat() - 21.955) < 1e-4
    assert abs(station.getLon() - (-159.3566666)) < 1e-4
    assert station.fields["state"] == "HI"

    assert len(station.parameters) == 2
    assert station.parameters[0]["name"] == "Water Level"
    assert station.parameters[0]["status"] is True
    assert station.parameters[1]["name"] == "Air Temp"
    assert station.parameters[1]["status"] is False


def test_station_has_sensor() -> None:
    from lxml import etree

    xml_str = """
    <station name="Test Station" ID="123456">
        <metadata>
            <location>
                <lat>21 57.3 N</lat>
                <long>159 21.4 W</long>
                <state>HI</state>
            </location>
        </metadata>
        <parameter name="Water Level" sensorID="A1" DCP="1" status="1"/>
        <parameter name="Air Temp" sensorID="A2" DCP="2" status="0"/>
    </station>
    """
    root = etree.fromstring(xml_str)
    station = stations.Station(root)

    assert station.hasSensor("Water Level") is True
    assert station.hasSensor("Water Level", status=True) is True
    assert station.hasSensor("Water Level", status=False) is False
    assert station.hasSensor("Water Level", sensorID="A1") is True
    assert station.hasSensor("Water Level", sensorID="A2") is False
    assert station.hasSensor("Water Level", DCP="1") is True
    assert station.hasSensor("Water Level", DCP="2") is False

    assert station.hasSensor("Air Temp", status=None) is True
    assert station.hasSensor("Air Temp", status=False) is True
    assert station.hasSensor("Air Temp", status=True) is False

    assert station.hasSensor("Wind Speed") is False
    assert station.hasSensor(sensorID="A1") is True
    assert station.hasSensor(sensorID="X1") is False
