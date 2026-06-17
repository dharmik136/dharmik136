import pytest

from clerk.markers import replace_section

DOC = "a\n<!--FOO:START-->\nold\n<!--FOO:END-->\nb\n"

def test_replace_section_swaps_inner_keeps_markers():
    out = replace_section(DOC, "FOO", "new")
    assert "<!--FOO:START-->" in out and "<!--FOO:END-->" in out
    assert "new" in out and "old" not in out
    assert out.startswith("a\n") and out.rstrip().endswith("b")

def test_replace_section_is_idempotent():
    once = replace_section(DOC, "FOO", "new")
    twice = replace_section(once, "FOO", "new")
    assert once == twice

def test_missing_marker_raises():
    with pytest.raises(ValueError):
        replace_section("no markers here", "FOO", "new")

def test_replace_section_preserves_backslash_sequences():
    out = replace_section(DOC, "FOO", r"a\1b")
    assert r"a\1b" in out

def test_replace_section_multiline_inner():
    inner = "line1\nline2\nline3"
    out = replace_section(DOC, "FOO", inner)
    assert "<!--FOO:START-->\nline1\nline2\nline3\n<!--FOO:END-->" in out
