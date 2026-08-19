"""Record what a run did, so it can be undone.

Every line is written and flushed as its move happens, never batched at the
end. A run killed halfway through therefore leaves a journal describing
exactly the moves that reached the disk, which is what makes an interrupted
run recoverable rather than a guess.
"""

import json
from datetime import datetime
from pathlib import Path

from fileflow.planner import Move

JOURNAL_DIR = Path.home() / ".fileflow" / "journal"


def start_run() -> Path:
    """Return the path of a new, empty journal file.

    Runs are named after the local time they started, which sorts
    chronologically as plain text and needs no counter or UUID.

    The file is created straight away, empty. A run that ends up moving
    nothing must still be the latest run, or an undo afterwards would reach
    past it and revert the run before it instead.
    """
    JOURNAL_DIR.mkdir(parents=True, exist_ok=True)
    run = JOURNAL_DIR / f"{datetime.now().strftime('%Y%m%d-%H%M%S')}.jsonl"
    run.touch()
    return run


def record(run: Path, move: Move) -> None:
    """Append *move* to the journal at *run* and flush it to disk."""
    entry = {"source": str(move.source), "destination": str(move.destination)}
    with run.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(entry) + "\n")


def read_run(run: Path) -> list[Move]:
    """Return the moves recorded in the journal at *run*, in the order made."""
    return [
        Move(Path(entry["source"]), Path(entry["destination"]))
        for entry in (
            json.loads(line) for line in run.read_text(encoding="utf-8").splitlines()
        )
    ]


def latest_run() -> Path | None:
    """Return the most recent journal, or None if no run was ever recorded."""
    if not JOURNAL_DIR.is_dir():
        return None
    runs = sorted(JOURNAL_DIR.glob("*.jsonl"))
    return runs[-1] if runs else None
