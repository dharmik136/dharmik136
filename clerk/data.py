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
    """Content commits = commits whose author is not the clerk bot."""
    authors = _git(["log", "--format=%an"]).splitlines()
    return sum(1 for a in authors if a != CLERK_BOT)


def last_content_commit_date() -> str:
    """Date (YYYY·MM·DD) of the most recent non-bot commit."""
    log = _git(["log", "--format=%an%x09%cs"])
    for line in log.splitlines():
        author, date = line.split("\t", 1)
        if author != CLERK_BOT:
            return date.replace("-", "·")
    return datetime.now(timezone.utc).strftime("%Y·%m·%d")


def ref_status_from_signals(ref: dict, signals, dormant_days: int) -> RefStatus:
    if ref.get("manual_status"):
        return RefStatus(ref["ref"], ref["title"], ref["domain"],
                         ref["manual_status"], False)
    if signals is None:
        return RefStatus(ref["ref"], ref["title"], ref["domain"], "UNKNOWN", False)
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
            continue
        try:
            sig = fetch_repo_signals(ref["repo"], token)
            refs.append(ref_status_from_signals(ref, sig, cfg.dormant_days))
        except Exception:
            refs.append(ref_status_from_signals(ref, None, cfg.dormant_days))
    try:
        events = fetch_public_events(cfg.user, token)
    except Exception:
        events = []
    return DossierData(
        rev=rev_count(),
        seal=seal_hash(readme_text),
        filed=last_content_commit_date(),
        refs=refs,
        field_log=log_entries_from_events(events, cfg.field_log_len),
    )
