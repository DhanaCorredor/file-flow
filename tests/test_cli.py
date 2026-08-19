"""Tests for the command line tool, driven through ``main`` end to end.

The journal is redirected at ``tmp_path`` so no test can write to the real
home directory, and every run works on a real temporary tree.
"""

from pathlib import Path

import pytest

from fileflow import journal
from fileflow.cli import main

USAGE_ERROR = 2


@pytest.fixture(autouse=True)
def journal_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    directory = tmp_path / "journal"
    monkeypatch.setattr(journal, "JOURNAL_DIR", directory)
    return directory


@pytest.fixture
def messy(tmp_path: Path) -> Path:
    """A directory with one file per outcome the tests care about."""
    directory = tmp_path / "downloads"
    directory.mkdir()
    (directory / "invoice.pdf").write_bytes(b"pdf")
    (directory / "holiday.jpg").write_bytes(b"jpg")
    (directory / "mystery.xyz").write_bytes(b"?")
    return directory


def snapshot(root: Path) -> dict[str, bytes | None]:
    """Map every path under *root* to its contents, or None for directories."""
    return {
        str(path.relative_to(root)): path.read_bytes() if path.is_file() else None
        for path in sorted(root.rglob("*"))
    }


def test_a_dry_run_changes_nothing_on_disk(messy: Path) -> None:
    before = snapshot(messy)

    assert main([str(messy)]) == 0

    assert snapshot(messy) == before


def test_a_dry_run_prints_the_planned_moves(
    messy: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    main([str(messy)])

    output = capsys.readouterr().out
    assert "holiday.jpg -> Images/" in output
    assert "invoice.pdf -> Documents/" in output
    assert "mystery.xyz -> Other/" in output
    assert "--apply" in output


def test_apply_moves_the_files(messy: Path) -> None:
    assert main([str(messy), "--apply"]) == 0

    assert (messy / "Documents" / "invoice.pdf").read_bytes() == b"pdf"
    assert (messy / "Images" / "holiday.jpg").read_bytes() == b"jpg"
    assert (messy / "Other" / "mystery.xyz").read_bytes() == b"?"


def test_apply_performs_exactly_what_the_dry_run_printed(
    messy: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    main([str(messy)])
    planned = sorted(capsys.readouterr().out.splitlines()[:3])

    main([str(messy), "--apply"])
    performed = sorted(capsys.readouterr().out.splitlines()[:3])

    assert performed == planned


def test_a_skipped_file_is_reported_without_failing_the_run(
    messy: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (messy / "Documents").mkdir()
    (messy / "Documents" / "invoice.pdf").write_bytes(b"already here")

    assert main([str(messy), "--apply"]) == 0

    captured = capsys.readouterr()
    assert "skipped invoice.pdf: destination already exists" in captured.err
    assert (messy / "Documents" / "invoice.pdf").read_bytes() == b"already here"
    assert (messy / "invoice.pdf").read_bytes() == b"pdf"


def test_an_empty_directory_succeeds_quietly(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    empty = tmp_path / "empty"
    empty.mkdir()

    assert main([str(empty), "--apply"]) == 0
    assert "Nothing to organize." in capsys.readouterr().out


def test_a_missing_directory_fails_with_a_clear_message(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    missing = tmp_path / "nope"

    assert main([str(missing)]) == 1
    assert "no such directory" in capsys.readouterr().err


def test_a_path_that_is_a_file_fails(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    target = tmp_path / "file.pdf"
    target.touch()

    assert main([str(target)]) == 1
    assert "not a directory" in capsys.readouterr().err


def test_no_arguments_is_a_usage_error() -> None:
    with pytest.raises(SystemExit) as exit_info:
        main([])

    assert exit_info.value.code == USAGE_ERROR


def test_undo_with_a_directory_is_a_usage_error(messy: Path) -> None:
    with pytest.raises(SystemExit) as exit_info:
        main([str(messy), "--undo"])

    assert exit_info.value.code == USAGE_ERROR


def test_undo_restores_the_directory_byte_for_byte(messy: Path) -> None:
    before = snapshot(messy)

    main([str(messy), "--apply"])
    assert snapshot(messy) != before

    assert main(["--undo"]) == 0
    assert snapshot(messy) == before


def test_undo_before_any_run_fails(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--undo"]) == 1
    assert "no recorded run to undo" in capsys.readouterr().err


def test_undo_leaves_alone_a_file_the_user_moved_afterwards(
    messy: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    main([str(messy), "--apply"])
    kept = messy / "Documents" / "renamed.pdf"
    (messy / "Documents" / "invoice.pdf").rename(kept)

    assert main(["--undo"]) == 0

    captured = capsys.readouterr()
    assert "skipped invoice.pdf: no longer where the run left it" in captured.err
    assert kept.read_bytes() == b"pdf"
    assert not (messy / "invoice.pdf").exists()


def test_a_run_records_only_the_moves_it_made(messy: Path) -> None:
    (messy / "Documents").mkdir()
    (messy / "Documents" / "invoice.pdf").write_bytes(b"already here")

    main([str(messy), "--apply"])

    run = journal.latest_run()
    assert run is not None
    recorded = [move.source.name for move in journal.read_run(run)]
    assert sorted(recorded) == ["holiday.jpg", "mystery.xyz"]
