# FileFlow

[![CI](https://github.com/DhanaCorredor/file-flow/actions/workflows/ci.yml/badge.svg)](https://github.com/DhanaCorredor/file-flow/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![Checked with mypy](https://img.shields.io/badge/mypy-strict-2a6db2.svg)](https://mypy-lang.org/)
[![Ruff](https://img.shields.io/badge/linting-ruff-d7ff64.svg)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A safe, reversible command-line tool that organizes messy directories.

> **Not usable yet.** There is no command-line interface at this point — only the
> packaging and quality tooling. The section below states the design being built,
> not what the code does today.

Point it at a folder such as `~/Downloads` and it sorts files into categorized
subfolders. Three properties drive the design:

- **Safe by default** — preview the plan; change nothing unless `--apply` is passed.
- **Reversible** — journal every run so it can be undone with a single command.
- **Predictable** — never overwrite a file. Resolve name collisions instead of ignoring them.

Zero runtime dependencies: the Python standard library covers everything.

## Requirements

Python 3.11 or newer.

## Development

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

git config core.hooksPath .githooks   # run the quality gates before each commit

pytest                           # run the test suite
ruff check . && ruff format --check .
mypy fileflow
```

The hook runs the same checks CI runs, so a failing commit is caught before it is
written rather than after it is pushed. It is opt-in because git never enables hooks
from a clone automatically.

## License

[MIT](LICENSE)
