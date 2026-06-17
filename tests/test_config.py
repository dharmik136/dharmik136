from clerk.config import load_config

def test_load_config_parses_sections(tmp_path):
    p = tmp_path / "dossier.yaml"
    p.write_text(
        "doctrine:\n  - one\n  - two\n  - three\n"
        "refs:\n"
        "  - {ref: DRS-001, title: claude-enter, domain: workflow, repo: dharmik136/claude-enter}\n"
        "  - {ref: DRS-003, title: ITSM brief, domain: ITSM, manual_status: DRAFTING}\n"
        "classification:\n  light: 'UNCLASSIFIED // FIELD FILE'\n  redact: ['SHINGALA']\n"
        "clerk:\n  dormant_days: 30\n  field_log_len: 5\n",
        encoding="utf-8",
    )
    cfg = load_config(str(p))
    assert cfg.doctrine == ["one", "two", "three"]
    assert cfg.refs[0]["repo"] == "dharmik136/claude-enter"
    assert cfg.refs[1]["manual_status"] == "DRAFTING"
    assert cfg.dormant_days == 30
    assert cfg.field_log_len == 5
    assert cfg.classification["light"].startswith("UNCLASSIFIED")
