"""
shapes.py
---------
Small, dependency-free SVG primitive builders. Nothing here knows
anything about "code" — it just knows how to emit SVG markup strings.
Keeping this separate means generator.py reads like a recipe instead
of a wall of string formatting.
"""

import math 


def circle(cx, cy, r, fill, opacity=1.0, stroke=None, stroke_width=0):
    stroke_attr = f' stroke="{stroke}" stroke-width="{stroke_width}"' if stroke else ""
    return (
        f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" '
        f'fill="{fill}" opacity="{opacity:.2f}"{stroke_attr} />'
    )


def line(x1, y1, x2, y2, stroke, width=1.0, opacity=1.0):
    return (
        f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
        f'stroke="{stroke}" stroke-width="{width:.2f}" opacity="{opacity:.2f}" '
        f'stroke-linecap="round" />'
    )


def polygon(points, fill, opacity=1.0):
    pts = " ".join(f"{x:.2f},{y:.2f}" for x, y in points)
    return f'<polygon points="{pts}" fill="{fill}" opacity="{opacity:.2f}" />'


def spiral_path(cx, cy, turns, radius, stroke, width=1.5, opacity=0.9, points_per_turn=40):
    """A logarithmic-ish spiral built as a polyline. Used to represent loops."""
    total_points = int(turns * points_per_turn)
    if total_points < 2:
        return ""
    pts = []
    for i in range(total_points + 1):
        t = i / points_per_turn
        angle = t * 2 * math.pi
        r = radius * (t / max(turns, 0.001))
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        pts.append(f"{x:.2f},{y:.2f}")
    return (
        f'<polyline points="{" ".join(pts)}" fill="none" '
        f'stroke="{stroke}" stroke-width="{width:.2f}" opacity="{opacity:.2f}" '
        f'stroke-linecap="round" />'
    )


def branch(cx, cy, angle, length, stroke, width=1.2, opacity=0.85):
    """A single limb radiating from a point. Used to represent if/else branches."""
    x2 = cx + length * math.cos(angle)
    y2 = cy + length * math.sin(angle)
    return line(cx, cy, x2, y2, stroke, width, opacity), (x2, y2)


def text_label(x, y, content, fill, size=11, anchor="start", opacity=0.6):
    safe = (
        content.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    return (
        f'<text x="{x:.2f}" y="{y:.2f}" fill="{fill}" font-size="{size}" '
        f'font-family="monospace" text-anchor="{anchor}" opacity="{opacity:.2f}">'
        f"{safe}</text>"
    )
