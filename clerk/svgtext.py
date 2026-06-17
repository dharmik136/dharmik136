from xml.sax.saxutils import escape

from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen


class MonoFont:
    """A monospace TTF wrapper that outlines glyphs to SVG path data."""

    def __init__(self, path: str, size: float):
        ttf = TTFont(path)
        self.size = size
        self.upm = ttf["head"].unitsPerEm
        self.cmap = ttf.getBestCmap()
        self.glyphset = ttf.getGlyphSet()
        self.scale = size / self.upm
        # monospace: every advance equals 'M' advance width
        m_glyph = self.cmap.get(ord("M"))
        if m_glyph is None:
            raise ValueError(f"Font {path!r} has no 'M' glyph; cannot determine monospace advance.")
        self.advance = ttf["hmtx"][m_glyph][0] * self.scale

    def text_width(self, text: str) -> float:
        return self.advance * len(text)

    def char_path(self, ch: str) -> str:
        gname = self.cmap.get(ord(ch))
        if gname is None:
            return ""
        pen = SVGPathPen(self.glyphset)
        self.glyphset[gname].draw(pen)
        return pen.getCommands()


def outline_text(font: MonoFont, text: str, x: float, baseline: float,
                 fill: str = "#111111") -> str:
    """Return SVG <path> markup for `text` laid out monospaced from x at baseline.

    Font units are y-up; each glyph is translated into place and flipped via
    a negative y-scale so it renders correctly in SVG's y-down space.
    """
    safe_fill = escape(fill, {'"': "&quot;"})
    parts = []
    for i, ch in enumerate(text):
        if ch == " ":
            continue
        d = font.char_path(ch)
        if not d:
            continue
        # .2f rounding is within SVG sub-pixel tolerance; exact integer accumulation is unnecessary.
        gx = x + i * font.advance
        parts.append(
            f'<path transform="translate({gx:.2f},{baseline:.2f}) '
            f'scale({font.scale:.5f},{-font.scale:.5f})" d="{d}" fill="{safe_fill}"/>'
        )
    return "".join(parts)
