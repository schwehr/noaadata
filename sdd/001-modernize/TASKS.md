# Actionable Task Checklist (TASKS): Modernizing noaadata to Pure-Python >=3.13

This checklist outlines the sequential tasks required to modernize the `noaadata` repository (\[`README`\](noaadata/README)) according to the Spec-Driven Development (SDD) roadmap defined in \[`PRD.md`\](noaadata/PRD.md) and \[`SPEC.md`\](noaadata/SPEC.md).

______________________________________________________________________

## Phase 1: Spec-Driven Setup, Governance, & Dependency Management

- [x] **1.1 Establish SDD Governance Documents**

  - [x] Create \[`PRD.md`\](noaadata/PRD.md) defining project goals, user stories, and requirements.
  - [x] Create \[`SPEC.md`\](noaadata/SPEC.md) detailing technical architecture, type systems, and optimization strategies.
  - [x] Create \[`TASKS.md`\](noaadata/TASKS.md) (this document) to track all modernization tasks.
  - [x] Create \[`AGENTS.md`\](noaadata/AGENTS.md) at the repository root documenting repository structure, commands, and strict version control rules:
    - Enforce **Conventional Commits** (`<type>(<scope>): <subject>`).
    - Explicitly mandate **NO Tag or Conversation ID Entries** in commits.
    - Include explicit instructions to continuously update all sections of `AGENTS.md` as the codebase evolves throughout SDD phases.

- [x] **1.2 Configure Pre-Commit Hook Guardrails**

  - [x] Create an initial `.pre-commit-config.yaml` with `conventional-pre-commit` (enforcing Conventional Commits) and `mdformat` (80-column Markdown formatting).
  - [x] Verification command: `pre-commit run --all-files`

- [x] **1.3 Migrate Packaging to PEP 621 (`pyproject.toml`) & `uv`**

  - [x] Remove legacy \[`setup.py`\](noaadata/setup.py), `setup.cfg`, `requirements.txt`, and \[`MANIFEST.in`\](noaadata/MANIFEST.in).
  - [x] Create `pyproject.toml` with `hatchling` as the PEP 517 build backend and declare `requires-python = ">=3.13"`.
  - [x] Migrate CLI scripts from \[`scripts/`\](noaadata/scripts) into `[project.scripts]` entry points in `pyproject.toml`.
  - [x] Configure dependency groups (`dev`, optional `db` and `gis` extras) and generate deterministic `uv.lock`.
  - [x] Verification command: `uv sync && uv run python -c "import noaadata, ais, aisutils, nmea; print('Import OK')"`

- [x] **1.4 Standardize Package Layout**

  - [x] Reorganize or standardize code directory layout under `src/noaadata`, `src/ais`, `src/aisutils`, and `src/nmea` (or preserve root package directories with updated paths in `pyproject.toml`).
  - [x] Ensure dedicated top-level `tests/`, `docs/`, and `examples/` directories exist.

______________________________________________________________________

## Phase 2: Test Infrastructure, Coverage, & Benchmarking (`pytest`)

- [x] **2.1 Migrate Legacy Tests to Idiomatic `pytest`**

  - [x] Migrate tests from \[`test/grid_tests.py`\](noaadata/test/grid_tests.py) and \[`test/test.ais`\](noaadata/test/test.ais) into structured test suites in `tests/`:
    - `tests/test_ais/` (AIS messages 1-24, IMO messages, binary waterlevel messages, whale notices).
    - `tests/test_aisutils/` (\[`BitVector.py`\](noaadata/aisutils/BitVector.py), \[`aisstring.py`\](noaadata/aisutils/aisstring.py), \[`binary.py`\](noaadata/aisutils/binary.py), \[`grid.py`\](noaadata/aisutils/grid.py)).
    - `tests/test_nmea/` (\[`gga.py`\](noaadata/nmea/gga.py), \[`rmc.py`\](noaadata/nmea/rmc.py), \[`zda.py`\](noaadata/nmea/zda.py), \[`znt.py`\](noaadata/nmea/znt.py), \[`checksum.py`\](noaadata/nmea/checksum.py)).
    - `tests/test_noaadata/` (\[`stations.py`\](noaadata/noaadata/stations.py), \[`waterlevel_dap.py`\](noaadata/noaadata/waterlevel_dap.py)).
  - [x] Replace legacy `unittest.TestCase` assertions (`self.assertEqual`, `self.assertTrue`) with standard Python `assert` statements.
  - [x] Use `@pytest.mark.parametrize` for covering bitstream boundary cases and ITU-R M.1371 message variations.
  - [x] Use `tmp_path` fixtures for database and KML file output testing; use `pytest.raises(ValueError, match=...)` for exception testing.
  - [x] Verification command: `uv run pytest -v`

