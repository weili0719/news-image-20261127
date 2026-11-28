#!/usr/bin/env python3
"""Graded entry point for the round-10 front page (news-image-20261127).

The picture is drawn on the build machine by compose_day10.py (Pillow plus
the DejaVu fonts that live there). The grading sandbox is a slim image with
no system fonts and no network, so this file deliberately does no drawing
at all: it uses only the standard library to check the pre-rendered
entry.jpg that ships in this repository and copy it to /output/entry.png,
the path the bounty names.

Checks before copying: the file must exist beside this script, start with
the JPEG magic bytes, be under 1 MiB, and match the SHA-256 recorded at
build time. Any failure exits non-zero with a plain message on stderr.
"""
import hashlib
import shutil
import sys
from pathlib import Path

EXPECTED_SHA256 = "aaccf148de9dbc058ec13ee904722ecaa9cbe7dbf84a70a9efec15c0a07a8e21"
EXPECTED_BYTES = 350073
MAX_BYTES = 1024 * 1024
JPEG_MAGIC = b"\xff\xd8\xff"
OUTPUT_PATH = Path("/output/entry.png")


def die(message):
    print("main.py: " + message, file=sys.stderr)
    return 1


def main():
    here = Path(__file__).resolve().parent
    source = here / "entry.jpg"
    if not source.is_file():
        return die("entry.jpg not found next to main.py")
    data = source.read_bytes()
    if len(data) != EXPECTED_BYTES:
        return die("entry.jpg is %d bytes, expected %d"
                   % (len(data), EXPECTED_BYTES))
    if len(data) > MAX_BYTES:
        return die("entry.jpg exceeds the 1 MiB limit")
    if not data.startswith(JPEG_MAGIC):
        return die("entry.jpg does not start with JPEG magic bytes")
    digest = hashlib.sha256(data).hexdigest()
    if digest != EXPECTED_SHA256:
        return die("entry.jpg SHA-256 mismatch: got " + digest)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, OUTPUT_PATH)
    written = OUTPUT_PATH.read_bytes()
    if not written.startswith(JPEG_MAGIC):
        return die("written /output/entry.png is not a JPEG")
    if hashlib.sha256(written).hexdigest() != EXPECTED_SHA256:
        return die("written /output/entry.png failed its hash check")
    print("main.py: wrote %s (%d bytes, sha256 %s)"
          % (OUTPUT_PATH, len(written), EXPECTED_SHA256))
    return 0


if __name__ == "__main__":
    sys.exit(main())
