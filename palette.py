"""
palette.py
----------
Turns a CodeSignature into a small deterministic color palette + "mood".

Same source file -> same palette, always (it's seeded off the sha256
digest of the source, not off randomness). Different code -> a
genuinely different palette, because the seed and the structural
numbers both feed the hue math.
"""

import colorsys
from dataclasses import dataclass


@dataclass
class Palette:
    background: str
    primary: str
    secondary: str
    accent: str
    line: str
    mood: str


def _hex(r, g, b) -> str:
    return "#{:02x}{:02x}{:02x}".format(
        max(0, min(255, int(r * 255))),
        max(0, min(255, int(g * 255))),
        max(0, min(255, int(b * 255))),
    )


def _seed_float(digest: str, offset: int, span: int = 8) -> float:
    """Pull a stable pseudo-random float in [0, 1) out of the hex digest."""
    chunk = digest[offset: offset + span] or "0"
    return int(chunk, 16) / (16 ** span)


def build_palette(sig) -> Palette:
    d = sig.digest or "0" * 64

    base_hue = _seed_float(d, 0)
    hue_spread = 0.08 + 0.25 * _seed_float(d, 8)

    # Structure nudges the mood:
    # more loops -> warmer / more saturated ("energetic")
    # more branches -> cooler / higher contrast ("intricate")
    # deep nesting -> darker background ("dense")
    loop_bias = min(1.0, sig.loop_count / 12.0)
    branch_bias = min(1.0, sig.branch_count / 12.0)
    depth_bias = min(1.0, sig.max_depth / 10.0)

    hue = (base_hue + 0.15 * loop_bias - 0.10 * branch_bias) % 1.0
    sat = 0.45 + 0.4 * loop_bias
    light_bg = 0.12 + 0.10 * (1 - depth_bias)

    bg_r, bg_g, bg_b = colorsys.hls_to_rgb(hue, light_bg, 0.35)
    pr_r, pr_g, pr_b = colorsys.hls_to_rgb((hue + hue_spread) % 1.0, 0.55, sat)
    se_r, se_g, se_b = colorsys.hls_to_rgb((hue - hue_spread) % 1.0, 0.6, sat * 0.8)
    ac_r, ac_g, ac_b = colorsys.hls_to_rgb((hue + 0.5) % 1.0, 0.65, min(1.0, sat + 0.2))
    ln_r, ln_g, ln_b = colorsys.hls_to_rgb(hue, 0.85, 0.25)

    if depth_bias > 0.6:
        mood = "dense"
    elif loop_bias > branch_bias and loop_bias > 0.3:
        mood = "energetic"
    elif branch_bias > 0.3:
        mood = "intricate"
    elif sig.complexity < 3:
        mood = "minimal"
    else:
        mood = "balanced"

    return Palette(
        background=_hex(bg_r, bg_g, bg_b),
        primary=_hex(pr_r, pr_g, pr_b),
        secondary=_hex(se_r, se_g, se_b),
        accent=_hex(ac_r, ac_g, ac_b),
        line=_hex(ln_r, ln_g, ln_b),
        mood=mood,
    )
