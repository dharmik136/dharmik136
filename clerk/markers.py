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
