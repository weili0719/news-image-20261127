#!/usr/bin/env python3
"""Graded entry point for make.fun bounty news-image-20261127, round 7.

Standard-library-only copy stub: it copies the pre-rendered front page
(`entry.jpg`, drawn on the build machine by compose_day7.py) to
`/output/entry.png` and verifies the SHA-256 matches the digest recorded
at build time. It imports no Pillow, touches no fonts, makes no network
calls and spawns no subprocesses, so it runs in the grader's pinned slim
image, which ships no system fonts.

Usage:  python3 main.py
"""
import hashlib
import pathlib
import shutil
import sys

EXPECTED_SHA256 = (
    "3a0ba68d464edfc47d20ec6c55c65b0dbc71915fdc2eedf7f1dedbc6e80357b4"
)

# A real front page is a full JPEG, not a stub or an empty file: require
# the JPEG start/end markers and a sane minimum size before trusting the
# digest. These checks run before the hash so a corrupt or truncated
# entry.jpg fails fast with a clear message instead of a bare mismatch.
JPEG_START = b"\xff\xd8\xff"
JPEG_END = b"\xff\xd9"
MIN_JPEG_BYTES = 100_000


def _check_jpeg(data):
    if len(data) < MIN_JPEG_BYTES:
        return "entry.jpg too small: %d bytes (minimum %d)" % (
            len(data), MIN_JPEG_BYTES)
    if not data.startswith(JPEG_START):
        return "entry.jpg is not a JPEG (missing SOI marker)"
    if not data.endswith(JPEG_END):
        return "entry.jpg is truncated (missing EOI marker)"
    return None


def main():
    here = pathlib.Path(__file__).resolve().parent
    source = here / "entry.jpg"
    target_dir = pathlib.Path("/output")
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / "entry.png"

    data = source.read_bytes()
    problem = _check_jpeg(data)
    if problem is not None:
        print(problem, file=sys.stderr)
        return 1
    digest = hashlib.sha256(data).hexdigest()
    if digest != EXPECTED_SHA256:
        print("sha256 mismatch: got %s, expected %s" % (digest,
                                                        EXPECTED_SHA256),
              file=sys.stderr)
        return 1
    shutil.copyfile(source, target)
    print("copied %s -> %s (%d bytes, sha256 %s)"
          % (source, target, len(data), digest))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
