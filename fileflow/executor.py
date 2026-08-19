"""Carry out a plan the planner already built.

This is the only module that changes the filesystem, and it decides nothing:
every destination was chosen upstream, so a dry run and a real run differ
only in whether this function is called at all.

Nothing here overwrites. A move whose destination is taken is reported back
untouched rather than forced through.
"""

import shutil
from pathlib import Path
from typing import NamedTuple

from fileflow import journal
from fileflow.planner import Move


class Skip(NamedTuple):
    """A move that was refused, and the reason it could not be made."""

    move: Move
    reason: str


def apply_plan(moves: list[Move], run: Path | None = None) -> list[Skip]:
    """Perform *moves*, returning the ones that were refused.

    Category folders are created as needed. A move is refused when its
    destination is already taken, or when the folder it needs is blocked by a
    file of that name; in both cases the source file is left exactly where it
    is.

    Each completed move is appended to the journal at *run* before the next
    one starts, so an interrupted run leaves a record of what it managed to
    do. Passing None performs the moves without recording them.
    """
    skips = []
    for move in moves:
        if move.destination.exists():
            skips.append(Skip(move, "destination already exists"))
            continue
        try:
            move.destination.parent.mkdir(exist_ok=True)
        except FileExistsError:
            skips.append(Skip(move, f"{move.destination.parent.name} is not a folder"))
            continue
        shutil.move(move.source, move.destination)
        if run is not None:
            journal.record(run, move)
    return skips


def undo(moves: list[Move]) -> list[Skip]:
    """Put the files of a recorded run back, returning the moves refused.

    Moves are reverted newest first, mirroring the order they were made. A
    file the user has since renamed, deleted or replaced is left alone and
    reported: undoing a run must never undo the user's own later work.
    """
    skips = []
    for move in reversed(moves):
        if not move.destination.exists():
            skips.append(Skip(move, "no longer where the run left it"))
            continue
        if move.source.exists():
            skips.append(Skip(move, "its original path is taken again"))
            continue
        shutil.move(move.destination, move.source)

    _remove_emptied_folders(moves)
    return skips


def _remove_emptied_folders(moves: list[Move]) -> None:
    """Delete the category folders a revert left empty.

    One left behind would make the tree differ from the one the run started
    with. Only empty ones go: a folder still holding a file is the user's
    business, not ours.
    """
    for folder in {move.destination.parent for move in moves}:
        if folder.is_dir() and not any(folder.iterdir()):
            folder.rmdir()
