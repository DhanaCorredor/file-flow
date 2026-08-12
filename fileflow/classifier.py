"""Decide which folder a file belongs in, from its name alone.

Pure by design: classification never reads the filesystem, so both this module
and the planner built on top of it are testable without a directory tree.
"""

from pathlib import Path

# Extensions grouped by destination folder. Grouping reads better than a flat
# extension -> category map, and it is the shape a user edits to add a format.
_EXTENSIONS_BY_CATEGORY: dict[str, frozenset[str]] = {
    "Documents": frozenset(
        {
            ".pdf",
            ".doc",
            ".docx",
            ".odt",
            ".rtf",
            ".txt",
            ".md",
            ".epub",
            ".xls",
            ".xlsx",
            ".ods",
            ".csv",
            ".ppt",
            ".pptx",
            ".odp",
        }
    ),
    "Images": frozenset(
        {
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".bmp",
            ".tif",
            ".tiff",
            ".webp",
            ".svg",
            ".ico",
            ".heic",
            ".psd",
        }
    ),
    "Audio": frozenset(
        {
            ".mp3",
            ".wav",
            ".flac",
            ".aac",
            ".ogg",
            ".opus",
            ".m4a",
            ".wma",
            ".aiff",
        }
    ),
    "Video": frozenset(
        {
            ".mp4",
            ".mkv",
            ".mov",
            ".avi",
            ".wmv",
            ".flv",
            ".webm",
            ".m4v",
            ".mpg",
            ".mpeg",
        }
    ),
    "Archives": frozenset(
        {
            ".zip",
            ".tar",
            ".gz",
            ".tgz",
            ".bz2",
            ".xz",
            ".zst",
            ".7z",
            ".rar",
            ".iso",
        }
    ),
    "Code": frozenset(
        {
            ".py",
            ".js",
            ".ts",
            ".jsx",
            ".tsx",
            ".java",
            ".c",
            ".h",
            ".cpp",
            ".cs",
            ".go",
            ".rs",
            ".rb",
            ".php",
            ".swift",
            ".kt",
            ".sh",
            ".ps1",
            ".sql",
            ".html",
            ".css",
            ".xml",
            ".json",
            ".yaml",
            ".yml",
            ".toml",
            ".ini",
        }
    ),
}

_CATEGORY_BY_EXTENSION: dict[str, str] = {
    extension: category
    for category, extensions in _EXTENSIONS_BY_CATEGORY.items()
    for extension in extensions
}


def classify(path: Path) -> str:
    """Return the name of the folder *path* belongs in.

    Only the final extension is considered, case-insensitively: ``.tar.gz``
    classifies as an archive through ``.gz``. Anything unrecognised, including
    files with no extension at all, lands in ``Other`` rather than being
    guessed at.
    """
    return _CATEGORY_BY_EXTENSION.get(path.suffix.lower(), "Other")
