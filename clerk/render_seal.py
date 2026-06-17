import os
from clerk.svgtext import MonoFont, outline_text

FONT = "clerk/fonts/JetBrainsMono-Regular.ttf"


def render_seal(data, out_dir: str, font_path: str = FONT) -> None:
    font = MonoFont(font_path, size=15)
    line = f"ENTRY No.1 · REV {data.rev} · SEAL {data.seal} · FILED {data.filed}"
    pad = 18
    width = int(font.text_width(line) + pad * 2)
    height = 40
    glyphs = outline_text(font, line, x=pad, baseline=26, fill="#111111")
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" '
        f'aria-label="{line}">'
        f'<rect x="1" y="1" width="{width-2}" height="{height-2}" rx="3" '
        f'fill="none" stroke="#111111" stroke-width="1.5"/>'
        f'{glyphs}</svg>'
    )
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "seal.svg"), "w", encoding="utf-8") as fh:
        fh.write(svg)
