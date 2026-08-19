"""Tests for building the move plan.

Every test builds a real tree under ``tmp_path``. The planner's whole promise
is that it reads a directory without altering it, and only a real directory
can prove that.
"""

from collections.abc import Callable
from pathlib import Path

import pytest

from fileflow.planner import Move, build_plan

Snapshot = Callable[[Path], dict[str, bytes | None]]


def test_empty_directory_yields_no_moves(tmp_path: Path) -> None:
    assert build_plan(tmp_path) == []


def test_loose_files_are_routed_to_their_category(tmp_path: Path) -> None:
    (tmp_path / "invoice.pdf").touch()
    (tmp_path / "holiday.jpg").touch()

    assert build_plan(tmp_path) == [
        Move(tmp_path / "holiday.jpg", tmp_path / "Images" / "holiday.jpg"),
        Move(tmp_path / "invoice.pdf", tmp_path / "Documents" / "invoice.pdf"),
    ]


def test_unrecognised_files_are_routed_to_other(tmp_path: Path) -> None:
    (tmp_path / "mystery.xyz").touch()

    assert build_plan(tmp_path) == [
        Move(tmp_path / "mystery.xyz", tmp_path / "Other" / "mystery.xyz")
    ]


def test_destinations_stay_inside_the_scanned_directory(tmp_path: Path) -> None:
    (tmp_path / "song.mp3").touch()
    (tmp_path / "invoice.pdf").touch()

    plan = build_plan(tmp_path)

    # Without this the loop below would pass on an empty plan, vouching for
    # nothing.
    assert [move.source.name for move in plan] == ["invoice.pdf", "song.mp3"]
    for move in plan:
        assert move.destination.parent.parent == tmp_path


def test_existing_subdirectories_and_their_contents_are_left_alone(
    tmp_path: Path,
) -> None:
    project = tmp_path / "ProjectX"
    project.mkdir()
    (project / "notes.txt").touch()
    (tmp_path / "loose.txt").touch()

    plan = build_plan(tmp_path)

    assert plan == [Move(tmp_path / "loose.txt", tmp_path / "Documents" / "loose.txt")]


def test_a_category_folder_that_already_exists_is_not_treated_as_a_file(
    tmp_path: Path,
) -> None:
    (tmp_path / "Documents").mkdir()
    (tmp_path / "report.pdf").touch()

    assert build_plan(tmp_path) == [
        Move(tmp_path / "report.pdf", tmp_path / "Documents" / "report.pdf")
    ]


def test_hidden_files_are_skipped(tmp_path: Path) -> None:
    (tmp_path / ".env").touch()
    (tmp_path / ".DS_Store").touch()
    (tmp_path / "visible.pdf").touch()

    plan = build_plan(tmp_path)

    assert [move.source.name for move in plan] == ["visible.pdf"]


def test_zero_byte_files_are_still_planned(tmp_path: Path) -> None:
    empty = tmp_path / "empty.pdf"
    empty.touch()

    assert empty.stat().st_size == 0
    assert build_plan(tmp_path) == [Move(empty, tmp_path / "Documents" / "empty.pdf")]


def test_names_with_spaces_and_unicode_are_planned_unchanged(tmp_path: Path) -> None:
    name = "informe anual — versión final.pdf"
    (tmp_path / name).touch()

    assert build_plan(tmp_path) == [
        Move(tmp_path / name, tmp_path / "Documents" / name)
    ]


def test_the_plan_is_sorted_and_reproducible(tmp_path: Path) -> None:
    for name in ["c.mp3", "a.pdf", "b.jpg"]:
        (tmp_path / name).touch()

    plan = build_plan(tmp_path)

    assert [move.source.name for move in plan] == ["a.pdf", "b.jpg", "c.mp3"]
    assert build_plan(tmp_path) == plan


def test_building_a_plan_does_not_change_the_directory(
    tmp_path: Path, snapshot: Snapshot
) -> None:
    (tmp_path / "invoice.pdf").write_bytes(b"pdf")
    (tmp_path / "mystery.xyz").write_bytes(b"?")
    (tmp_path / ".hidden").write_bytes(b"secret")
    nested = tmp_path / "ProjectX"
    nested.mkdir()
    (nested / "notes.txt").write_bytes(b"notes")
    before = snapshot(tmp_path)

    build_plan(tmp_path)

    assert snapshot(tmp_path) == before


def test_a_missing_directory_raises_rather_than_returning_nothing(
    tmp_path: Path,
) -> None:
    with pytest.raises(FileNotFoundError):
        build_plan(tmp_path / "does-not-exist")


def test_a_path_that_is_a_file_raises(tmp_path: Path) -> None:
    target = tmp_path / "not-a-directory.pdf"
    target.touch()

    with pytest.raises(NotADirectoryError):
        build_plan(target)
