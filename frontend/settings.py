"""Runtime settings shared by the Streamlit pages."""
from __future__ import annotations

import os


def show_drafts() -> bool:
    """Drafts and unreviewed comparison cells show only when SHOW_DRAFTS=1.

    Leave it unset on the public deployment.
    """
    return os.environ.get("SHOW_DRAFTS", "").strip().lower() in {"1", "true", "yes"}


def escape_markdown_dollars(text: str | None) -> str:
    """Streamlit renders $...$ as LaTeX, which mangles amounts like $30b and $300b."""
    return (text or "").replace("\\$", "$").replace("$", "\\$")
