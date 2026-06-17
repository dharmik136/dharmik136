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