- [x] **2.2 Enforce Code Coverage Thresholds (`pytest-cov`)**

  - [x] Configure `pytest-cov` options in `pyproject.toml` (`--cov=noaadata --cov=ais --cov=aisutils --cov=nmea --cov-report=term-missing`).
  - [x] Add unit tests for untested branches across all four core packages to achieve 100% on refactored modules.
  - [x] Verification command: `uv run pytest --cov`

- [x] **2.3 Implement Property-Based & Fuzz Testing (`hypothesis` & `hypofuzz`)**

  - [x] Implement invariant property test suites in `tests/test_properties/`:
    - Test `BitVector` slicing, padding, and binary unpacking invariants.
    - Test bidirectional 6-bit ASCII encoding/decoding in \[`aisstring.py`\](noaadata/aisutils/aisstring.py).
    - Test NMEA-0183 XOR checksum calculation invariance in \[`checksum.py`\](noaadata/nmea/checksum.py).
  - [x] Add `hypofuzz` configuration for continuous fuzzing.
  - [x] Verification command: `uv run pytest tests/test_properties/ -v`

- [x] **2.4 Establish Performance Benchmarks (`pytest-benchmark`)**

  - [x] Create regression benchmark suites in `tests/benchmarks/`:
    - Benchmark `BitVector` slice extraction and concatenation.
    - Benchmark Class A AIS position report decoding (\[`ais_msg_1.py`\](noaadata/ais/ais_msg_1.py), \[`ais_msg_2.py`\](noaadata/ais/ais_msg_2.py), \[`ais_msg_3.py`\](noaadata/ais/ais_msg_3.py)).
    - Benchmark NMEA sentence checksum verification.
  - [x] Save initial baseline: `uv run pytest tests/benchmarks/ --benchmark-only --benchmark-save=baseline`

______________________________________________________________________

## Phase 3: Style, Formatting, & Static Analysis Guardrails

- [x] **3.1 Configure & Run `ruff` Formatting and Linting**

  - [x] Configure `ruff` in `pyproject.toml` with target Python `3.13` and selected rule sets (`E`, `F`, `W`, `I`, `UP`, `B`, `C4`, `SIM`, `RUF`, `PT`, `PL`).
  - [x] Run `ruff format` across `src/`, `tests/`, and `scripts/` to standardize formatting.
  - [x] Fix all linter warnings and errors reported by `ruff check` (e.g., removing unused imports, unnecessary dunders, and pointless statements).
  - [x] Verification command: `uv run ruff check && uv run ruff format --check`

- [x] **3.2 Standardize Markdown & Spell Checking (`mdformat` & `codespell`)**

  - [x] Format all Markdown files to 80-column GitHub Flavored Markdown using `mdformat`.
  - [x] Configure `codespell` with a custom dictionary for marine/NOAA abbreviations (`MMSI`, `SOG`, `COG`, `NMEA`, `CO-OPS`, `RTCM`).
  - [x] Fix all reported spelling errors across docstrings, documentation, and comments.
  - [x] Verification command: `uv run mdformat --check . && uv run codespell .`

- [ ] **3.3 Expand Pre-Commit Hooks & Static Security Scanning**

  - [ ] Update `.pre-commit-config.yaml` to execute `ruff-format`, `ruff`, `codespell`, `ty`, and `mypy` on pre-commit.
  - [ ] Integrate static security scanners: check for security antipatterns using `semgrep` and `bandit -r src/`, and scan GitHub workflows using `zizmor`.
  - [ ] Verification command: `pre-commit run --all-files`

______________________________________________________________________

## Phase 4: Python Syntax & Language Modernization

- [ ] **4.1 Automated Syntax Upgrades (`pyupgrade`)**

  - [ ] Run `pyupgrade --py313-plus` across all Python source files in `src/`, `tests/`, and `scripts/`.
  - [ ] Strip remaining Python 2 compatibility artifacts: remove explicit `(object)` inheritance, modernize exception syntax (`except Exception as err:`), and convert `super(Class, self)` to zero-argument `super()`.
  - [ ] Verification command: `uv run ruff check`

