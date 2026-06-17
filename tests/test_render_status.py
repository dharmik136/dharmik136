import xml.dom.minidom as minidom
from clerk.data import RefStatus
from clerk.render_status import render_status

def test_render_status_writes_one_svg_per_ref(tmp_path):
    refs = [RefStatus("DRS-001", "claude-enter", "workflow", "SHIPPED v0.1.0 · last activity 3d", False),
            RefStatus("DRS-002", "content", "ops", "ACTIVE · last activity 90d", True)]
    render_status(refs, out_dir=str(tmp_path))
    a = (tmp_path / "status-DRS-001.svg").read_text(encoding="utf-8")
    b = (tmp_path / "status-DRS-002.svg").read_text(encoding="utf-8")
    minidom.parseString(a); minidom.parseString(b)
    assert "DORMANT" not in a
    assert "DORMANT" in b          # stale ref gets the overprint glyphs
    assert "<text" not in a

def test_render_status_escapes_aria(tmp_path):
    refs = [RefStatus("DRS-9", "t", "d", 'a"b & c', False)]
    render_status(refs, out_dir=str(tmp_path))
    svg = (tmp_path / "status-DRS-9.svg").read_text(encoding="utf-8")
    minidom.parseString(svg)       # well-formed despite quote/amp
    assert "&quot;" in svg and "&amp;" in svg
