"""Tests for extension based classification.

No filesystem here on purpose: ``classify`` takes a path but never touches it,
and these tests hold it to that by passing paths that do not exist.
"""

from pathlib import Path

import pytest

from fileflow.classifier import _EXTENSIONS_BY_CATEGORY, classify


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("invoice.pdf", "Documents"),
        ("notes.md", "Documents"),
        ("holiday.jpg", "Images"),
        ("diagram.svg", "Images"),
        ("podcast.mp3", "Audio"),
        ("lecture.mkv", "Video"),
        ("backup.zip", "Archives"),
        ("main.py", "Code"),
        ("config.toml", "Code"),
    ],
)
def test_known_extensions_map_to_their_category(name: str, expected: str) -> None:
    assert classify(Path(name)) == expected


@pytest.mark.parametrize(
    "name",
    ["mystery.xyz", "README", "archive.", "data.unknownformat"],
)
def test_unrecognised_files_fall_back_to_other(name: str) -> None:
    assert classify(Path(name)) == "Other"


@pytest.mark.parametrize("name", ["REPORT.PDF", "Photo.JpG", "song.Mp3"])
def test_extension_matching_ignores_case(name: str) -> None:
    assert classify(Path(name)) != "Other"


def test_multi_part_extension_uses_the_last_suffix() -> None:
    assert classify(Path("logs.tar.gz")) == "Archives"


def test_only_the_file_name_matters_not_its_directory() -> None:
    # A misleading parent directory must not sway the result.
    assert classify(Path("/home/user/Images/report.pdf")) == "Documents"


@pytest.mark.parametrize(
    "name",
    ["informe anual.pdf", "cañón.jpg", "résumé (final).docx", "🎵 track.mp3"],
)
def test_spaces_and_unicode_in_names_do_not_break_classification(name: str) -> None:
    assert classify(Path(name)) != "Other"


def test_no_extension_is_claimed_by_two_categories() -> None:
    seen: dict[str, str] = {}
    for category, extensions in _EXTENSIONS_BY_CATEGORY.items():
        for extension in extensions:
            assert extension not in seen, (
                f"{extension} is in both {seen.get(extension)} and {category}"
            )
            seen[extension] = category


def test_every_extension_is_stored_lowercase_with_a_leading_dot() -> None:
    for extensions in _EXTENSIONS_BY_CATEGORY.values():
        for extension in extensions:
            assert extension == extension.lower()
            assert extension.startswith(".")


def test_other_is_not_used_as_a_category_name_in_the_map() -> None:
    # "Other" is the fallback for unrecognised files; a category by that name
    # would make an unknown extension indistinguishable from a known one.
    assert "Other" not in _EXTENSIONS_BY_CATEGORY