- [ ] **4.2 String Formatting Modernization**

  - [ ] Convert all `%`-formatting and `.format()` calls in \[`aisstring.py`\](noaadata/aisutils/aisstring.py), \[`sqlhelp.py`\](noaadata/aisutils/sqlhelp.py), and AIS/NMEA message decoders to f-strings (`f"MMSI: {mmsi}"`).
  - [ ] Verification command: `uv run pytest`

- [ ] **4.3 Standardize Docstrings to Google Python Docstring Style**

  - [ ] Audit and rewrite docstrings across all modules, classes, and methods in \[`noaadata`\](noaadata/noaadata), \[`ais`\](noaadata/ais), \[`aisutils`\](noaadata/aisutils), and \[`nmea`\](noaadata/nmea) to follow structured **Google Python Docstring Style** (`Args:`, `Returns:`, `Raises:`, `Attributes:`).

- [ ] **4.4 Standard Library & Control Flow Modernization**

  - [ ] Replace legacy pseudo-random generator calls (`random`) with `secrets` where security-sensitive or modern RNG generation applies.
  - [ ] Convert eager list transformations (`list(map(...))`, `list(filter(...))`) to generator expressions or comprehensions.
  - [ ] Ensure all file, socket, and database stream I/O operations use `with` context managers.
  - [ ] Verification command: `uv run pytest`

______________________________________________________________________

## Phase 5: Strict Static Typing & Protocols

- [ ] **5.1 Remediation of Baseline Type Errors (`ty`)**

  - [ ] Enable `ty` (`astral-sh/ty`) as a fast initial static type checker.
  - [ ] Identify and resolve baseline type errors across \[`noaadata`\](noaadata/noaadata), \[`ais`\](noaadata/ais), \[`aisutils`\](noaadata/aisutils), and \[`nmea`\](noaadata/nmea).
  - [ ] Verification command: `uv run ty check`

- [ ] **5.2 Complete Function & Attribute Type Annotations (PEP 585 / PEP 604)**

  - [ ] Add explicit type annotations for all function parameters, return types, and class attributes.
  - [ ] Eliminate ambiguous `Any` types; prefer precise typing (`Sequence[int]`, `Buffer`, `Literal`, `Mapping`).
  - [ ] Adopt modern PEP 585/604 syntax: `list[int]`, `dict[str, Any]`, union `|` operator (`int | None`), and `typing.Self` for constructors/builders.

- [ ] **5.3 Define Structural Protocols (`typing.Protocol`)**

  - [ ] Define `AISMessageHandler` and `NMEASentenceHandler` protocols in `src/ais/protocols.py` and `src/nmea/protocols.py`.
  - [ ] Define protocols for database bridges and GIS exporters in `src/aisutils/protocols.py`.

- [ ] **5.4 Add PEP 561 Package Markers & Multi-Checker Verification**

  - [ ] Add `py.typed` empty marker files to `src/noaadata/`, `src/ais/`, `src/aisutils/`, and `src/nmea/`.
  - [ ] Enforce strict cross-checker compatibility across `mypy --strict`, `pyright`, and `pyrefly`.
  - [ ] Verification command: `uv run mypy src/ tests/ && uv run ty check`

______________________________________________________________________

## Phase 6: Idiomatic API & Architectural Refactoring

- [ ] **6.0 Switch to using bitvector-modern**

  - [ ] Verify that all python files using BitVector have more than 95% test coverages.
  - [ ] Switch from Avi KaK's BitVector to https://github.com/schwehr/bitvector-modern

- [ ] **6.1 Implement Python Dunder Methods (Data Model Protocols)**

  - [ ] Refactor \[`BitVector.py`\](noaadata/aisutils/BitVector.py) and AIS message classes to implement standard dunders (`__getitem__`, `__setitem__`, `__len__`, `__iter__`, `__reversed__`, `__eq__`, `__int__`, `__format__`).
  - [ ] Implement bitwise operator overloading (`&`, `|`, `^`, `~`, `<<`, `>>`) on `BitVector` with clean immutability semantics.

