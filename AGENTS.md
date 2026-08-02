# AGENTS.md: Developer & AI Coding Assistant Guide

This document provides operational guidance, repository architecture, build/test
commands, and strict governance rules for developers and AI coding assistants
working on **noaadata** ([`README`](README)).

> **IMPORTANT CONTINUOUS UPDATE MANDATE**: As `noaadata` undergoes Spec-Driven
> Development (SDD) modernization from legacy packaging ([`setup.py`](setup.py))
> to modern Python (`>=3.13`, `pyproject.toml`, `uv`, `pytest`, `ruff`, strict
> static typing), **you must continuously update all sections of `AGENTS.md`**
> (overview, repository layout, build/test commands, formatting standards, and
> architecture notes) as the codebase evolves.

______________________________________________________________________

## 1. Project Overview (Current State)

`noaadata` is a Python library for encoding, decoding, and processing NOAA
CO-OPS marine water level data, Automatic Identification System (AIS) ship
traffic binary messages, USCG N-AIS receive fields, and NMEA-0183 marine
sentences. It also provides database bridges (PostgreSQL/PostGIS, SQLite3) and
GIS exporters (Google Earth KML).

The project is currently undergoing a multi-phase Spec-Driven Development (SDD)
modernization initiative outlined in [`PRD.md`](PRD.md), [`SPEC.md`](SPEC.md),
and [`TASKS.md`](TASKS.md).

______________________________________________________________________

## 2. Repository Layout (Current State)

- [`noaadata/`](noaadata): NOAA CO-OPS water level SOAP and DAP client/parsing
  ([`stations.py`](noaadata/stations.py),
  [`waterlevel_dap.py`](noaadata/waterlevel_dap.py),
  [`waterlevelraw.py`](noaadata/waterlevelraw.py),
  [`dumpallwl.py`](noaadata/dumpallwl.py)).
- [`ais/`](ais): Marine AIS binary message definitions (messages 1–24, IMO
  messages, binary waterlevel messages, whale notices, compilers/translators).
- [`aisutils/`](aisutils): Core [`BitVector.py`](aisutils/BitVector.py), 6-bit
  ASCII strings ([`aisstring.py`](aisutils/aisstring.py)), binary bit unpacking
  ([`binary.py`](aisutils/binary.py)), database bridges
  ([`database.py`](aisutils/database.py), [`sqlhelp.py`](aisutils/sqlhelp.py)),
  USCG extensions ([`uscg.py`](aisutils/uscg.py)), and grid calculations
  ([`grid.py`](aisutils/grid.py)).
- [`nmea/`](nmea): Standard NMEA-0183 sentences ([`gga.py`](nmea/gga.py),
  [`rmc.py`](nmea/rmc.py), [`zda.py`](nmea/zda.py), [`znt.py`](nmea/znt.py), and
  checksum validation [`checksum.py`](nmea/checksum.py)).
- [`scripts/`](scripts): 69 command-line utilities for AIS traffic decoding,
  database ingestion, and KML generation.
- [`test/`](test): Legacy test scripts ([`grid_tests.py`](test/grid_tests.py),
  [`test.ais`](test/test.ais)).
- [`setup.py`](setup.py): Legacy setuptools build script (to be replaced by
  `pyproject.toml` and `hatchling`).

______________________________________________________________________

## 3. Build & Test Commands (Current State)

### Legacy Environment Setup

Currently, `noaadata` uses setuptools:

```bash
# Install package in editable mode
python setup.py develop

# Run legacy test script
python test/grid_tests.py
```

> **Note**: As Phase 1 and Phase 2 of the SDD modernization complete, these
> commands will transition to `uv sync`, `uv run pytest`, `uv run ruff check`,
> and `uv run ty check`. Update this section immediately upon completion of
> Phase 1 (`pyproject.toml` adoption).

______________________________________________________________________

## 4. Strict Version Control & Git Commit Rules

All contributors and AI coding assistants MUST adhere to the following version
control guardrails:

### 4.1 Conventional Commits Required

Every Git commit message MUST follow the **Conventional Commits** specification:

```
<type>(<scope>): <subject>
```

- **Allowed Types**:
  - `feat`: A new feature or capability (e.g.,
    `feat(ais): add support for message 24`).
  - `fix`: A bug fix (e.g., `fix(nmea): resolve checksum boundary error`).
  - `refactor`: Code refactoring without behavioral changes (e.g.,
    `refactor(aisutils): implement dunder protocols on BitVector`).
  - `test`: Adding or updating test suites (e.g.,
    `test(noaadata): migrate legacy grid tests to pytest`).
  - `build`: Packaging or dependency updates (e.g.,
    `build: migrate from setup.py to pyproject.toml and hatchling`).
  - `docs`: Documentation updates (e.g.,
    `docs: update migration guide and AGENTS.md`).
  - `chore`: Maintenance tasks (e.g.,
    `chore: configure ruff and mdformat pre-commit hooks`).
- **Scope**: Must name the specific package or component being modified (`ais`,
  `aisutils`, `nmea`, `noaadata`, `scripts`, `test`, `build`, `docs`).
- **Subject**: Concise, imperative description of the change (lower-case, no
  trailing period).

### 4.2 ABSOLUTELY NO Tag or Conversation ID Entries in Commits

- **CRITICAL**: Do **NOT** include any `TAG=gy`, `TAG=agy`, `CONV=...`,
  `BUG=...`, or conversation ID metadata trailers in Git commit messages for
  this repository.
- Commit messages must remain clean, standard Conventional Commits without
  automated conversation tracking trailers.

______________________________________________________________________

## 5. Style & Documentation Standards

- **Docstrings**: Use **Google Python Docstring Style** (`Args:`, `Returns:`,
  `Raises:`, `Attributes:`) for all modules, classes, and functions.
- **Formatting**: Maintain 88-column line length for Python code (enforced by
  `ruff format` in Phase 3) and 80-column line length for Markdown documentation
  (enforced by `mdformat`).
- **Type Annotations**: Follow PEP 585/PEP 604 syntax (`list[int]`,
  `str | None`, `typing.Self`). Do not introduce ambiguous `Any` types without
  explicit documentation.
