"""Unit tests for NMEA ZDA and ZNT sentence parsers."""

from nmea import zda, znt


def test_zda_decode_and_epoch() -> None:
    sentence = "$ZQZDA,110003.00,27,03,2006,-5,00*47"
    decoded = zda.zdaDecode(sentence)
    assert decoded["year"] == 2006
    assert decoded["mon"] == 3
    assert decoded["day"] == 27

    epoch_sec = zda.zdaEpochSeconds(sentence)
    assert epoch_sec > 0


def test_znt_decode() -> None:
    sentence = "$PNTZNT,1270567048.57,127.0.0.1,17.151.16.21,4,1270565749.41,0.000080,-20,0.117325,0.046249*14"
    znt_obj = znt.Znt(sentence)
    assert znt_obj.params["stratum"] == 4
    assert znt_obj.params["talker"] == "NT"
