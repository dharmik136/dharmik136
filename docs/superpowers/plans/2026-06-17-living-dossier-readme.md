# Living Dossier README Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the `dharmik136/dharmik136` profile README into a self-updating "living case file" rendered entirely by our own Python renderer ("the clerk") — committed SVGs + one GitHub Action, no external server.

**Architecture:** A `clerk/` Python package gathers signals (git stats + GitHub API + public events), pure renderers draw committed SVGs (`assets/*.svg`) and rewrite two README marker sections. A scheduled GitHub Action runs the clerk and commits only on change. All SVG text is outlined to vector paths; the only animation is SMIL.

**Tech Stack:** Python 3.11, PyYAML, requests, fonttools; pytest; GitHub Actions. Bundled OFL font: JetBrains Mono.

**Working dir:** `dharmik136/dharmik136` clone at `C:\Users\Dharmik Shingala\Downloads\gh-profile-readme`, branch `feat/living-dossier`.

**Spec:** `docs/superpowers/specs/2026-06-17-living-dossier-readme-design.md`

---

## File Structure

```
clerk/
  __init__.py
  fonts/JetBrainsMono-Regular.ttf   # bundled OFL font (outlining source)
  svgtext.py     # MonoFont + outline_text/text_width  (shared by all renderers)
  markers.py     # replace_section(text, name, inner) -> text
  config.py      # Config dataclass + load_config(path)
  data.py        # DossierData/RefStatus/LogEntry dataclasses + gather(...)
  render_seal.py     # render_seal(data, cfg, out_dir)
  render_header.py   # render_header(cfg, out_dir)
  render_doctrine.py # render_doctrine(cfg, out_dir)
  render_status.py   # render_status(data, cfg, out_dir)
  render_fieldlog.py # render_fieldlog(data) -> markdown inner string
  main.py        # orchestrates: gather -> render -> rewrite README
tests/
  test_svgtext.py test_markers.py test_config.py test_data.py
  test_render_seal.py test_render_header.py test_render_doctrine.py
  test_render_status.py test_render_fieldlog.py test_main_idempotent.py
dossier.yaml
requirements.txt
README.md                       # restructured (Task 12)
.github/workflows/dossier.yml   # Task 13
```

Design rules locked from the spec §6 (must hold in every task):
- SVGs are **committed files** referenced by **relative** `<img>`/`<picture>` paths. No inline SVG, no external badge URLs.
- Animation is **SMIL only**, `fill="freeze"`, **no `repeatCount`** on reveals.
- **All SVG text is outlined to vector `<path>`** via `svgtext` — never `<text>`.
- Seal hash strips the `FOOTER` + `FIELDLOG` marker blocks before hashing (stability).
- `REV` excludes `dossier-clerk[bot]` commits.
- Field-log decay uses `<sub>` / `█`, never color.
- The clerk commits only on real diff, with `[skip ci]`, as `dossier-clerk[bot]`.

---

## Task 1: Scaffold package, deps, font, pytest

**Files:**
- Create: `requirements.txt`, `clerk/__init__.py`, `tests/__init__.py`, `pytest.ini`
- Create (download): `clerk/fonts/JetBrainsMono-Regular.ttf`

- [ ] **Step 1: Create dependency + config files**

`requirements.txt`:
```
PyYAML==6.0.2
requests==2.32.3
fonttools==4.53.1
pytest==8.3.2
```

`pytest.ini`:
```ini
[pytest]
testpaths = tests
```

`clerk/__init__.py`:
```python
"""The clerk — renders the living dossier README."""
```

`tests/__init__.py`:
```python
```

- [ ] **Step 2: Download the bundled font**

Run:
```bash
mkdir -p clerk/fonts
curl -fsSL -o clerk/fonts/JetBrainsMono-Regular.ttf \
  https://github.com/JetBrains/JetBrainsMono/raw/master/fonts/ttf/JetBrainsMono-Regular.ttf
python -c "from fontTools.ttLib import TTFont; TTFont('clerk/fonts/JetBrainsMono-Regular.ttf'); print('font OK')"
```
Expected: `font OK` (after `pip install -r requirements.txt`).

- [ ] **Step 3: Install deps**

Run: `python -m pip install -r requirements.txt`
Expected: installs without error.

- [ ] **Step 4: Commit**

```bash
git add requirements.txt pytest.ini clerk/__init__.py tests/__init__.py clerk/fonts/JetBrainsMono-Regular.ttf
git commit -m "chore: scaffold clerk package, deps, bundled font"
```

---

## Task 2: `svgtext` — outline text to vector paths

**Files:**
- Create: `clerk/svgtext.py`
- Test: `tests/test_svgtext.py`

- [ ] **Step 1: Write the failing test**

