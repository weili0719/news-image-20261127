#!/usr/bin/env python3
"""Copy the pre-rendered front page to the grader output location.

The image itself is rendered ahead of time by compose.py on the build
machine, so this script needs nothing but the standard library: no fonts,
no image libraries, no network, no subprocesses. It just copies entry.jpg
to /output/entry.png and checks the copy is exactly the file that was
submitted, byte for byte.
"""

import hashlib
import os
import shutil
import sys
from pathlib import Path

SOURCE_NAME = "entry.jpg"
EXPECTED_SHA256 = "00f7434e33a780a8393467f88f0d31367fba712593349697dbaa0f6c36a12920"
JPEG_MAGIC = b"\xff\xd8"
MIN_BYTES = 10_000
OUTPUT_DIR = Path("/output")
OUTPUT_NAME = "entry.png"


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    source = Path(__file__).resolve().parent / SOURCE_NAME
    if not source.is_file():
        print(f"error: source image not found: {source}", file=sys.stderr)
        return 1

    source_size = os.path.getsize(source)
    if source_size < MIN_BYTES:
        print(
            f"error: source image too small: {source} is {source_size} bytes, "
            f"expected at least {MIN_BYTES} bytes",
            file=sys.stderr,
        )
        return 1
    with open(source, "rb") as handle:
        magic = handle.read(len(JPEG_MAGIC))
    if magic != JPEG_MAGIC:
        print(
            f"error: source image is not a JPEG: {source} starts with "
            f"{magic.hex() or '(empty)'}, expected magic bytes ff d8",
            file=sys.stderr,
        )
        return 1

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    target = OUTPUT_DIR / OUTPUT_NAME
    shutil.copyfile(source, target)

    actual = sha256_of(target)
    if actual != EXPECTED_SHA256:
        print(f"error: sha256 mismatch for copied file {target}", file=sys.stderr)
        print(f"  expected: {EXPECTED_SHA256}", file=sys.stderr)
        print(f"  actual:   {actual}", file=sys.stderr)
        return 1

    size = os.path.getsize(target)
    if size != source_size:
        print(
            f"error: copied file size changed: source {source_size} bytes, "
            f"copy {size} bytes",
            file=sys.stderr,
        )
        return 1
    print(f"ok: wrote {target} ({size} bytes, sha256 {actual})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
