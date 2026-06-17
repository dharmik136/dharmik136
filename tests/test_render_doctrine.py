import xml.dom.minidom as minidom
from clerk.config import Config
from clerk.render_doctrine import render_doctrine

def _cfg():
    return Config(doctrine=["Decide what to defend first; write second.",
                            "Specificity is the only luxury that scales.",
                            "Write the small tool the workflow lacks."],
                  refs=[], channels={}, classification={}, dormant_days=30,
                  field_log_len=5, user="dharmik136")

def test_doctrine_uses_smil_freeze_and_does_not_loop(tmp_path):
    render_doctrine(_cfg(), out_dir=str(tmp_path))
    svg = (tmp_path / "doctrine-light.svg").read_text(encoding="utf-8")
    minidom.parseString(svg)
    assert "<animate" in svg                 # SMIL present
    assert 'fill="freeze"' in svg            # holds final frame
    # only the cursor blink repeats (one per line); the text reveal freezes
    assert svg.count("repeatCount") == len(_cfg().doctrine)
    assert "<text" not in svg                # outlined

def test_doctrine_writes_dark_variant(tmp_path):
    render_doctrine(_cfg(), out_dir=str(tmp_path))
    assert (tmp_path / "doctrine-dark.svg").exists()
