from clerk.svgtext import MonoFont, outline_text

FONT = "clerk/fonts/JetBrainsMono-Regular.ttf"

def test_monospace_advance_is_uniform():
    f = MonoFont(FONT, size=16)
    assert f.text_width("AAAA") == f.advance * 4
    assert f.advance > 0

def test_outline_text_emits_one_path_per_visible_glyph():
    f = MonoFont(FONT, size=16)
    svg = outline_text(f, "AB", x=0, baseline=20)
    assert svg.count("<path") == 2
    assert "transform=" in svg and 'd="' in svg

def test_space_emits_no_path_but_advances():
    f = MonoFont(FONT, size=16)
    svg = outline_text(f, "A B", x=0, baseline=20)
    assert svg.count("<path") == 2  # space draws nothing
