import math
import os
from clerk.svgtext import MonoFont, outline_text

FONT = "clerk/fonts/JetBrainsMono-Regular.ttf"
LINE_H = 26
PAD = 16
TYPE_SECS = 1.6     # per line reveal duration
CURSOR_W = 9


def _variant(cfg, font, ink, cursor_fill):
    lines = cfg.doctrine
    width = math.ceil(max(font.text_width(s) for s in lines) + PAD * 2 + CURSOR_W)
    height = PAD * 2 + LINE_H * len(lines)
    body = []
    for i, line in enumerate(lines):
        baseline = PAD + LINE_H * (i + 1) - 8
        begin = i * TYPE_SECS
        line_w = font.text_width(line)
        clip_id = f"clip{i}"
        glyphs = outline_text(font, line, x=PAD, baseline=baseline, fill=ink)
        body.append(
            f'<clipPath id="{clip_id}"><rect x="{PAD}" y="{baseline-LINE_H+6}" '
            f'height="{LINE_H + 2}" width="0">'
            f'<animate attributeName="width" from="0" to="{line_w:.1f}" '
            f'begin="{begin:.2f}s" dur="{TYPE_SECS}s" fill="freeze"/>'
            f'</rect></clipPath>'
            f'<g clip-path="url(#{clip_id})">{glyphs}</g>'
        )
        cx_end = PAD + line_w
        body.append(
            f'<rect y="{baseline-LINE_H+8}" width="{CURSOR_W}" height="{LINE_H-6}" '
            f'fill="{cursor_fill}" x="{PAD:.1f}">'
            f'<animate attributeName="x" from="{PAD:.1f}" to="{cx_end:.1f}" '
            f'begin="{begin:.2f}s" dur="{TYPE_SECS}s" fill="freeze"/>'
            f'<animate attributeName="opacity" values="1;0;1" dur="1s" '
            f'begin="{(begin+TYPE_SECS):.2f}s" repeatCount="indefinite"/>'
            f'</rect>'
        )
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">' + "".join(body) + "</svg>"
    )
    return svg


def render_doctrine(cfg, out_dir: str, font_path: str = FONT) -> None:
    font = MonoFont(font_path, size=15)
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "doctrine-light.svg"), "w", encoding="utf-8") as fh:
        fh.write(_variant(cfg, font, ink="#111111", cursor_fill="#111111"))
    with open(os.path.join(out_dir, "doctrine-dark.svg"), "w", encoding="utf-8") as fh:
        fh.write(_variant(cfg, font, ink="#d8d8d8", cursor_fill="#d8d8d8"))
