import math
import os
from clerk.svgtext import MonoFont, outline_text

FONT = "clerk/fonts/JetBrainsMono-Regular.ttf"


def _svg(width, height, body, bg):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">'
        f'<rect width="{width}" height="{height}" fill="{bg}"/>{body}</svg>'
    )


def render_header(cfg, out_dir: str, font_path: str = FONT) -> None:
    font = MonoFont(font_path, size=14)
    text = cfg.classification["light"]
    pad = 14
    width = math.ceil(font.text_width(text) + pad * 2)
    height = 30
    os.makedirs(out_dir, exist_ok=True)

    # light: clean banner, dark ink on transparent
    light_glyphs = outline_text(font, text, x=pad, baseline=20, fill="#111111")
    with open(os.path.join(out_dir, "header-light.svg"), "w", encoding="utf-8") as fh:
        fh.write(_svg(width, height, light_glyphs, "none"))

    # dark: light ink, plus opaque redaction bars over configured words + stencil
    dark_glyphs = outline_text(font, text, x=pad, baseline=20, fill="#d8d8d8")
    bars = ""
    for word in cfg.classification.get("redact", []):
        idx = text.find(word)
        if idx < 0:
            continue
        x = pad + idx * font.advance
        w = len(word) * font.advance
        bars += (f'<rect x="{x:.1f}" y="7" width="{w:.1f}" height="17" '
                 f'fill="#000000"/>')
    stencil = cfg.classification.get("stencil", "")
    stencil_glyphs = ""
    if stencil:
        sfont = MonoFont(font_path, size=10)
        sx = width - sfont.text_width(stencil) - pad
        stencil_glyphs = outline_text(sfont, stencil, x=sx, baseline=20, fill="#7a2a2a")
    body = dark_glyphs + bars + stencil_glyphs
    with open(os.path.join(out_dir, "header-dark.svg"), "w", encoding="utf-8") as fh:
        fh.write(_svg(width, height, body, "none"))
