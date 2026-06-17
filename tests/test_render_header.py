import xml.dom.minidom as minidom
from clerk.config import Config
from clerk.render_header import render_header

def _cfg():
    return Config(doctrine=[], refs=[], channels={},
                  classification={"light": "UNCLASSIFIED // FIELD FILE — SHINGALA, D.",
                                  "redact": ["SHINGALA", "FIELD"], "stencil": "CONFIDENTIAL"},
                  dormant_days=30, field_log_len=5, user="dharmik136")

def test_render_header_writes_both_variants(tmp_path):
    render_header(_cfg(), out_dir=str(tmp_path))
    light = (tmp_path / "header-light.svg").read_text(encoding="utf-8")
    dark = (tmp_path / "header-dark.svg").read_text(encoding="utf-8")
    for svg in (light, dark):
        minidom.parseString(svg)
        assert "<text" not in svg
    # dark variant carries redaction bars; light does not
    assert dark.count("<rect") > light.count("<rect")
