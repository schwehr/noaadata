"""Unit tests for structural protocols in ais, nmea, and aisutils."""

from ais.protocols import AISMessageHandler
from aisutils.protocols import DatabaseBridge, GISExporter


class DummyAISDecoder:
    def decode(self, bv, validate=True):
        return {"mmsi": 123456789}

    def encode(self, params, validate=True):
        return None


class DummyDBBridge:
    def sql_create_table(self, outfile, db_type="sqlite", table_name=None):
        pass

    def sql_insert(self, params, outfile, table_name=None):
        pass


class DummyGISExporter:
    def export(self, records, outfile):
        pass


def test_ais_message_handler_protocol():
    decoder = DummyAISDecoder()
    assert isinstance(decoder, AISMessageHandler)


def test_database_bridge_protocol():
    bridge = DummyDBBridge()
    assert isinstance(bridge, DatabaseBridge)


def test_gis_exporter_protocol():
    exporter = DummyGISExporter()
    assert isinstance(exporter, GISExporter)
