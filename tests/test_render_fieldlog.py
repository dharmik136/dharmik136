from clerk.data import LogEntry
from clerk.render_fieldlog import render_fieldlog

def test_fieldlog_markdown_newest_first_with_sub_decay():
    entries = [LogEntry("2026·06·16", "claude-enter · 3 commits"),
               LogEntry("2026·06·12", "content · released v1")]
    md = render_fieldlog(entries)
    lines = [l for l in md.splitlines() if l.strip()]
    assert "2026·06·16" in lines[0]
    assert "<sub>" in lines[1]
    assert "color" not in md and "style=" not in md   # sanitizer-safe
    assert md.startswith("`") or "`" in lines[0]       # monospace via inline code

def test_fieldlog_empty_is_placeholder():
    assert "no recent" in render_fieldlog([]).lower()