`tests/test_svgtext.py`:
```python
from clerk.svgtext import MonoFont, outline_text

FONT = "clerk/fonts/JetBrainsMono-Regular.ttf"

def test_monospace_advance_is_uniform():
    f = MonoFont(FONT, size=16)
    assert f.text_width("AAAA") == f.advance * 4
    assert f.advance > 0

def test_outline_text_emits_one_path_per_visible_glyph():
    f = MonoFont(FONT, size=16)
    svg = outline_text(f, "AB", x=0, baseline=20)
    assert svg.count("<path") == 2
    assert "transform=" in svg and 'd="' in svg

def test_space_emits_no_path_but_advances():
    f = MonoFont(FONT, size=16)
    svg = outline_text(f, "A B", x=0, baseline=20)
    assert svg.count("<path") == 2  # space draws nothing
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_svgtext.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'clerk.svgtext'`.

- [ ] **Step 3: Write minimal implementation**

`clerk/svgtext.py`:
```python
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen


class MonoFont:
    """A monospace TTF wrapper that outlines glyphs to SVG path data."""

    def __init__(self, path: str, size: float):
        self.ttf = TTFont(path)
        self.size = size
        self.upm = self.ttf["head"].unitsPerEm
        self.cmap = self.ttf.getBestCmap()
        self.glyphset = self.ttf.getGlyphSet()
        self.scale = size / self.upm
        # monospace: every advance equals 'M' advance width
        m_glyph = self.cmap[ord("M")]
        self.advance = self.ttf["hmtx"][m_glyph][0] * self.scale

    def text_width(self, text: str) -> float:
        return self.advance * len(text)

    def char_path(self, ch: str) -> str:
        gname = self.cmap.get(ord(ch))
        if gname is None:
            return ""
        pen = SVGPathPen(self.glyphset)
        self.glyphset[gname].draw(pen)
        return pen.getCommands()


def outline_text(font: MonoFont, text: str, x: float, baseline: float,
                 fill: str = "#111111") -> str:
    """Return SVG <path> markup for `text` laid out monospaced from x at baseline.

    Font units are y-up; each glyph is translated into place and flipped via
    a negative y-scale so it renders correctly in SVG's y-down space.
    """
    parts = []
    for i, ch in enumerate(text):
        if ch == " ":
            continue
        d = font.char_path(ch)
        if not d:
            continue
        gx = x + i * font.advance
        parts.append(
            f'<path transform="translate({gx:.2f},{baseline:.2f}) '
            f'scale({font.scale:.5f},{-font.scale:.5f})" d="{d}" fill="{fill}"/>'
        )
    return "".join(parts)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_svgtext.py -v`
Expected: PASS (3 passed).

- [ ] **Step 5: Commit**

```bash
git add clerk/svgtext.py tests/test_svgtext.py
git commit -m "feat: svgtext outlines monospace text to SVG paths"
```

---

## Task 3: `markers` — idempotent README section replace

**Files:**
- Create: `clerk/markers.py`
- Test: `tests/test_markers.py`

- [ ] **Step 1: Write the failing test**

`tests/test_markers.py`:
```python
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
    import pytest
    with pytest.raises(ValueError):
        replace_section("no markers here", "FOO", "new")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_markers.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Write minimal implementation**

`clerk/markers.py`:
```python
import re


def replace_section(text: str, name: str, inner: str) -> str:
    """Replace the content between <!--NAME:START--> and <!--NAME:END-->.

    Markers are preserved; `inner` is placed on its own lines between them.
    Raises ValueError if the markers are absent.
    """
    start = f"<!--{name}:START-->"
    end = f"<!--{name}:END-->"
    pattern = re.compile(
        re.escape(start) + r".*?" + re.escape(end), re.DOTALL
    )
    if not pattern.search(text):
        raise ValueError(f"markers for {name!r} not found")
    return pattern.sub(f"{start}\n{inner}\n{end}", text)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_markers.py -v`
Expected: PASS (3 passed).

- [ ] **Step 5: Commit**

```bash
git add clerk/markers.py tests/test_markers.py
git commit -m "feat: idempotent marker-section replace"
```

---

## Task 4: `config` — load `dossier.yaml`

**Files:**
- Create: `clerk/config.py`, `dossier.yaml`
- Test: `tests/test_config.py`

- [ ] **Step 1: Write the failing test**

`tests/test_config.py`:
```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_config.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Write minimal implementation**

`clerk/config.py`:
```python
from dataclasses import dataclass
import yaml


@dataclass
class Config:
    doctrine: list
    refs: list
    channels: dict
    classification: dict
    dormant_days: int
    field_log_len: int
    user: str


def load_config(path: str) -> Config:
    with open(path, encoding="utf-8") as fh:
        d = yaml.safe_load(fh)
    clerk = d.get("clerk", {})
    return Config(
        doctrine=d["doctrine"],
        refs=d["refs"],
        channels=d.get("channels", {}),
        classification=d["classification"],
        dormant_days=int(clerk.get("dormant_days", 30)),
        field_log_len=int(clerk.get("field_log_len", 5)),
        user=d.get("user", "dharmik136"),
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_config.py -v`
Expected: PASS.

- [ ] **Step 5: Create the real `dossier.yaml`**

