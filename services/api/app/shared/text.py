"""Small text helpers used when normalising jobs. Pure functions: easy to test."""

import html
import re

_LIST_ITEM = re.compile(r"<\s*li[^>]*>", re.IGNORECASE)
_BLOCK_END = re.compile(r"<\s*(br|/p|/li|/div|/h[1-6]|/ul|/ol)\s*/?\s*>", re.IGNORECASE)
_ANY_TAG = re.compile(r"<[^>]+>")


def html_to_text(raw: str) -> str:
    """Turn an HTML job description into readable plain text.

    "<p>Hello</p><ul><li>Python</li></ul>"  ->  "Hello\n- Python"
    """
    text = _LIST_ITEM.sub("\n- ", raw)  # <li> becomes a bullet
    text = _BLOCK_END.sub("\n", text)  # end of a paragraph/line becomes a newline
    text = _ANY_TAG.sub("", text)  # remove every other tag
    text = html.unescape(text)  # "&amp;" -> "&", "&nbsp;" -> non-breaking space

    # Clean each line, then drop repeated empty lines
    lines = [" ".join(line.split()) for line in text.splitlines()]
    cleaned: list[str] = []
    for line in lines:
        if line or (cleaned and cleaned[-1]):
            cleaned.append(line)
    return "\n".join(cleaned).strip()


def fix_mojibake(text: str) -> str:
    """Repair text that was UTF-8 but got decoded as Latin-1 ("â€”" instead of "—").

    RemoteOK sends text like this. If the repair fails, the text was fine: keep it.
    """
    try:
        return text.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text


def normalise_for_hash(text: str) -> str:
    """Lowercase and collapse whitespace, so "  Senior  Dev " == "senior dev"."""
    return " ".join(text.lower().split())
