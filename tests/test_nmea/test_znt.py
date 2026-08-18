import io
import time
from unittest import mock

import pytest

from nmea import znt
from nmea.nmea_error import NmeaChecksumError


def test_checksum_str():
    # Valid ZNT string checksum check
    nmea_str = "$PNTZNT,1270567048.57,127.0.0.1,17.151.16.21,4,1270565749.41,0.000080,-20,0.117325,0.046249*14"
    assert znt.checksum_str(nmea_str) == "14"

    # Another standard checksum
    assert (
        znt.checksum_str(
            "$GPRMC,173011.82,V,4222.8770,N,07103.0096,W,0.00,0.0,151008,14.9,W,N*27"
        )
        == "27"
    )


def test_make_float():
    d = {"val": "1.23", "otherval": "4.56"}
    znt.make_float(d, "val")
    assert d["val"] == 1.23
    assert d["otherval"] == "4.56"


def test_znt_decode_success():
    nmea_str = "$PNTZNT,1270567048.57,127.0.0.1,17.151.16.21,4,1270565749.41,0.000080,-20,0.117325,0.046249*14"
    z = znt.Znt(nmea_str=nmea_str)
    assert z.params["talker"] == "NT"
    assert z.params["nmea_type"] == "ZNT"
    assert z.params["timestamp"] == 1270567048.57
    assert z.params["host"] == "127.0.0.1"
    assert z.params["ref_clock"] == "17.151.16.21"
    assert z.params["stratum"] == 4
    assert z.params["last_update"] == 1270565749.41
    assert z.params["offset"] == 0.000080
    assert z.params["precision"] == -20.0
    assert z.params["root_delay"] == 0.117325
    assert z.params["root_dispersion"] == 0.046249
    assert z.params["checksum"] == "14"


def test_znt_decode_invalid_checksum():
    nmea_str = "$PNTZNT,1270567048.57,127.0.0.1,17.151.16.21,4,1270565749.41,0.000080,-20,0.117325,0.046249*15"
    with pytest.raises(NmeaChecksumError) as exc:
        znt.Znt(nmea_str=nmea_str)
    assert 'Got "15", expected "14"' in str(exc.value)


def test_znt_decode_not_znt():
    nmea_str = "$GPRMC,173011.82,V,4222.8770,N,07103.0096,W,0.00,0.0,151008,14.9,W,N*27"
    with pytest.raises(znt.NmeaNotZnt):
        znt.Znt(nmea_str=nmea_str)


class MockNTPStats:
    def __init__(self):
        self.ref_id = 0
        self.stratum = 2
        self.ref_time = 1270565749.41
        self.offset = 0.000080
        self.precision = -20
        self.root_delay = 0.117325
        self.root_dispersion = 0.046249
        self.version = 4
        self.leap = 0
        self.mode = 4
        self.poll = 6
        self.delay = 0.001
        self.tx_time = 1270565749.41
        self.orig_time = 1270565749.41
        self.recv_time = 1270565749.41
        self.dest_time = 1270565749.41


class MockNTPClient:
    def request(self, host, version=None):
        return MockNTPStats()


@mock.patch("ntplib.NTPClient", MockNTPClient)
@mock.patch("ntplib.ref_id_to_text")
def test_znt_get_status(mock_ref_id_to_text):
    mock_ref_id_to_text.return_value = "17.151.16.21"

    z = znt.Znt(hostname="127.0.0.1")
    assert z.params["talker"] == "PNT"
    assert z.params["host"] == "127.0.0.1"
    assert z.params["ref_clock"] == "17.151.16.21"
    assert z.params["stratum"] == 2
    assert z.params["last_update"] == 1270565749.41
    assert z.params["offset"] == "0.000080"
    assert z.params["precision"] == -20
    assert z.params["root_delay"] == "0.117325"
    assert z.params["root_dispersion"] == "0.046249"

    assert z.nmea_str.startswith("$PNTZNT,")
    assert z.nmea_str.endswith(f"*{znt.checksum_str(z.nmea_str)}")


def test_znt_pretty():
    nmea_str = "$PNTZNT,1270567048.57,127.0.0.1,17.151.16.21,4,1270565749.41,0.000080,-20,0.117325,0.046249*14"
    z = znt.Znt(nmea_str=nmea_str)
    pretty_str = z.pretty()

    assert "ZNT - NMEA Proprietary NTP status report" in pretty_str
    assert "talker:    NT" in pretty_str
    assert "timestamp:    1270567048.57" in pretty_str
    assert "stratum:    4" in pretty_str
    assert "precision:    -20.0" in pretty_str


def test_znt_logger_will_write():
    # Test always write
    logger_always = znt.ZntLogger(None, always=True)
    assert logger_always.will_write() is True

    # Test max_sec expiry
    logger_sec = znt.ZntLogger(None, max_sec=0.1)
    logger_sec.last_write = time.time() - 0.2
    assert logger_sec.will_write() is True

    # Test max_cnt expiry
    logger_cnt = znt.ZntLogger(None, max_cnt=5)
    logger_cnt.cnt_since_last = 6
    assert logger_cnt.will_write() is True

    # Test disabled
    logger_disabled = znt.ZntLogger(None, enabled=False, max_sec=10)
    assert logger_disabled.will_write() is False

    # Test state_str
    assert "update: NOT ENABLED" in logger_disabled.state_str()
    assert "update: WILL write" in logger_cnt.state_str()

    logger_not_ready = znt.ZntLogger(None, max_cnt=5)
    assert "update: NO write..." in logger_not_ready.state_str()


@mock.patch("nmea.znt.Znt")
def test_znt_logger_update(mock_znt_class):
    mock_znt_instance = mock.Mock()
    mock_znt_instance.nmea_str = "$PNTZNT,fake*xx"
    mock_znt_class.return_value = mock_znt_instance

    out_file = io.StringIO()
    logger = znt.ZntLogger(out_file, always=True, station="TESTSTATION")

    logger.update()

    output = out_file.getvalue()
    assert "$PNTZNT,fake*xx,TESTSTATION," in output


@mock.patch("nmea.znt.Znt")
def test_znt_logger_update_no_write(mock_znt_class):
    mock_znt_instance = mock.Mock()
    mock_znt_instance.nmea_str = "$PNTZNT,fake*xx"
    mock_znt_class.return_value = mock_znt_instance

    out_file = io.StringIO()
    logger = znt.ZntLogger(out_file, max_cnt=5)
    logger.cnt_since_last = 0

    logger.update()

    # Should not write
    assert out_file.getvalue() == ""
    assert logger.cnt_since_last == 1

    # Force write
    logger.update(force=True)
    assert mock_znt_class.called