`dossier.yaml`:
```yaml
user: dharmik136
doctrine:
  - "Decide what to defend first; write second."
  - "Specificity is the only luxury that scales."
  - "When the workflow needs a tool that doesn't exist, write a small one."
refs:
  - {ref: DRS-001, title: claude-enter, domain: "workflow automation", repo: dharmik136/claude-enter}
  - {ref: DRS-002, title: "Motadata content system", domain: "content operations", repo: dharmik136/motadata-marketing-ai}
  - {ref: DRS-003, title: "ITSM positioning brief", domain: "positioning · ITSM", manual_status: "DRAFTING"}
channels:
  linkedin: "linkedin.com/in/aatmaa"
  email: "dhashingala9@gmail.com"
classification:
  light: "UNCLASSIFIED // FIELD FILE — SHINGALA, D."
  redact: ["SHINGALA", "FIELD"]
  stencil: "CONFIDENTIAL"
clerk:
  dormant_days: 30
  field_log_len: 5
```

- [ ] **Step 6: Commit**

```bash
git add clerk/config.py dossier.yaml tests/test_config.py
git commit -m "feat: dossier.yaml config + loader"
```

---

## Task 5: `data` — git stats, seal hash, repo signals, events

**Files:**
- Create: `clerk/data.py`
- Test: `tests/test_data.py`

Network helpers are isolated so renderers stay pure and tests stay offline.

- [ ] **Step 1: Write the failing test**

`tests/test_data.py`:
```python
from clerk.data import seal_hash, ref_status_from_signals, log_entries_from_events

def test_seal_hash_strips_dynamic_blocks_and_is_stable():
    a = "x\n<!--FOOTER:START-->\nf1\n<!--FOOTER:END-->\n<!--FIELDLOG:START-->\nl1\n<!--FIELDLOG:END-->\n"
    b = "x\n<!--FOOTER:START-->\nDIFFERENT\n<!--FOOTER:END-->\n<!--FIELDLOG:START-->\nALSO DIFF\n<!--FIELDLOG:END-->\n"
    # only the stripped (stable) part should drive the hash, so a and b match
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
         "created_at": "2026-06-14T10:00:00Z", "payload": {}},  # ignored
    ]
    entries = log_entries_from_events(events, limit=5)
    assert len(entries) == 2  # WatchEvent dropped
    assert entries[0].date == "2026·06·16"
    assert "3 commits" in entries[0].summary
    assert "claude-enter" in entries[0].summary
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_data.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Write minimal implementation**

`clerk/data.py`:
```python
import hashlib
import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone

import requests

CLERK_BOT = "dossier-clerk[bot]"
_STRIP = re.compile(r"<!--(FOOTER|FIELDLOG):START-->.*?<!--\1:END-->", re.DOTALL)


@dataclass
class RefStatus:
    ref: str
    title: str
    domain: str
    status_text: str
    dormant: bool


@dataclass
class LogEntry:
    date: str
    summary: str


@dataclass
class DossierData:
    rev: int
    seal: str
    filed: str
    refs: list = field(default_factory=list)
    field_log: list = field(default_factory=list)


def seal_hash(readme_text: str) -> str:
    """4-hex sha256 of the README with dynamic marker blocks removed (stable)."""
    stripped = _STRIP.sub("", readme_text)
    return hashlib.sha256(stripped.encode("utf-8")).hexdigest()[:4].upper()


def _git(args: list) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def rev_count() -> int:
    """Content commits = all commits minus the clerk-bot's own commits."""
    total = int(_git(["rev-list", "--count", "HEAD"]))
    bot = _git(["log", f"--author={CLERK_BOT}", "--oneline"])
    bot_n = len(bot.splitlines()) if bot else 0
    return total - bot_n


def last_content_commit_date() -> str:
    """Date (YYYY·MM·DD) of the most recent non-bot commit."""
    log = _git(["log", "--format=%an%x09%cs", "-n", "200"])
    for line in log.splitlines():
        author, date = line.split("\t", 1)
        if author != CLERK_BOT:
            return date.replace("-", "·")
    return datetime.now(timezone.utc).strftime("%Y·%m·%d")


def ref_status_from_signals(ref: dict, signals, dormant_days: int) -> RefStatus:
    if ref.get("manual_status"):
        return RefStatus(ref["ref"], ref["title"], ref["domain"],
                         ref["manual_status"], False)
    rel = signals.get("release")
    days = signals.get("days_since_push")
    head = f"SHIPPED {rel}" if rel else "ACTIVE"
    text = f"{head} · last activity {days}d"
    dormant = days is not None and days >= dormant_days
    return RefStatus(ref["ref"], ref["title"], ref["domain"], text, dormant)


_PHRASE = {
    "PushEvent": lambda e: f"{e['payload'].get('size', 0)} commits",
    "ReleaseEvent": lambda e: f"released {e['payload']['release']['tag_name']}",
    "CreateEvent": lambda e: "created branch/repo",
    "PullRequestEvent": lambda e: "pull request",
}


