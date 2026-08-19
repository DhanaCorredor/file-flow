# FileFlow

[![CI](https://github.com/DhanaCorredor/file-flow/actions/workflows/ci.yml/badge.svg)](https://github.com/DhanaCorredor/file-flow/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![Checked with mypy](https://img.shields.io/badge/mypy-strict-2a6db2.svg)](https://mypy-lang.org/)
[![Ruff](https://img.shields.io/badge/linting-ruff-d7ff64.svg)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A safe, reversible command-line tool that organizes messy directories.

Point it at a folder such as `~/Downloads` and it sorts loose files into
categorized subfolders. Three properties drive the design:

- **Safe by default** — it prints the plan and changes nothing unless `--apply` is passed.
- **Reversible** — every run is journaled, and `--undo` puts the files back.
- **Predictable** — it never overwrites a file. A move it cannot make safely is
  reported and skipped, never forced.

Zero runtime dependencies: the Python standard library covers everything.

## Install

Python 3.11 or newer.

```bash
pip install .
```

## Usage

Preview what would happen. This is the default, and it writes nothing:

```console
$ fileflow ~/Downloads
archive.zip -> Archives/
holiday.jpg -> Images/
invoice.pdf -> Documents/
mystery.xyz -> Other/
song.mp3 -> Audio/

5 file(s) to move. Nothing was written; pass --apply to perform them.
```

Perform the moves:

```console
$ fileflow ~/Downloads --apply
...
Moved 5 file(s), skipped 0.
Recorded as 20260819-144516. Undo it with: fileflow --undo
```

Change your mind:

```console
$ fileflow --undo
Put back 5 file(s), skipped 0.
```

`python -m fileflow` works identically.

### What it touches

Only loose files at the top level of the directory you name. Subfolders you
already organized are left alone, contents included, and so are hidden files.
It never recurses.

Files are sorted by extension into `Documents`, `Images`, `Audio`, `Video`,
`Archives`, `Code`, and `Other` for anything unrecognized.

### What it refuses to do

A move is skipped, and the reason printed, when the destination name is already
taken, or when a loose file carries the name of a category folder and blocks it.
The source file stays exactly where it is. Skipped files do not make the run fail:
the exit code is `0`, `1` for a run that could not proceed, `2` for misuse of the
command line.

Undo is equally careful. A file you renamed, deleted or replaced after the run is
reported and left alone rather than overwritten.

> **Design intent, not yet built:** resolving a name collision by comparing
> hashes and adding a numeric suffix, deleting verified duplicates behind an
> opt-in flag, and reading categories from a TOML config file.

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
