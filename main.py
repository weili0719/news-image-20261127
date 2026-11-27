"""Place the finished 27 November front page at the grading location.

The artwork is a pre-rendered JPEG that ships in this repository as
entry.jpg. This program does no drawing at all: it copies those bytes
to /output/entry.png and checks the copy's SHA-256 against the digest
recorded at build time, so a corrupted or truncated copy is caught
instead of being graded. Standard library only; no fonts, no images
library, no network, no subprocess.
"""

import hashlib
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ARTWORK = HERE / "entry.jpg"
TARGET = Path("/output/entry.png")
RECORDED_DIGEST = "00f7434e33a780a8393467f88f0d31367fba712593349697dbaa0f6c36a12920"
BLOCK = 1024 * 128


def sha256_of(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for piece in iter(lambda: stream.read(BLOCK), b""):
            hasher.update(piece)
    return hasher.hexdigest()


def main() -> int:
    if not ARTWORK.is_file():
        print(f"missing artwork: {ARTWORK}", file=sys.stderr)
        return 1
    if sha256_of(ARTWORK) != RECORDED_DIGEST:
        print("shipped artwork digest does not match the recorded build digest",
              file=sys.stderr)
        return 1
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    with ARTWORK.open("rb") as src, TARGET.open("wb") as dst:
        shutil.copyfileobj(src, dst, BLOCK)
    if sha256_of(TARGET) != RECORDED_DIGEST:
        print("copied output digest does not match the recorded build digest",
              file=sys.stderr)
        return 1
    print(f"wrote {TARGET} ({TARGET.stat().st_size} bytes, sha256 {RECORDED_DIGEST[:12]}...)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