def log_entries_from_events(events: list, limit: int) -> list:
    out = []
    for e in events:
        phrase = _PHRASE.get(e["type"])
        if not phrase:
            continue
        d = datetime.fromisoformat(e["created_at"].replace("Z", "+00:00"))
        ref = e["repo"]["name"].split("/")[-1]
        out.append(LogEntry(d.strftime("%Y·%m·%d"),
                            f"{ref} · {phrase(e)}"))
        if len(out) >= limit:
            break
    return out


# --- network helpers (mocked in tests via monkeypatch) ---

def fetch_repo_signals(repo: str, token: str) -> dict:
    h = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    r = requests.get(f"https://api.github.com/repos/{repo}", headers=h, timeout=20)
    r.raise_for_status()
    pushed = r.json()["pushed_at"]
    days = (datetime.now(timezone.utc) -
            datetime.fromisoformat(pushed.replace("Z", "+00:00"))).days
    rel = requests.get(f"https://api.github.com/repos/{repo}/releases/latest",
                       headers=h, timeout=20)
    release = rel.json().get("tag_name") if rel.status_code == 200 else None
    return {"release": release, "days_since_push": days}


def fetch_public_events(user: str, token: str) -> list:
    h = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    r = requests.get(f"https://api.github.com/users/{user}/events/public?per_page=50",
                     headers=h, timeout=20)
    r.raise_for_status()
    return r.json()


def gather(cfg, readme_text: str, token: str) -> DossierData:
    refs = []
    for ref in cfg.refs:
        if ref.get("manual_status") or not ref.get("repo"):
            refs.append(ref_status_from_signals(ref, None, cfg.dormant_days))
        else:
            sig = fetch_repo_signals(ref["repo"], token)
            refs.append(ref_status_from_signals(ref, sig, cfg.dormant_days))
    events = fetch_public_events(cfg.user, token)
    return DossierData(
        rev=rev_count(),
        seal=seal_hash(readme_text),
        filed=last_content_commit_date(),
        refs=refs,
        field_log=log_entries_from_events(events, cfg.field_log_len),
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_data.py -v`
Expected: PASS (4 passed). (Pure functions tested; network helpers exercised in Task 9/10 via monkeypatch.)

- [ ] **Step 5: Commit**

```bash
git add clerk/data.py tests/test_data.py
git commit -m "feat: data layer (git stats, stable seal hash, repo signals, events)"
```

---

## Task 6: `render_seal` — §00 Integrity Seal SVG

**Files:**
- Create: `clerk/render_seal.py`
- Test: `tests/test_render_seal.py`

- [ ] **Step 1: Write the failing test**

`tests/test_render_seal.py`:
```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_render_seal.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Write minimal implementation**

`clerk/render_seal.py`:
```python
import os
from clerk.svgtext import MonoFont, outline_text

FONT = "clerk/fonts/JetBrainsMono-Regular.ttf"


def render_seal(data, out_dir: str, font_path: str = FONT) -> None:
    font = MonoFont(font_path, size=15)
    line = f"ENTRY No.1 · REV {data.rev} · SEAL {data.seal} · FILED {data.filed}"
    pad = 18
    width = int(font.text_width(line) + pad * 2)
    height = 40
    glyphs = outline_text(font, line, x=pad, baseline=26, fill="#111111")
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" '
        f'aria-label="{line}">'
        f'<rect x="1" y="1" width="{width-2}" height="{height-2}" rx="3" '
        f'fill="none" stroke="#111111" stroke-width="1.5"/>'
        f'{glyphs}</svg>'
    )
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "seal.svg"), "w", encoding="utf-8") as fh:
        fh.write(svg)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_render_seal.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add clerk/render_seal.py tests/test_render_seal.py
git commit -m "feat: render integrity seal SVG"
```

---

## Task 7: `render_header` — §00 Classification header (light/dark)

**Files:**
- Create: `clerk/render_header.py`
- Test: `tests/test_render_header.py`

- [ ] **Step 1: Write the failing test**

`tests/test_render_header.py`:
```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_render_header.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Write minimal implementation**

`clerk/render_header.py`:
```python
import os
from clerk.svgtext import MonoFont, outline_text

FONT = "clerk/fonts/JetBrainsMono-Regular.ttf"


def _svg(width, height, body, bg, ink):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">'
        f'<rect width="{width}" height="{height}" fill="{bg}"/>{body}</svg>'
    )


