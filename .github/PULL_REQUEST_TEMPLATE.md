## Description

Please provide a summary of the changes and the rationale behind them.

- Fixes # (issue)
- Feature / Optimization / Maintenance

## Type of Change

- [ ] `feat`: A new feature
- [ ] `fix`: A bug fix
- [ ] `refactor`: Code refactoring without behavioral changes
- [ ] `perf`: Performance or memory layout optimization
- [ ] `test`: Unit, property, or benchmark test updates
- [ ] `docs`: Documentation updates
- [ ] `build` / `chore`: Packaging, CI/CD, or maintenance

## Verification & Testing

Please confirm the following verification steps have passed:

- [ ] All unit, property, and benchmark tests pass: `uv run pytest`
- [ ] Code formatting passes: `uv run ruff format --check`
- [ ] Linting passes: `uv run ruff check`
- [ ] Markdown formatting passes: `uv run mdformat --check README docs/ sdd/`
- [ ] Spell check passes: `uv run codespell .`
- [ ] Type check passes: `uv run mypy src/`
