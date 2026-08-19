"""Carry out a plan the planner already built.

This is the only module that changes the filesystem, and it decides nothing:
every destination was chosen upstream, so a dry run and a real run differ
only in whether this function is called at all.

Nothing here overwrites. A move whose destination is taken is reported back
untouched rather than forced through.
"""

import shutil
from typing import NamedTuple

from fileflow.planner import Move


class Skip(NamedTuple):
    """A move that was refused, and the reason it could not be made."""

    move: Move
    reason: str


def apply_plan(moves: list[Move]) -> list[Skip]:
    """Perform *moves*, returning the ones that were refused.

    Category folders are created as needed. A move is refused when its
    destination is already taken, or when the folder it needs is blocked by a
    file of that name; in both cases the source file is left exactly where it
    is.
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
    return skips
