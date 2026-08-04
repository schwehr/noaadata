# noaadata

`noaadata` is a Python library for encoding, decoding, and processing NOAA CO-OPS marine water level data, Automatic Identification System (AIS) ship traffic binary messages, USCG N-AIS receive fields, and NMEA-0183 marine sentences.

## Key Features

- **NOAA CO-OPS Client & Data Parsing**: Fetch and process SOAP and DAP water level data.
- **Marine AIS Decoding**: Full support for AIS binary messages (messages 1–24, IMO binary messages, RIS/SLS messages).
- **USCG N-AIS Extensions**: Parse and construct USCG N-AIS metadata sentences (`UscgNmea`).
- **NMEA-0183 Sentence Handling**: Standard sentences (`GGA`, `RMC`, `ZDA`, `ZNT`) with high-performance XOR checksum validation.
- **Database & GIS Bridges**: Exporters for PostgreSQL/PostGIS, SQLite3, and Google Earth KML.

## Quick Start

### Installation

Install `noaadata` using `uv` or `pip`:

```bash
uv add noaadata
```

### Basic Usage

#### USCG NMEA & AIS Decoding

```python
from ais import ais_msg_1
from aisutils.uscg import UscgNmea

# Parse a USCG N-AIS sentence
sentence = "!AIVDM,1,1,,A,15Mt9B001;rgAFhGKLaRK1v2040@,0*63,s-85,d-110,T1270379515.39,r003669958,1270379515.39"
uscg_msg = UscgNmea(sentence)

# Extract bit vector payload and decode AIS Message 1
bv = uscg_msg.getBitVector()
report = ais_msg_1.decode(bv)

print(
    f"MMSI: {report['UserID']}, SOG: {report['SOG']} knots, Position: ({report['longitude']}, {report['latitude']})"
)
```
