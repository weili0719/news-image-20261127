"""Emit the finished 27 November news mosaic.

This entry's program takes the pre-rendered JPEG that ships beside it
and places an identical copy at the grading location, /output/entry.png.
The picture itself is fixed artwork; the program only moves bytes, so
every run produces exactly the same output file.
"""

from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

SOURCE_NAME = "entry.jpg"
DESTINATION = Path("/output/entry.png")
CHUNK = 1024 * 64


def _source_path() -> Path:
    """Locate the artwork next to this script, wherever it is run from."""
    return Path(__file__).resolve().parent / SOURCE_NAME


def _digest(path: Path) -> str:
    """Return the SHA-256 hex digest of a file, read in blocks."""
    summer = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            block = handle.read(CHUNK)
            if not block:
                break
            summer.update(block)
        return summer.hexdigest()


def publish() -> None:
    """Copy the mosaic to the output path and confirm it landed intact."""
    artwork = _source_path()
    before = _digest(artwork)
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    with artwork.open("rb") as reader, DESTINATION.open("wb") as writer:
        shutil.copyfileobj(reader, writer, CHUNK)
    after = _digest(DESTINATION)
    if before != after:
        raise RuntimeError("output does not match the shipped artwork")
    print(f"wrote {DESTINATION} ({DESTINATION.stat().st_size} bytes)")


if __name__ == "__main__":
    publish()
