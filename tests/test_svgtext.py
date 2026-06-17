from clerk.svgtext import MonoFont, outline_text

FONT = "clerk/fonts/JetBrainsMono-Regular.ttf"

def test_monospace_advance_is_uniform():
    f = MonoFont(FONT, size=16)
    assert f.text_width("AAAA") == f.advance * 4
    assert f.advance > 0
    # JetBrains Mono advance width is 600 units; at size=16 with upm=1000:
    # advance = 16 * 600/1000 = 9.6
    assert abs(f.advance - 9.6) < 0.01
    assert abs(f.text_width("AAAA") - 38.4) < 0.01

def test_outline_text_emits_one_path_per_visible_glyph():
    f = MonoFont(FONT, size=16)
    svg = outline_text(f, "AB", x=0, baseline=20)
    assert svg.count("<path") == 2
    assert "transform=" in svg and 'd="' in svg

def test_space_emits_no_path_but_advances():
    f = MonoFont(FONT, size=16)
    svg = outline_text(f, "A B", x=0, baseline=20)
    assert svg.count("<path") == 2  # space draws nothing

def test_outline_text_honors_x_offset():
    f = MonoFont(FONT, size=16)
    svg = outline_text(f, "A", x=10, baseline=0)
    assert "translate(10.00," in svg

def test_fill_is_escaped():
    f = MonoFont(FONT, size=16)
    fill_val = 'r"x'
    svg = outline_text(f, "A", x=0, baseline=0, fill=fill_val)
    assert "&quot;" in svg
    assert 'fill="r"x"' not in svg
