"""Smoke tests guarding packaging integrity.

These catch the failures that only appear once the project is installed
rather than run from the source tree, which unit tests never reach.
"""

import importlib
import re
from importlib.metadata import version
from pathlib import Path

import fileflow


def test_package_is_importable_by_name() -> None:
    assert importlib.import_module("fileflow") is fileflow


def test_version_follows_semantic_versioning() -> None:
    assert re.fullmatch(r"\d+\.\d+\.\d+", fileflow.__version__)


def test_installed_version_matches_package_metadata() -> None:
    assert version("fileflow") == fileflow.__version__


def test_type_marker_ships_with_the_package() -> None:
    assert fileflow.__file__ is not None
    marker = Path(fileflow.__file__).parent / "py.typed"
    assert marker.is_file(), "PEP 561 marker missing: annotations will be ignored"
