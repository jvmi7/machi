# codeart

Turn a Python file into generative art. No neural net, no API calls —
just your code's own shape (functions, loops, branches, nesting) mapped
onto an SVG canvas.

Same file in -> same art out, every time. Change the code, change the art.

```
python cli.py your_file.py --html
```

That writes `your_file.svg` (and `your_file.html` if you open it in a
browser instead of an SVG viewer).

## How it reads your code

| In the code | On the canvas |
|---|---|
| each function | a ring, sized by that function's line count |
| each loop (`for` / `while`) | a spiral arm |
| each `if` / branch | a limb radiating from the center |
| each `try` block | a small dot orbiting close to the center |
| each import | a faint scattered dot in the background |
| max nesting depth | how tightly everything is packed toward the center |
| overall complexity | the radius of the thin outer ring |

Colors are generated from a hash of the source file, then nudged by the
same numbers above — more loops skews the palette warmer, more branching
skews it cooler, deeper nesting darkens the background. That combination
also produces a one-word "mood" (`energetic`, `intricate`, `dense`,
`minimal`, `balanced`) which gets printed to the console and stamped in
the corner of the image.

## Files

- **`analyzer.py`** — parses a `.py` file with Python's own `ast` module
  and reduces it to a `CodeSignature`: counts of functions, classes,
  loops, branches, try blocks, imports, nesting depth, etc.
- **`palette.py`** — turns a `CodeSignature` into a deterministic color
  `Palette` (background / primary / secondary / accent / line colors +
  a mood label).
- **`shapes.py`** — small SVG primitive builders (circles, lines,
  spirals, branch limbs, labels). No code-awareness, just markup.
- **`generator.py`** — the actual layout logic. Combines a
  `CodeSignature` + `Palette` + the shape helpers into one SVG string.
- **`cli.py`** — command-line entry point: `python cli.py <file.py>`.

## Usage

```bash
# basic — writes your_file.svg next to your source
python cli.py your_file.py

# custom output path
python cli.py your_file.py -o art.svg

# also write a standalone HTML file you can just open in a browser
python cli.py your_file.py --html
```

No dependencies beyond the Python standard library.

## Why

Every codebase has a shape — some are shallow and repetitive, some are
deeply nested and branchy, some loop constantly, some barely branch at
all. This just makes that shape visible. Point it at your messiest
file and your cleanest one and compare.

Not a bot, not an agent — just a deterministic renderer. Loosely
inspired by projects like Agent Machi that treat source code as raw
material for visual art.
