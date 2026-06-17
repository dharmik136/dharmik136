import math
import os
from xml.sax.saxutils import escape
from clerk.svgtext import MonoFont, outline_text

FONT = "clerk/fonts/JetBrainsMono-Regular.ttf"


def render_status(refs, out_dir: str, font_path: str = FONT) -> None:
    font = MonoFont(font_path, size=12)
    os.makedirs(out_dir, exist_ok=True)
    for ref in refs:
        pad = 8
        width = math.ceil(font.text_width(ref.status_text) + pad * 2)
        height = 22
        glyphs = outline_text(font, ref.status_text, x=pad, baseline=15, fill="#111111")
        overprint = ""
        if ref.dormant:
            overprint = (
                f'<g transform="rotate(-8 {width/2:.0f} {height/2:.0f})" opacity="0.45"'
                f' aria-label="DORMANT">'
                + outline_text(font, "DORMANT", x=pad, baseline=15, fill="#7a2a2a")
                + "</g>"
            )
        aria = escape(ref.status_text, {'"': "&quot;"})
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" aria-label="{aria}">'
            f'{glyphs}{overprint}</svg>'
        )
        with open(os.path.join(out_dir, f"status-{ref.ref}.svg"), "w", encoding="utf-8") as fh:
            fh.write(svg)
