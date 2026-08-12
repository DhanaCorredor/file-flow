"""Turn a directory listing into the complete list of moves to perform.

The plan is built in full before anything is touched, which is what lets a
dry run and a real run share one code path: the same list is either printed
or handed to the executor.

Reading the directory is unavoidable I/O, but nothing here writes: calling
``build_plan`` can never change a single byte on disk.
"""

from pathlib import Path
from typing import NamedTuple

from fileflow.classifier import classify


class Move(NamedTuple):
    """One file relocation, decided but not yet performed."""

    source: Path
    destination: Path


def build_plan(directory: Path) -> list[Move]:
    """Return the moves that would organize *directory*.

    Only loose files at the top level are considered. Existing subdirectories
    are left completely alone, since they are structure the user already
    arranged by hand, and hidden files are skipped. Entries are walked in
    sorted order so a plan is reproducible between the dry run and the run
    that applies it.

    Propagates ``FileNotFoundError`` or ``NotADirectoryError`` if *directory*
    is not a readable directory; reporting that is the caller's job.
    """
    moves = []
    for entry in sorted(directory.iterdir()):
        if entry.name.startswith("."):
            continue
        if not entry.is_file():
            continue
        moves.append(Move(entry, directory / classify(entry) / entry.name))
    return moves
