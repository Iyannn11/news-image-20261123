#!/usr/bin/env python3
"""main.py — news-image-20261123 entry program (Python 3.13, stdlib only).

Writes the entry image to /output/entry.png (or $MAKEFUN_OUTPUT_DIR).
The image is rendered by render.py from the facts in SOURCES.md using only
files bundled in this repository (fonts/, flags/*.svg, map_data.py), so the
program needs no network and no system fonts; it copies the rendered
entry.png beside this file, exactly like the kit's starter program.

Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
  mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")

os.makedirs(OUT, exist_ok=True)
shutil.copyfile(os.path.join(HERE, "entry.png"),
                os.path.join(OUT, "entry.png"))
