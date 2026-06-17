from clerk.data import seal_hash, ref_status_from_signals, log_entries_from_events, rev_count

def test_seal_hash_strips_dynamic_blocks_and_is_stable():
    a = "x\n<!--FOOTER:START-->\nf1\n<!--FOOTER:END-->\n<!--FIELDLOG:START-->\nl1\n<!--FIELDLOG:END-->\n"
    b = "x\n<!--FOOTER:START-->\nDIFFERENT\n<!--FOOTER:END-->\n<!--FIELDLOG:START-->\nALSO DIFF\n<!--FIELDLOG:END-->\n"
    assert seal_hash(a) == seal_hash(b)
    assert len(seal_hash(a)) == 4

def test_ref_status_marks_dormant_past_threshold():
    fresh = ref_status_from_signals(
        {"ref": "DRS-001", "title": "x", "domain": "d", "repo": "o/r"},
        signals={"release": "v0.1.0", "days_since_push": 3}, dormant_days=30)
    assert fresh.dormant is False
    assert "SHIPPED v0.1.0" in fresh.status_text

    stale = ref_status_from_signals(
        {"ref": "DRS-002", "title": "y", "domain": "d", "repo": "o/r"},
        signals={"release": None, "days_since_push": 90}, dormant_days=30)
    assert stale.dormant is True

def test_manual_status_ref_bypasses_signals():
    s = ref_status_from_signals(
        {"ref": "DRS-003", "title": "z", "domain": "d", "manual_status": "DRAFTING"},
        signals=None, dormant_days=30)
    assert s.status_text == "DRAFTING"
    assert s.dormant is False

def test_log_entries_phrase_push_events():
    events = [
        {"type": "PushEvent", "repo": {"name": "dharmik136/claude-enter"},
         "created_at": "2026-06-16T10:00:00Z", "payload": {"size": 3}},
        {"type": "ReleaseEvent", "repo": {"name": "dharmik136/x"},
         "created_at": "2026-06-15T10:00:00Z", "payload": {"release": {"tag_name": "v1"}}},
        {"type": "WatchEvent", "repo": {"name": "dharmik136/y"},
         "created_at": "2026-06-14T10:00:00Z", "payload": {}},
    ]
    entries = log_entries_from_events(events, limit=5)
    assert len(entries) == 2
    assert entries[0].date == "2026·06·16"
    assert "3 commits" in entries[0].summary
    assert "claude-enter" in entries[0].summary

def test_rev_count_excludes_bot_commits(monkeypatch):
    import clerk.data as d
    monkeypatch.setattr(d, "_git", lambda args: "Alice\ndossier-clerk[bot]\nBob\ndossier-clerk[bot]\nAlice")
    assert d.rev_count() == 3

def test_ref_status_none_signals_is_unknown():
    s = ref_status_from_signals({"ref": "DRS-9", "title": "t", "domain": "d"}, None, 30)
    assert s.status_text == "UNKNOWN" and s.dormant is False

def test_log_entries_release_event_phrasing():
    events = [{"type": "ReleaseEvent", "repo": {"name": "o/proj"},
               "created_at": "2026-06-15T10:00:00Z",
               "payload": {"release": {"tag_name": "v1.2"}}}]
    e = log_entries_from_events(events, limit=5)
    assert e[0].summary == "proj · released v1.2"

def test_log_entries_respects_limit():
    events = [{"type": "PushEvent", "repo": {"name": "o/a"},
               "created_at": "2026-06-16T10:00:00Z", "payload": {"size": 1}}] * 4
    assert len(log_entries_from_events(events, limit=2)) == 2
