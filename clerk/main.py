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
