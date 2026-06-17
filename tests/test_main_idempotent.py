from clerk import data as data_mod
from clerk.config import load_config
from clerk.data import DossierData, RefStatus, LogEntry
from clerk.main import run

README = """\
# file
<!--FOOTER:START-->
old footer
<!--FOOTER:END-->
<!--FIELDLOG:START-->
old log
<!--FIELDLOG:END-->
"""

CFG_YAML = (
    "user: dharmik136\n"
    "doctrine: [a, b, c]\n"
    "refs:\n  - {ref: DRS-003, title: t, domain: d, manual_status: DRAFTING}\n"
    "classification: {light: 'X', redact: [], stencil: ''}\n"
    "clerk: {dormant_days: 30, field_log_len: 5}\n"
)

def test_run_is_idempotent(tmp_path, monkeypatch):
    repo = tmp_path
    (repo / "README.md").write_text(README, encoding="utf-8")
    (repo / "dossier.yaml").write_text(CFG_YAML, encoding="utf-8")
    (repo / "assets").mkdir()

    fixed = DossierData(rev=47, seal="9F2C", filed="2026·06·16",
                        refs=[RefStatus("DRS-003", "t", "d", "DRAFTING", False)],
                        field_log=[LogEntry("2026·06·16", "claude-enter · 3 commits")])
    monkeypatch.setattr("clerk.main.gather", lambda cfg, txt, token: fixed)

    run(repo_dir=str(repo), token="x")
    first = (repo / "README.md").read_text(encoding="utf-8")
    run(repo_dir=str(repo), token="x")
    second = (repo / "README.md").read_text(encoding="utf-8")
    assert first == second           # no churn on second run
    assert "2026·06·16" in first     # field log written
    assert (repo / "assets" / "seal.svg").exists()
    assert (repo / "assets" / "doctrine-light.svg").exists()
    assert (repo / "assets" / "status-DRS-003.svg").exists()
