"""Tests for applying a move plan.

Plans are handed to the executor by hand rather than built by the planner:
the executor's job is to carry out whatever list it is given, and building
the list here keeps each test independent of how directory entries sort.
"""

from pathlib import Path

from fileflow.executor import Skip, apply_plan
from fileflow.planner import Move, build_plan


def test_a_file_is_moved_into_its_category_folder(tmp_path: Path) -> None:
    source = tmp_path / "invoice.pdf"
    source.write_bytes(b"pdf")
    destination = tmp_path / "Documents" / "invoice.pdf"

    assert apply_plan([Move(source, destination)]) == []
    assert not source.exists()
    assert destination.read_bytes() == b"pdf"


def test_an_empty_plan_creates_nothing(tmp_path: Path) -> None:
    assert apply_plan([]) == []
    assert list(tmp_path.iterdir()) == []


def test_file_contents_survive_the_move(tmp_path: Path) -> None:
    source = tmp_path / "song.mp3"
    source.write_bytes(bytes(range(256)))

    apply_plan([Move(source, tmp_path / "Audio" / "song.mp3")])

    assert (tmp_path / "Audio" / "song.mp3").read_bytes() == bytes(range(256))


def test_one_category_folder_serves_every_file_in_it(tmp_path: Path) -> None:
    for name in ["a.pdf", "b.pdf"]:
        (tmp_path / name).write_bytes(name.encode())

    skips = apply_plan(
        [
            Move(tmp_path / "a.pdf", tmp_path / "Documents" / "a.pdf"),
            Move(tmp_path / "b.pdf", tmp_path / "Documents" / "b.pdf"),
        ]
    )

    assert skips == []
    assert sorted(p.name for p in (tmp_path / "Documents").iterdir()) == [
        "a.pdf",
        "b.pdf",
    ]


def test_an_existing_category_folder_is_reused(tmp_path: Path) -> None:
    (tmp_path / "Documents").mkdir()
    (tmp_path / "Documents" / "old.pdf").write_bytes(b"old")
    source = tmp_path / "new.pdf"
    source.write_bytes(b"new")

    assert apply_plan([Move(source, tmp_path / "Documents" / "new.pdf")]) == []
    assert (tmp_path / "Documents" / "old.pdf").read_bytes() == b"old"
    assert (tmp_path / "Documents" / "new.pdf").read_bytes() == b"new"


def test_a_taken_destination_is_skipped_and_neither_file_changes(
    tmp_path: Path,
) -> None:
    source = tmp_path / "report.pdf"
    source.write_bytes(b"incoming")
    (tmp_path / "Documents").mkdir()
    destination = tmp_path / "Documents" / "report.pdf"
    destination.write_bytes(b"already here")
    move = Move(source, destination)

    assert apply_plan([move]) == [Skip(move, "destination already exists")]
    assert source.read_bytes() == b"incoming"
    assert destination.read_bytes() == b"already here"


def test_a_file_blocking_a_category_folder_is_skipped_not_destroyed(
    tmp_path: Path,
) -> None:
    blocker = tmp_path / "Images"
    blocker.write_bytes(b"not a folder")
    source = tmp_path / "holiday.jpg"
    source.write_bytes(b"jpg")
    move = Move(source, tmp_path / "Images" / "holiday.jpg")

    assert apply_plan([move]) == [Skip(move, "Images is not a folder")]
    assert blocker.read_bytes() == b"not a folder"
    assert source.read_bytes() == b"jpg"


def test_a_skip_does_not_stop_the_rest_of_the_plan(tmp_path: Path) -> None:
    (tmp_path / "Documents").mkdir()
    (tmp_path / "Documents" / "taken.pdf").write_bytes(b"already here")
    (tmp_path / "taken.pdf").write_bytes(b"incoming")
    (tmp_path / "fine.pdf").write_bytes(b"fine")

    skips = apply_plan(
        [
            Move(tmp_path / "taken.pdf", tmp_path / "Documents" / "taken.pdf"),
            Move(tmp_path / "fine.pdf", tmp_path / "Documents" / "fine.pdf"),
        ]
    )

    assert [skip.move.source.name for skip in skips] == ["taken.pdf"]
    assert (tmp_path / "Documents" / "fine.pdf").read_bytes() == b"fine"


def test_names_with_spaces_and_unicode_are_moved_unchanged(tmp_path: Path) -> None:
    name = "informe anual — versión final.pdf"
    source = tmp_path / name
    source.write_bytes(b"pdf")

    apply_plan([Move(source, tmp_path / "Documents" / name)])

    assert (tmp_path / "Documents" / name).read_bytes() == b"pdf"


def test_a_zero_byte_file_is_moved(tmp_path: Path) -> None:
    source = tmp_path / "empty.pdf"
    source.touch()

    apply_plan([Move(source, tmp_path / "Documents" / "empty.pdf")])

    assert (tmp_path / "Documents" / "empty.pdf").stat().st_size == 0


def test_a_planned_run_moves_every_loose_file(tmp_path: Path) -> None:
    (tmp_path / "invoice.pdf").write_bytes(b"pdf")
    (tmp_path / "holiday.jpg").write_bytes(b"jpg")
    (tmp_path / "mystery.xyz").write_bytes(b"?")

    assert apply_plan(build_plan(tmp_path)) == []
    assert (tmp_path / "Documents" / "invoice.pdf").read_bytes() == b"pdf"
    assert (tmp_path / "Images" / "holiday.jpg").read_bytes() == b"jpg"
    assert (tmp_path / "Other" / "mystery.xyz").read_bytes() == b"?"