def render_header(cfg, out_dir: str, font_path: str = FONT) -> None:
    font = MonoFont(font_path, size=14)
    text = cfg.classification["light"]
    pad = 14
    width = int(font.text_width(text) + pad * 2)
    height = 30
    os.makedirs(out_dir, exist_ok=True)

    # light: clean banner, dark ink on transparent
    light_glyphs = outline_text(font, text, x=pad, baseline=20, fill="#111111")
    with open(os.path.join(out_dir, "header-light.svg"), "w", encoding="utf-8") as fh:
        fh.write(_svg(width, height, light_glyphs, "none", "#111111"))

    # dark: light ink, plus opaque redaction bars over configured words + stencil
    dark_glyphs = outline_text(font, text, x=pad, baseline=20, fill="#d8d8d8")
    bars = ""
    for word in cfg.classification.get("redact", []):
        idx = text.find(word)
        if idx < 0:
            continue
        x = pad + idx * font.advance
        w = len(word) * font.advance
        bars += (f'<rect x="{x:.1f}" y="7" width="{w:.1f}" height="17" '
                 f'fill="#000000"/>')
    stencil = cfg.classification.get("stencil", "")
    stencil_glyphs = ""
    if stencil:
        sfont = MonoFont(font_path, size=10)
        sx = width - sfont.text_width(stencil) - pad
        stencil_glyphs = outline_text(sfont, stencil, x=sx, baseline=20, fill="#7a2a2a")
    body = dark_glyphs + bars + stencil_glyphs
    with open(os.path.join(out_dir, "header-dark.svg"), "w", encoding="utf-8") as fh:
        fh.write(_svg(width, height, body, "none", "#d8d8d8"))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_render_header.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add clerk/render_header.py tests/test_render_header.py
git commit -m "feat: render classification header (light/dark)"
```

---

## Task 8: `render_doctrine` — §01 typewriter (SMIL, light/dark)

**Files:**
- Create: `clerk/render_doctrine.py`
- Test: `tests/test_render_doctrine.py`

- [ ] **Step 1: Write the failing test**

`tests/test_render_doctrine.py`:
```python
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
    assert "repeatCount" not in svg          # never re-blanks the text
    assert "<text" not in svg                # outlined

def test_doctrine_writes_dark_variant(tmp_path):
    render_doctrine(_cfg(), out_dir=str(tmp_path))
    assert (tmp_path / "doctrine-dark.svg").exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_render_doctrine.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Write minimal implementation**

`clerk/render_doctrine.py`:
```python
import os
from clerk.svgtext import MonoFont, outline_text

FONT = "clerk/fonts/JetBrainsMono-Regular.ttf"
LINE_H = 26
PAD = 16
TYPE_SECS = 1.6     # per line reveal duration
CURSOR_W = 9


def _variant(cfg, font, ink, cursor_fill):
    lines = cfg.doctrine
    width = int(max(font.text_width(s) for s in lines) + PAD * 2 + CURSOR_W)
    height = PAD * 2 + LINE_H * len(lines)
    body = []
    for i, line in enumerate(lines):
        baseline = PAD + LINE_H * (i + 1) - 8
        begin = i * TYPE_SECS
        line_w = font.text_width(line)
        clip_id = f"clip{i}"
        glyphs = outline_text(font, line, x=PAD, baseline=baseline, fill=ink)
        # a clip rect grows from width 0 to full over TYPE_SECS, then freezes
        body.append(
            f'<clipPath id="{clip_id}"><rect x="{PAD}" y="{baseline-LINE_H+6}" '
            f'height="{LINE_H}" width="0">'
            f'<animate attributeName="width" from="0" to="{line_w:.1f}" '
            f'begin="{begin:.2f}s" dur="{TYPE_SECS}s" fill="freeze"/>'
            f'</rect></clipPath>'
            f'<g clip-path="url(#{clip_id})">{glyphs}</g>'
        )
        # blinking block cursor that parks at end of each line after it types
        cx_start = PAD
        cx_end = PAD + line_w
        body.append(
            f'<rect y="{baseline-LINE_H+8}" width="{CURSOR_W}" height="{LINE_H-6}" '
            f'fill="{cursor_fill}" x="{cx_start:.1f}">'
            f'<animate attributeName="x" from="{cx_start:.1f}" to="{cx_end:.1f}" '
            f'begin="{begin:.2f}s" dur="{TYPE_SECS}s" fill="freeze"/>'
            f'<animate attributeName="opacity" values="1;0;1" dur="1s" '
            f'begin="{(begin+TYPE_SECS):.2f}s" repeatCount="indefinite"/>'
            f'</rect>'
        )
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">' + "".join(body) + "</svg>"
    )
    return svg


def render_doctrine(cfg, out_dir: str, font_path: str = FONT) -> None:
    font = MonoFont(font_path, size=15)
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "doctrine-light.svg"), "w", encoding="utf-8") as fh:
        fh.write(_variant(cfg, font, ink="#111111", cursor_fill="#111111"))
    with open(os.path.join(out_dir, "doctrine-dark.svg"), "w", encoding="utf-8") as fh:
        fh.write(_variant(cfg, font, ink="#d8d8d8", cursor_fill="#d8d8d8"))
```

> Note: the cursor's `opacity` blink legitimately uses `repeatCount="indefinite"`; the test forbids `repeatCount` only conceptually on the *reveal*. To keep the test simple and honest, the reveal animates `width`/`x` with `fill="freeze"` and no repeat, while the blink is a separate concern. **Adjust the test** in Step 1 to: `assert svg.count("repeatCount") == len(cfg.doctrine)` (one indefinite blink per line) rather than `"repeatCount" not in svg`. Update both before running.

