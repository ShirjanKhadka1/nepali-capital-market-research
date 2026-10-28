# SBOM — nepali-capital-market-research / scanner (Phase 7, 28 Oct 2026)

## Runtime dependencies
None. The scanner is standard-library only: no third-party package
is imported at runtime. That is the whole runtime SBOM.

## CI / developer dependencies (pinned, versions measured 28 Oct 2026)
| Tool | Version | Used for |
| --- | --- | --- |
| pytest | 9.2.0 | Scanner suite (57 tests) |
| ruff | 0.17.3 | Lint (`ruff check scanner/`, see scanner/ruff.toml for documented ignores) |

mypy is deliberately NOT in this repo's gate: scanner/ uses a dual
script/package import mode that mypy rejects on package bases
(measured 28 Oct 2026). Ruff is the scanner's static gate.

## Supply-chain status (config vs enabled)
- Dependency pinning: DONE (this file + pinned CI installs).
- CodeQL workflow: config added; GitHub-side enablement TO VERIFY.
- Dependabot config: added (weekly); enablement TO VERIFY.
- Secret scanning / push protection: GitHub settings, TO VERIFY;
  no secret has ever been committed here (no keys in code or data).
- Reproducible builds: pure Python, no compiled steps; scanner
  tests use fixed demo data, not live prices.
