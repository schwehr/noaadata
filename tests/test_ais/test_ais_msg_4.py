import pytest

from ais import ais_msg_4
from aisutils import binary


def test_encode_decode() -> None:
    """Test encoding and then decoding preserves the parameters for AIS message 4."""
    params = ais_msg_4.testParams()
    bv = ais_msg_4.encode(params)
    decoded_params = ais_msg_4.decode(bv)

    assert decoded_params["MessageID"] == params["MessageID"]
    assert decoded_params["UserID"] == params["UserID"]
    assert decoded_params["RepeatIndicator"] == params["RepeatIndicator"]
    assert decoded_params["Time_year"] == params["Time_year"]
    assert decoded_params["Time_month"] == params["Time_month"]
    assert decoded_params["Time_day"] == params["Time_day"]
    assert decoded_params["Time_hour"] == params["Time_hour"]
    assert decoded_params["Time_min"] == params["Time_min"]
    assert decoded_params["Time_sec"] == params["Time_sec"]
    assert decoded_params["PositionAccuracy"] == params["PositionAccuracy"]
    assert pytest.approx(float(decoded_params["Position_longitude"]), 0.001) == float(
        params["Position_longitude"]
    )
    assert pytest.approx(float(decoded_params["Position_latitude"]), 0.001) == float(
        params["Position_latitude"]
    )
    assert decoded_params["fixtype"] == params["fixtype"]
    assert decoded_params["RAIM"] == params["RAIM"]
    assert decoded_params["state_syncstate"] == params["state_syncstate"]
    assert decoded_params["state_slottimeout"] == params["state_slottimeout"]
    assert decoded_params["state_slotoffset"] == params["state_slotoffset"]


def test_decode_message_4() -> None:
    """Test decoding a specific payload for AIS message 4."""
    payload = "403Ot1i00018?w?W1A4r3@@@@@@@"
    bv = binary.ais6tobitvec(payload)

    msg = ais_msg_4.decode(bv)
    assert msg["MessageID"] == 4
    assert "UserID" in msg
    assert "Time_year" in msg
    assert "Time_month" in msg
    assert "Time_day" in msg
    assert "Time_hour" in msg
    assert "Time_min" in msg
    assert "Time_sec" in msg
