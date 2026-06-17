import xml.dom.minidom as minidom
from clerk.data import DossierData
from clerk.render_seal import render_seal

def test_render_seal_writes_valid_svg_with_no_text_elements(tmp_path):
    data = DossierData(rev=47, seal="9F2C", filed="2026·06·16")
    render_seal(data, out_dir=str(tmp_path))
    svg = (tmp_path / "seal.svg").read_text(encoding="utf-8")
    minidom.parseString(svg)              # well-formed
    assert "<text" not in svg             # outlined, not live text
    assert "<path" in svg                 # glyphs present
    assert svg.strip().endswith("</svg>")
    assert "<rect" in svg
    assert 'fill="none"' in svg
    assert "aria-label=" in svg


def test_render_seal_escapes_special_chars(tmp_path):
    from clerk.data import DossierData
    data = DossierData(rev=1, seal='A"B', filed="x&y")
    render_seal(data, out_dir=str(tmp_path))
    svg = (tmp_path / "seal.svg").read_text(encoding="utf-8")
    import xml.dom.minidom as minidom
    minidom.parseString(svg)            # must stay well-formed
    assert "&quot;" in svg and "&amp;" in svg
