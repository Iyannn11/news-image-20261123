"""THE WORLD IN ONE DAY — MONDAY 23 NOVEMBER 2026.

Entry program for the make.fun news-image-20261123 bounty. The page
itself is drawn by render.py; this program simply copies the finished
1024x1024 front page (entry.png) to the grader's output directory.

Runs under Python 3.13, standard library only. The source image lives
next to this file; the destination is MAKEFUN_OUTPUT_DIR, falling back
to /output, exactly as the grader mounts it. The repository is mounted
read-only at run time, so nothing is ever written next to this file.
"""

import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))


def main() -> int:
    src = HERE / "entry.png"
    dst = OUT_DIR / "entry.png"
    if not src.is_file():
        print(f"missing image: {src}", file=sys.stderr)
        return 1
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    print(f"copied {src} -> {dst} ({dst.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
