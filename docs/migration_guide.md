# Migration Guide: Upgrading to Modern `noaadata`

This guide assists developers upgrading from legacy `noaadata` / `setup.py`
packaging to the modern Python `>=3.14` standard using `pyproject.toml` and
`uv`.

## Overview of Major Changes

1. **Python 3.14+ Requirements**:

   - Modern `noaadata` requires Python `>=3.14`.
   - Uses PEP 585/PEP 604 standard typing syntax (`list[int]`, `str | None`).

1. **Packaging & Installation**:

   - Legacy `setup.py` has been replaced with standard `pyproject.toml` using
     `hatchling` as the build backend.
   - Development environments are managed deterministically using `uv`.

1. **CLI Commands**:

   - All executable scripts under `scripts/` have been refactored into module
     entry points inside `src/noaadata/cli/` and registered as
     `[project.scripts]` in `pyproject.toml`.
   - Example: Run `ais-info` or `uv run ais-info` directly.

1. **Performance & Memory Optimizations**:

   - **Bit Vector Operations**: Payloads are processed using bitwise integer
     shifts (`int(bv)`), yielding ~7-9x decoding speedups.
   - **Memory Layout**: Key classes (`UscgNmea`, `Grid`, `Station`, `Znt`,
     `AisPositionStats`) utilize `__slots__` to eliminate per-instance
     `__dict__` overhead.
   - **Checksum Calculation**: NMEA checksums use byte-vector
     `functools.reduce(operator.xor, ...)` for maximum throughput.

## Upgrading Development Setup

```bash
# Sync dependencies and build virtual environment with uv
uv sync

# Run tests
uv run pytest
```
