__author__ = "Kurt Schwehr"
__version__ = ["$Revision:", "4799", "$"][1]
__revision__ = __version__  # For pylint
__date__ = [
    "$Date:",
    "2006-09-25",
    "11:09:02",
    "-0400",
    "(Mon,",
    "25",
    "Sep",
    "2006)",
    "$",
][1]
__copyright__ = "2009"
__license__ = "Apache 2.0"

__doc__ = """
Handle communication state as described in Annex 2 - 3.3.7.2.1 of ITU 1371.3

@since: 2009-Jul-21
"""

sotdma_fields = (
    "sync_state",
    "slot_timeout",
    "received_stations",
    "slot_number",
    "commstate_utc_hour",
    "commstate_utc_min",
    "commstate_utc_spare",
    "slot_offset",
)


def sotdma_sql_fields(c):
    "sqlhelp fields for commstate"
    for field in sotdma_fields:
        c.addInt(field)


def sotdma_parse_bits(bv):
    assert len(bv) == 19
    v = int(bv)
    sync_state = (v >> 17) & 0x3
    slot_timeout = (v >> 14) & 0x7
    submessage = v & 0x3FFF

    r = {
        "sync_state": sync_state,
        "slot_timeout": slot_timeout,
    }

    if slot_timeout in (3, 5, 7):
        r["received_stations"] = submessage
    elif slot_timeout in (2, 4, 6):
        r["slot_number"] = submessage
    elif slot_timeout == 1:
        r["commstate_utc_hour"] = (submessage >> 9) & 0x1F
        r["commstate_utc_min"] = (submessage >> 2) & 0x7F
        r["commstate_utc_spare"] = submessage & 0x3
    elif slot_timeout == 0:
        r["slot_offset"] = submessage
    else:
        raise AssertionError()

    return r


itdma_fields = (
    "sync_state",
    "slot_increment",
    "slots_to_allocate",
    "keep_flag",
)


def itdma_sql_fields(c):
    "sqlhelp fields for commstate"
    for field in itdma_fields:
        c.addInt(field)


def itdma_parse_bits(bv):
    assert len(bv) == 19
    v = int(bv)
    return {
        "sync_state": (v >> 17) & 0x3,
        "slot_increment": (v >> 4) & 0x1FFF,
        "slots_to_allocate": (v >> 1) & 0x7,
        "keep_flag": v & 0x1,
    }


def sql_fields(c):
    "sqlhelp fields for commstate - both SOTDMA and ITDMA"
    for field in set(sotdma_fields + itdma_fields):
        c.addInt(field)
