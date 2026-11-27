#!/usr/bin/env python3
"""Sum up 27 November 2026's world news in one image.

Entry for the make.fun bounty "Sum up 27 November's world news in one
image" (slug: news-image-20261127).

The program copies the image held in this repository (entry.jpg, a
1024x1024 JPEG, 316,073 bytes) to /output/entry.png, exactly as the
bounty describes as the simplest program for this bounty. It uses
only the Python standard library, makes no network requests, and is
fully deterministic: every run writes the same bytes.
"""

import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "entry.jpg"
OUTPUT = Path("/output/entry.png")


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SOURCE, OUTPUT)


if __name__ == "__main__":
    main()
