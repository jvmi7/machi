#!/usr/bin/env python3
"""
cli.py
------
Command-line entry point.

Usage:
    python cli.py path/to/your_code.py
    python cli.py path/to/your_code.py -o art.svg
    python cli.py path/to/your_code.py --html      # also write a viewable .html

Turns one Python source file into one SVG artwork whose shapes, colors,
and layout are all derived from that file's structure.
"""

import argparse
import os
import sys

from analyzer import analyze_file
from palette import build_palette
from generator import generate_svg


def build_html_wrapper(svg: str, title: str) -> str:
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{title} — code art</title>
<style>
  body {{ margin:0; display:flex; align-items:center; justify-content:center;
          min-height:100vh; background:#0b0b0f; }}
  svg {{ max-width:90vmin; max-height:90vmin; box-shadow:0 20px 60px rgba(0,0,0,.5); }}
</style>
</head>
<body>
{svg}
</body>
</html>
"""


def main():
    parser = argparse.ArgumentParser(
        description="Turn a Python file's structure into generative SVG art."
    )
    parser.add_argument("source", help="Path to a .py file to render")
    parser.add_argument(
        "-o", "--output", default=None,
        help="Output SVG path (default: <source-name>.svg)",
    )
    parser.add_argument(
        "--html", action="store_true",
        help="Also write a standalone .html file you can open directly",
    )
    args = parser.parse_args()

    if not os.path.isfile(args.source):
        print(f"error: no such file: {args.source}", file=sys.stderr)
        sys.exit(1)

    sig = analyze_file(args.source)
    palette = build_palette(sig)
    svg = generate_svg(sig, palette)

    out_path = args.output or (os.path.splitext(os.path.basename(args.source))[0] + ".svg")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg)

    print(f"wrote {out_path}")
    print(
        f"  mood={palette.mood}  functions={sig.function_count} "
        f"loops={sig.loop_count} branches={sig.branch_count} "
        f"depth={sig.max_depth} complexity={sig.complexity:.1f}"
    )

    if args.html:
        html_path = os.path.splitext(out_path)[0] + ".html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(build_html_wrapper(svg, os.path.basename(args.source)))
        print(f"wrote {html_path}")


if __name__ == "__main__":
    main()