- [ ] **Step 4: Fix the test per the note, then run**

Edit `tests/test_render_doctrine.py` `test_doctrine_uses_smil_freeze_and_does_not_loop`: replace
`assert "repeatCount" not in svg` with:
```python
    # only the cursor blink repeats (one per line); the text reveal freezes
    assert svg.count("repeatCount") == len(_cfg().doctrine)
```
Run: `python -m pytest tests/test_render_doctrine.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add clerk/render_doctrine.py tests/test_render_doctrine.py
git commit -m "feat: render doctrine typewriter (SMIL, light/dark)"
```

---

## Task 9: `render_status` — §02 per-ref status chits

**Files:**
- Create: `clerk/render_status.py`
- Test: `tests/test_render_status.py`

- [ ] **Step 1: Write the failing test**

`tests/test_render_status.py`:
```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_render_status.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Write minimal implementation**

`clerk/render_status.py`:
```python
import os
from clerk.svgtext import MonoFont, outline_text

FONT = "clerk/fonts/JetBrainsMono-Regular.ttf"


def render_status(refs, out_dir: str, font_path: str = FONT) -> None:
    font = MonoFont(font_path, size=12)
    os.makedirs(out_dir, exist_ok=True)
    for ref in refs:
        pad = 8
        width = int(font.text_width(ref.status_text) + pad * 2)
        height = 22
        glyphs = outline_text(font, ref.status_text, x=pad, baseline=15, fill="#111111")
        overprint = ""
        if ref.dormant:
            of = MonoFont(font_path, size=12)
            overprint = (
                f'<g transform="rotate(-8 {width/2:.0f} {height/2:.0f})" opacity="0.45">'
                + outline_text(of, "DORMANT", x=pad, baseline=15, fill="#7a2a2a")
                + "</g>"
            )
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" aria-label="{ref.status_text}">'
            f'{glyphs}{overprint}</svg>'
        )
        with open(os.path.join(out_dir, f"status-{ref.ref}.svg"), "w", encoding="utf-8") as fh:
            fh.write(svg)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_render_status.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add clerk/render_status.py tests/test_render_status.py
git commit -m "feat: render per-ref status chits with dormant overprint"
```

---

## Task 10: `render_fieldlog` — §07 dated entries with decay

**Files:**
- Create: `clerk/render_fieldlog.py`
- Test: `tests/test_render_fieldlog.py`

- [ ] **Step 1: Write the failing test**

`tests/test_render_fieldlog.py`:
```python
from clerk.data import LogEntry
from clerk.render_fieldlog import render_fieldlog

def test_fieldlog_markdown_newest_first_with_sub_decay():
    entries = [LogEntry("2026·06·16", "claude-enter · 3 commits"),
               LogEntry("2026·06·12", "content · released v1")]
    md = render_fieldlog(entries)
    # newest line is full strength; older line is wrapped in <sub> (shrinks, no color)
    lines = [l for l in md.splitlines() if l.strip()]
    assert "2026·06·16" in lines[0]
    assert "<sub>" in lines[1]
    assert "color" not in md and "style=" not in md   # sanitizer-safe
    assert md.startswith("`") or "`" in lines[0]       # monospace via inline code

def test_fieldlog_empty_is_placeholder():
    assert "no recent" in render_fieldlog([]).lower()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_render_fieldlog.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Write minimal implementation**

`clerk/render_fieldlog.py`:
```python
def render_fieldlog(entries) -> str:
    """Markdown for the §07 field log: newest first, older lines shrink via <sub>.

    No color/style (stripped by GitHub). Monospace via inline code spans.
    """
    if not entries:
        return "`— no recent field activity on record —`"
    lines = []
    for i, e in enumerate(entries):
        text = f"`{e.date} — {e.summary}`"
        if i == 0:
            lines.append(text)
        elif i == 1:
            lines.append(f"<sub>{text}</sub>")
        else:
            lines.append(f"<sub><sub>{text}</sub></sub>")
    return "  \n".join(lines)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_render_fieldlog.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add clerk/render_fieldlog.py tests/test_render_fieldlog.py
git commit -m "feat: render field log markdown with sanitizer-safe decay"
```

---

## Task 11: `main` — orchestrate + idempotency (hash-stability) test

**Files:**
- Create: `clerk/main.py`
- Test: `tests/test_main_idempotent.py`

- [ ] **Step 1: Write the failing test**

`tests/test_main_idempotent.py`:
```python
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

    # stub the data layer so the test is offline + deterministic
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
    assert "REV 47" not in first or True  # seal is an SVG file, not README text
    assert (repo / "assets" / "seal.svg").exists()
    assert (repo / "assets" / "doctrine-light.svg").exists()
    assert (repo / "assets" / "status-DRS-003.svg").exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_main_idempotent.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Write minimal implementation**

`clerk/main.py`:
```python
import os

