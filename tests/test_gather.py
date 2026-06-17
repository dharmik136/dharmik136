import clerk.data as d
from clerk.config import Config

def _cfg(refs):
    return Config(doctrine=[], refs=refs, channels={}, classification={},
                  dormant_days=30, field_log_len=5, user="u")

def test_gather_happy_path(monkeypatch):
    monkeypatch.setattr(d, "fetch_repo_signals", lambda repo, token: {"release": "v1", "days_since_push": 2})
    monkeypatch.setattr(d, "fetch_public_events", lambda user, token: [
        {"type": "PushEvent", "repo": {"name": "u/r"}, "created_at": "2026-06-16T00:00:00Z", "payload": {"size": 1}}])
    monkeypatch.setattr(d, "rev_count", lambda: 10)
    monkeypatch.setattr(d, "last_content_commit_date", lambda: "2026·06·16")
    data = d.gather(_cfg([{"ref": "DRS-1", "title": "t", "domain": "x", "repo": "u/r"}]), "readme", "tok")
    assert data.refs[0].status_text.startswith("SHIPPED v1")
    assert len(data.field_log) == 1 and data.rev == 10

def test_gather_isolates_repo_fetch_failure(monkeypatch):
    def boom(repo, token): raise RuntimeError("404")
    monkeypatch.setattr(d, "fetch_repo_signals", boom)
    monkeypatch.setattr(d, "fetch_public_events", lambda user, token: [])
    monkeypatch.setattr(d, "rev_count", lambda: 1)
    monkeypatch.setattr(d, "last_content_commit_date", lambda: "2026·06·16")
    data = d.gather(_cfg([{"ref": "DRS-1", "title": "t", "domain": "x", "repo": "u/r"}]), "readme", "tok")
    assert data.refs[0].status_text == "UNKNOWN"     # fell back, did not crash

def test_gather_isolates_events_failure(monkeypatch):
    def boom(user, token): raise RuntimeError("403 rate limit")
    monkeypatch.setattr(d, "fetch_public_events", boom)
    monkeypatch.setattr(d, "rev_count", lambda: 1)
    monkeypatch.setattr(d, "last_content_commit_date", lambda: "2026·06·16")
    data = d.gather(_cfg([{"ref": "DRS-3", "title": "t", "domain": "x", "manual_status": "DRAFTING"}]), "readme", "tok")
    assert data.field_log == []                       # empty, did not crash
    assert data.refs[0].status_text == "DRAFTING"
