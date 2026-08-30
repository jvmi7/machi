"""
generator.py
------------
The "artist". Takes a CodeSignature (analyzer.py) and a Palette
(palette.py) and lays out an SVG piece.

Mapping, roughly:
  - one ring per function, sized by that function's line count
  - one spiral arm per loop
  - one branch per if/branch, radiating outward
  - nesting depth controls how tightly everything is packed toward
    the center
  - import count seeds a scatter of small background dots

Nothing here is random per-run: every number is derived from the
signature's digest, so re-running on the same file reproduces the
same picture, and small code changes produce visibly different (but
not wildly different) art.
"""

import math

from shapes import circle, spiral_path, branch, text_label, line

WIDTH = 800
HEIGHT = 800
CENTER = (WIDTH / 2, HEIGHT / 2)


def _seed_stream(digest: str):
    """Yield an endless stream of pseudo-random floats in [0, 1) derived
    from the hex digest, cycling if we run past its length."""
    i = 0
    n = len(digest)
    while True:
        chunk = digest[i % n: i % n + 4] or "0"
        yield (int(chunk, 16) % 10007) / 10007
        i += 4


def generate_svg(sig, palette) -> str:
    seed = _seed_stream(sig.digest or "0" * 64)
    cx, cy = CENTER
    parts = []

    parts.append(
        f'<rect x="0" y="0" width="{WIDTH}" height="{HEIGHT}" '
        f'fill="{palette.background}" />'
    )

    # Faint background scatter, one dot per import.
    for _ in range(sig.import_count):
        x = next(seed) * WIDTH
        y = next(seed) * HEIGHT
        r = 1.5 + next(seed) * 2.5
        parts.append(circle(x, y, r, palette.secondary, opacity=0.25))

    # Packing radius shrinks as nesting depth grows -> denser code
    # reads as a tighter, more compressed piece.
    pack = 1.0 - min(0.55, sig.max_depth * 0.05)

    # One ring per function, sized by that function's length,
    # arranged evenly around the center.
    fn_lengths = sig.function_lengths or [max(1, sig.line_count // 4)]
    n = len(fn_lengths)
    max_len = max(fn_lengths)
    base_radius = min(WIDTH, HEIGHT) * 0.34 * pack

    for i, length in enumerate(fn_lengths):
        angle = (i / max(n, 1)) * 2 * math.pi + next(seed) * 0.2
        dist = base_radius * (0.4 + 0.6 * (i % 5) / 5)
        x = cx + dist * math.cos(angle)
        y = cy + dist * math.sin(angle)
        r = 8 + (length / max(max_len, 1)) * 46
        opacity = 0.55 + 0.35 * next(seed)
        parts.append(circle(x, y, r, palette.primary, opacity=opacity))
        parts.append(
            circle(x, y, r * 0.55, palette.background, opacity=0.5)
        )

    # One spiral arm per loop, rotated around the center.
    for i in range(sig.loop_count):
        angle_offset = (i / max(sig.loop_count, 1)) * 2 * math.pi
        arm_cx = cx + 30 * math.cos(angle_offset)
        arm_cy = cy + 30 * math.sin(angle_offset)
        turns = 2 + next(seed) * 3
        radius = base_radius * (0.5 + 0.4 * next(seed))
        parts.append(
            spiral_path(
                arm_cx, arm_cy, turns, radius,
                stroke=palette.accent, width=1.2 + next(seed),
                opacity=0.55,
            )
        )

    # One branch limb per if/branch, radiating from center.
    for i in range(sig.branch_count):
        angle = next(seed) * 2 * math.pi
        length = base_radius * (0.3 + 0.7 * next(seed))
        seg, (ex, ey) = branch(
            cx, cy, angle, length,
            stroke=palette.line, width=1.0 + next(seed) * 1.5,
            opacity=0.5,
        )
        parts.append(seg)
        if next(seed) > 0.5:
            parts.append(circle(ex, ey, 3 + next(seed) * 4, palette.accent, opacity=0.7))

    # One small dot ring per try/except block, drawn tight around center.
    for i in range(sig.try_count):
        angle = (i / max(sig.try_count, 1)) * 2 * math.pi
        r = 18 + i * 6
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        parts.append(circle(x, y, 4, palette.secondary, opacity=0.8))

    # A thin outer ring whose radius encodes overall complexity.
    outline_r = base_radius * (0.85 + min(0.4, sig.complexity / 60))
    parts.append(
        f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{outline_r:.2f}" '
        f'fill="none" stroke="{palette.line}" stroke-width="1" opacity="0.35" />'
    )

    # Signature strip at the bottom: file name + mood + a few raw numbers.
    label = (
        f"{sig.file_name}  ·  {palette.mood}  ·  "
        f"fn:{sig.function_count} loop:{sig.loop_count} "
        f"branch:{sig.branch_count} depth:{sig.max_depth}"
    )
    parts.append(text_label(24, HEIGHT - 20, label, palette.line, size=12, opacity=0.5))

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}">\n'
        + "\n".join(parts)
        + "\n</svg>\n"
    )
    return svg
