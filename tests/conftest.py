"""Fixtures shared by the test modules."""

from collections.abc import Callable
from pathlib import Path

import pytest

from fileflow import journal


@pytest.fixture(autouse=True)
def journal_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect the journal at *tmp_path* and return where it now points.

    Autouse and unconditional. A suite for a tool that moves files must not be
    able to write to a real home directory, and the surest way to guarantee
    that is to leave no test out, including the ones that never mention a run.
    """
    directory = tmp_path / "journal"
    monkeypatch.setattr(journal, "JOURNAL_DIR", directory)
    return directory


@pytest.fixture
def snapshot() -> Callable[[Path], dict[str, bytes | None]]:
    """Return a function mapping every path under a root to its contents.

    Directories map to None. Comparing two snapshots is how a test asserts
    that a tree is untouched, or restored exactly.
    """

    def take(root: Path) -> dict[str, bytes | None]:
        return {
            str(path.relative_to(root)): path.read_bytes() if path.is_file() else None
            for path in sorted(root.rglob("*"))
        }

    return take
