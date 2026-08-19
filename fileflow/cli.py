"""Parse the command line, print what happened, pick an exit code.

Everything this module knows about organizing files comes from the modules
below it: it never decides where a file goes, and never moves one itself.
"""

import argparse
import sys
from pathlib import Path

from fileflow import executor, journal
from fileflow.planner import Move, build_plan


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="fileflow",
        description="Organize a directory by sorting loose files into "
        "categorized subfolders.",
    )
    parser.add_argument(
        "directory",
        nargs="?",
        type=Path,
        help="the directory to organize",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="perform the moves; without it nothing on disk is touched",
    )
    parser.add_argument(
        "--undo",
        action="store_true",
        help="put back the files moved by the most recent run",
    )

    args = parser.parse_args(argv)
    if args.undo and args.directory is not None:
        parser.error("--undo takes no directory: it reverts the most recent run")
    if not args.undo and args.directory is None:
        parser.error("a directory is required")
    return args


def _describe(move: Move) -> str:
    return f"{move.source.name} -> {move.destination.parent.name}/"


def _organize(directory: Path, apply: bool) -> int:
    try:
        plan = build_plan(directory)
    except FileNotFoundError:
        print(f"fileflow: {directory}: no such directory", file=sys.stderr)
        return 1
    except NotADirectoryError:
        print(f"fileflow: {directory}: not a directory", file=sys.stderr)
        return 1

    if not plan:
        print("Nothing to organize.")
        return 0

    if not apply:
        for move in plan:
            print(_describe(move))
        print(
            f"\n{len(plan)} file(s) to move. Nothing was written; "
            f"pass --apply to perform them."
        )
        return 0

    run = journal.start_run()
    skips = executor.apply_plan(plan, run)
    refused = {skip.move for skip in skips}
    for move in plan:
        if move not in refused:
            print(_describe(move))
    for skip in skips:
        print(f"skipped {skip.move.source.name}: {skip.reason}", file=sys.stderr)

    print(f"\nMoved {len(plan) - len(skips)} file(s), skipped {len(skips)}.")
    print(f"Recorded as {run.stem}. Undo it with: fileflow --undo")
    return 0


def _undo() -> int:
    run = journal.latest_run()
    if run is None:
        print("fileflow: no recorded run to undo", file=sys.stderr)
        return 1

    moves = journal.read_run(run)
    skips = executor.undo(moves)
    for skip in skips:
        print(f"skipped {skip.move.destination.name}: {skip.reason}", file=sys.stderr)

    print(f"Put back {len(moves) - len(skips)} file(s), skipped {len(skips)}.")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Run the command line tool and return its exit code.

    Returns 0 when the run completed, 1 when it could not. Files the run
    refused to touch are reported but do not make it a failure: nothing went
    wrong, there was simply less to do than planned. Misuse of the command
    line exits 2, which argparse handles on its own.
    """
    args = _parse_args(argv)
    if args.undo:
        return _undo()
    return _organize(args.directory, args.apply)
