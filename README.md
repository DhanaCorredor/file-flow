# FileFlow

[![CI](https://github.com/DhanaCorredor/file-flow/actions/workflows/ci.yml/badge.svg)](https://github.com/DhanaCorredor/file-flow/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![Checked with mypy](https://img.shields.io/badge/mypy-strict-2a6db2.svg)](https://mypy-lang.org/)
[![Ruff](https://img.shields.io/badge/linting-ruff-d7ff64.svg)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A safe, reversible command-line tool that organizes messy directories.

Point it at a folder such as `~/Downloads` and it sorts files into categorized
subfolders. It is built around three guarantees:

- **Safe by default** — previews the plan and changes nothing unless you pass `--apply`.
- **Reversible** — every run is journaled and can be undone with a single command.
- **Predictable** — never overwrites a file. Name collisions are resolved, not ignored.

Zero runtime dependencies: the Python standard library covers everything.

## Requirements

Python 3.11 or newer.

## Development

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

pytest                           # run the test suite
ruff check . && ruff format --check .
mypy fileflow
```

## License

[MIT](LICENSE)
