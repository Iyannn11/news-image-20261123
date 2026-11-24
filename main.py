"""Entrypoint for THE WORLD IN ONE DAY (News 23, round 4).

R1 rebuilt as close to unchanged as possible, with one defect fix
(map pins 11 and 8 separated — they overlapped in R1). See render.py.

The grader mounts this repository read-only and gives us a separate
writable directory through MAKEFUN_OUTPUT_DIR. Output ALWAYS goes
there, never under MAKEFUN_BOT_DIR. Bot files resolve through
MAKEFUN_BOT_DIR, never through process.cwd().
"""

import os
import sys


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    bot_dir = os.environ.get("MAKEFUN_BOT_DIR") or here
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or os.path.join(
        bot_dir, "output"
    )
    os.makedirs(out_dir, exist_ok=True)
    if bot_dir not in sys.path:
        sys.path.insert(0, bot_dir)
    import render

    out_path = os.path.join(out_dir, "entry.png")
    render.render(out_path)
    problems = render.checks()
    if problems:
        print("gap scan FAIL (%d):" % len(problems))
        for p in problems:
            print("  " + p)
        sys.exit(1)
    print("gap scan PASS")
    print("wrote %s" % out_path)


if __name__ == "__main__":
    main()
