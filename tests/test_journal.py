"""Tests for the run journal.

``JOURNAL_DIR`` is redirected at ``tmp_path`` throughout: a test suite that
wrote to the real home directory would be exactly the kind of surprise this
tool exists to avoid.
"""

from pathlib import Path

import pytest

from fileflow import journal
from fileflow.planner import Move


@pytest.fixture(autouse=True)
def journal_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    directory = tmp_path / "journal"
    monkeypatch.setattr(journal, "JOURNAL_DIR", directory)
    return directory


def test_a_recorded_move_reads_back_unchanged(tmp_path: Path) -> None:
    run = journal.start_run()
    move = Move(tmp_path / "invoice.pdf", tmp_path / "Documents" / "invoice.pdf")

    journal.record(run, move)

    assert journal.read_run(run) == [move]


def test_moves_read_back_in_the_order_they_were_recorded(tmp_path: Path) -> None:
    run = journal.start_run()
    first = Move(tmp_path / "a.pdf", tmp_path / "Documents" / "a.pdf")
    second = Move(tmp_path / "b.jpg", tmp_path / "Images" / "b.jpg")

    journal.record(run, first)
    journal.record(run, second)

    assert journal.read_run(run) == [first, second]


def test_each_move_is_on_disk_before_the_next_one_is_recorded(
    tmp_path: Path,
) -> None:
    run = journal.start_run()

    journal.record(run, Move(tmp_path / "a.pdf", tmp_path / "Documents" / "a.pdf"))

    # Read through a fresh handle: an entry buffered in memory would be
    # invisible here, and lost if the process were killed at this point.
    assert len(run.read_text(encoding="utf-8").splitlines()) == 1


def test_names_with_unicode_survive_the_round_trip(tmp_path: Path) -> None:
    run = journal.start_run()
    name = "informe anual — versión final.pdf"
    move = Move(tmp_path / name, tmp_path / "Documents" / name)

    journal.record(run, move)

    assert journal.read_run(run) == [move]


def test_a_started_run_is_empty(journal_dir: Path) -> None:
    run = journal.start_run()

    assert journal.read_run(run) == []
    assert run.parent == journal_dir


def test_latest_run_is_the_most_recent_of_several(journal_dir: Path) -> None:
    journal_dir.mkdir(parents=True)
    for name in ["20260819-100000", "20260819-120000", "20260819-110000"]:
        (journal_dir / f"{name}.jsonl").touch()

    latest = journal.latest_run()

    assert latest is not None
    assert latest.stem == "20260819-120000"


def test_latest_run_is_none_before_any_run_happened() -> None:
    assert journal.latest_run() is None


def test_latest_run_is_none_when_the_directory_holds_no_runs(
    journal_dir: Path,
) -> None:
    journal_dir.mkdir(parents=True)

    assert journal.latest_run() is None