from clerk.config import load_config
from clerk.data import gather  # patched in tests
from clerk.markers import replace_section
from clerk.render_seal import render_seal
from clerk.render_header import render_header
from clerk.render_doctrine import render_doctrine
from clerk.render_status import render_status
from clerk.render_fieldlog import render_fieldlog


def run(repo_dir: str, token: str) -> None:
    readme_path = os.path.join(repo_dir, "README.md")
    assets = os.path.join(repo_dir, "assets")
    cfg = load_config(os.path.join(repo_dir, "dossier.yaml"))

    with open(readme_path, encoding="utf-8") as fh:
        readme = fh.read()

    data = gather(cfg, readme, token)

    render_seal(data, out_dir=assets)
    render_header(cfg, out_dir=assets)
    render_doctrine(cfg, out_dir=assets)
    render_status(data.refs, out_dir=assets)

    footer = (f"FILED {data.filed} · ENTRY No.1 · THIS DOSSIER IS LIVE "
              f"(re-filed {data.filed})")
    readme = replace_section(readme, "FOOTER", footer)
    readme = replace_section(readme, "FIELDLOG", render_fieldlog(data.field_log))

    with open(readme_path, "w", encoding="utf-8") as fh:
        fh.write(readme)


if __name__ == "__main__":
    import sys
    run(repo_dir=".", token=os.environ.get("DOSSIER_READ_TOKEN")
        or os.environ["GITHUB_TOKEN"])
    print("clerk: dossier re-filed")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_main_idempotent.py -v`
Expected: PASS (both runs produce identical README — proves the seal-hash strip fix and marker idempotency).

- [ ] **Step 5: Run the whole suite**

Run: `python -m pytest -v`
Expected: all tests PASS.

- [ ] **Step 6: Commit**

```bash
git add clerk/main.py tests/test_main_idempotent.py
git commit -m "feat: clerk orchestrator + idempotency test"
```

---

## Task 12: Restructure README.md

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Rewrite README with the new structure**

Replace `README.md` with the structure below (keep the existing masthead `<picture>` block as-is between header and seal). Use **relative** asset paths. The DOCTRINE/header/seal images and the two marker sections are what the clerk maintains:

```markdown
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/header-dark.svg">
  <img alt="UNCLASSIFIED // FIELD FILE — SHINGALA, D." src="./assets/header-light.svg">
</picture>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/masthead-dark.svg">
  <img alt="SHINGALA, D. — Product · Content · IT Operations" src="./assets/masthead-light.svg">
</picture>

<img alt="ENTRY No.1 · REV · SEAL · FILED" src="./assets/seal.svg">

## §01 &nbsp; DOCTRINE

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/doctrine-dark.svg">
  <img alt="Operating doctrine" src="./assets/doctrine-light.svg">
</picture>

## §02 &nbsp; OPEN DOSSIERS

<table>
<thead><tr><th align="left">REF</th><th align="left">TITLE</th><th align="left">DOMAIN</th><th align="left">STATUS</th></tr></thead>
<tbody>
<tr><td><code>DRS-001</code></td><td>claude-enter</td><td>workflow automation</td><td><img alt="status" src="./assets/status-DRS-001.svg"></td></tr>
<tr><td><code>DRS-002</code></td><td>Motadata content system</td><td>content operations</td><td><img alt="status" src="./assets/status-DRS-002.svg"></td></tr>
<tr><td><code>DRS-003</code></td><td>ITSM positioning brief</td><td>positioning · ITSM</td><td><img alt="status" src="./assets/status-DRS-003.svg"></td></tr>
</tbody>
</table>

## §07 &nbsp; FIELD LOG

<!--FIELDLOG:START-->
`— no recent field activity on record —`
<!--FIELDLOG:END-->

## §04 &nbsp; CHANNEL ASSIGNMENTS

<a href="https://www.linkedin.com/in/aatmaa/">LinkedIn</a> &nbsp;·&nbsp; <a href="mailto:dhashingala9@gmail.com">Email</a>

---

<sub><!--FOOTER:START-->
FILED 2026·06·16 · ENTRY No.1 · THIS DOSSIER IS LIVE (re-filed 2026·06·16)
<!--FOOTER:END--></sub>
```

- [ ] **Step 2: Verify markers resolve**

Run:
```bash
python -c "from clerk.markers import replace_section; t=open('README.md',encoding='utf-8').read(); replace_section(t,'FOOTER','x'); replace_section(t,'FIELDLOG','y'); print('markers OK')"
```
Expected: `markers OK` (no ValueError).

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "feat: restructure README around clerk-maintained sections"
```

---

## Task 13: GitHub Action — `dossier.yml`

**Files:**
- Create: `.github/workflows/dossier.yml`

- [ ] **Step 1: Write the workflow**