- [ ] **6.2 Adopt Clean Constructor & Factory Patterns**

  - [ ] Require explicit keyword arguments for complex message class initialization.
  - [ ] Implement descriptive `classmethod` factory constructors (`from_bytes(data: bytes) -> Self`, `from_hex(hex_str: str) -> Self`, `from_bitvector(bits: BitVector) -> Self`, `from_stream(stream: IO[bytes]) -> Self`).

- [ ] **6.3 Decouple Orthogonal Concerns & Make State Explicit**

  - [ ] Decouple AIS/NMEA/waterlevel parsing structures from file paths and database connection handles; core codecs operate strictly on memory buffers, sequences, or streams.
  - [ ] Prefix internal implementation attributes with an underscore (`_bits`, `_size`, `_vector`, `_payload`) to clarify public API boundaries.
  - [ ] Standardize exception handling: replace bare `assert` statements with `ValueError`, `TypeError`, `KeyError`, `IndexError`, or custom domain exception classes.
  - [ ] Verification command: `uv run pytest -v && uv run mypy src/`

______________________________________________________________________

## Phase 7: Performance & Memory Optimization

- [ ] **7.1 Algorithmic & Built-In Acceleration**

  - [ ] Replace custom Python bit-counting and parity loops with `int.bit_count()` and standard C-backed Python built-ins.
  - [ ] Use `int.from_bytes(..., byteorder="big")` and `int.to_bytes(...)` in high-frequency binary unpacking paths.

- [ ] **7.2 Memory Layout & Packed Data Structures**

  - [ ] Refactor \[`BitVector.py`\](noaadata/aisutils/BitVector.py) and \[`binary.py`\](noaadata/aisutils/binary.py) to store bit sequences using compact contiguous storage (`bytearray`, `array.array('B')`, or fixed-width integer words) instead of Python lists of integers.
  - [ ] Define `__slots__` on high-instance AIS message classes (`AISMsg1`, `AISMsg2`, `AISMsg3`, `NMEA`, `Position`) to eliminate per-instance `__dict__` overhead.

- [ ] **7.3 Word-Level Bitwise Processing & Allocation Minimization**

  - [ ] Replace element-by-element bit iteration with block-level bitwise masking and bulk slice operations.
  - [ ] Pre-allocate correctly sized containers before decoding multi-field AIS payloads.
  - [ ] Eliminate redundant string/hex formatting conversions in hot decoding loops.
  - [ ] Verify speedups and ensure zero regressions against baseline: `uv run pytest tests/benchmarks/ --benchmark-compare=baseline`

______________________________________________________________________

## Phase 8: Documentation, CI/CD Automation, & Governance

- [ ] **8.1 Configure Modern Documentation (`mkdocs` & `mkdocstrings`)**

  - [ ] Create `mkdocs.yml` configured with `mkdocs-material` and `mkdocstrings[python]` to generate API reference pages from Google-style docstrings.
  - [ ] Write a comprehensive migration/porting guide (`docs/migration_guide.md`) for users upgrading from `noaadata 0.46` / legacy `setup.py`.
  - [ ] Verification command: `uv run mkdocs build --strict`

- [ ] **8.2 Establish GitHub Actions CI/CD Pipelines**

  - [ ] Create `.github/workflows/ci.yml` for automated matrix testing across Linux, macOS, and Windows on Python 3.13 and 3.14.
  - [ ] Ensure CI runs formatting (`ruff format --check`, `mdformat --check`), linting (`ruff check`), spell checking (`codespell`), typing (`ty`, `mypy`), tests with coverage (`--fail-under=95`), and benchmarks.
  - [ ] Create `.github/workflows/release.yml` to automate package building (`sdist`, `whl`) and publishing to PyPI via Trusted Publishing (OpenID Connect / OIDC).

- [ ] **8.3 Add Community Governance Files & Synchronize `AGENTS.md`**

  - [ ] Add standard community health files: \[`SECURITY.md`\](noaadata/SECURITY.md), \[`CODE_OF_CONDUCT.md`\](noaadata/CODE_OF_CONDUCT.md), \[`CODEOWNERS`\](noaadata/CODEOWNERS), and GitHub pull request templates.
  - [ ] Ensure \[`AGENTS.md`\](noaadata/AGENTS.md) is updated to reflect the final modernized architecture, package layout, and commands.
  - [ ] Final verification command: `uv run pytest && uv run ruff check && uv run mypy src/ tests/`
