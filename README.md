# FileFlow

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