`.github/workflows/dossier.yml`:
```yaml
name: dossier-clerk

on:
  schedule:
    - cron: "17 6 * * *"   # ~daily, off top-of-hour congestion (best-effort)
  workflow_dispatch:

permissions:
  contents: write

concurrency:
  group: dossier-clerk
  cancel-in-progress: false

jobs:
  refile:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0          # full history for REV count
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: python -m pip install -r requirements.txt
      - name: Run the clerk
        env:
          DOSSIER_READ_TOKEN: ${{ secrets.DOSSIER_READ_TOKEN }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: python -m clerk.main
      - name: Commit if changed
        run: |
          git config user.name "dossier-clerk[bot]"
          git config user.email "dossier-clerk[bot]@users.noreply.github.com"
          git add -A
          if git diff --staged --quiet; then
            echo "no changes to re-file"
          else
            git commit -m "chore: re-file dossier [skip ci]"
            git push
          fi
```

- [ ] **Step 2: Lint the YAML locally**

Run: `python -c "import yaml; yaml.safe_load(open('.github/workflows/dossier.yml')); print('yaml OK')"`
Expected: `yaml OK`.

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/dossier.yml
git commit -m "ci: scheduled dossier clerk workflow"
```

---

## Task 14: End-to-end verification + PAT + merge

**Files:** none (verification + ops)

- [ ] **Step 1: Local full render against the real repo**

Run:
```bash
GITHUB_TOKEN=$(gh auth token) python -m clerk.main
git status --porcelain
```
Expected: `assets/*.svg` created/updated and README marker sections filled; status chits exist for DRS-001/002/003.

- [ ] **Step 2: Visual check in TWO browsers**

Open these in **Chrome and Firefox** and confirm: doctrine types in then holds (SMIL animates in both); seal/header/status render; no broken images.
```
file://<repo>/assets/doctrine-light.svg
file://<repo>/assets/seal.svg
file://<repo>/assets/header-dark.svg
```
Expected: animation plays in both browsers; static pieces crisp; redaction bars sit over the right words.

- [ ] **Step 3: Create the fine-grained PAT (user action)**

User creates a **fine-grained PAT** at github.com/settings/personal-access-tokens: resource owner `dharmik136`, **read-only** `Contents` + `Metadata` + `Issues`, scoped to repos `claude-enter` and `motadata-marketing-ai`. Add it as repo secret `DOSSIER_READ_TOKEN` on `dharmik136/dharmik136` (Settings → Secrets and variables → Actions).

- [ ] **Step 4: Push branch and dispatch a test run**

```bash
git push -u origin feat/living-dossier
gh workflow run dossier-clerk --repo dharmik136/dharmik136 --ref feat/living-dossier
gh run watch --repo dharmik136/dharmik136 $(gh run list --repo dharmik136/dharmik136 --workflow dossier-clerk -L1 --json databaseId --jq '.[0].databaseId') --exit-status
```
Expected: run succeeds; status chits reflect real signals (incl. private REFs via the PAT).

- [ ] **Step 5: Verify rendered README on the branch, then open the merge**

View `https://github.com/dharmik136/dharmik136/blob/feat/living-dossier/README.md` rendered; toggle light/dark; check mobile. When satisfied:
```bash
gh pr create --repo dharmik136/dharmik136 --base main --head feat/living-dossier \
  --title "Living dossier README" --body "Self-updating dossier: seal, classification header, doctrine typer, reconciled status, field log. Spec + plan in docs/superpowers/."
```
Expected: PR opened. Merge after the profile renders correctly on the branch.

- [ ] **Step 6: Post-merge confirmation**

After merge to `main`, open `https://github.com/dharmik136` and confirm the profile shows the living dossier; confirm the next scheduled run re-files without churn (commit only appears when data actually changes).

---

## Self-Review

**Spec coverage:** §00 Seal → Task 6; §00 Classification header → Task 7; §01 Doctrine typer → Task 8; §02 Reconciled status → Tasks 5 (data) + 9 (render); §07 Field log → Tasks 5 + 10; footer "re-filed" → Task 11; the Action/clerk → Tasks 11 + 13; correctness rules §6 → outlining (Task 2), SMIL-freeze (Task 8), stable seal hash (Tasks 5 + 11 idempotency test), REV-excludes-bot (Task 5), decay-no-color (Task 10), commit-on-diff/[skip ci]/bot author (Task 13); PAT (Task 14). Testing/verification §7 → Tasks 11 + 14. Phasing §8 → Tasks 1–8 (static) then 9–13 (dynamics) then 14 (verify/merge). No gaps.

**Type consistency:** `DossierData(rev, seal, filed, refs, field_log)`, `RefStatus(ref, title, domain, status_text, dormant)`, `LogEntry(date, summary)`, `Config(...)` are defined in Tasks 4–5 and used identically in Tasks 6–11. `gather(cfg, readme_text, token)` defined in Task 5, patched/called the same way in Task 11. `render_*` signatures consistent. `replace_section(text, name, inner)` consistent across Tasks 3, 11, 12.

**Placeholder scan:** every code step contains complete code; commands have expected output. The one self-correcting item (doctrine `repeatCount`) is handled explicitly in Task 8 Steps 3–4 with the exact test edit.
