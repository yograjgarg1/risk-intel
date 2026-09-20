"""Pure helpers for the comparison page (kept separate so they can be unit tested)."""
from __future__ import annotations

import pandas as pd

from app.models import DIMENSIONS, FRAMEWORKS
from frontend.settings import escape_markdown_dollars

FRAMEWORK_LABELS = {
    "SR 26-2": "US: SR 26-2",
    "SS1/23": "UK: PRA SS1/23",
    "E-23": "Canada: OSFI E-23",
    "APRA": "Australia: APRA (distributed)",
}
PLACEHOLDER = "Under review"


def build_table(cells: list[dict], show_unreviewed: bool) -> pd.DataFrame:
    """Frameworks as columns, dimensions as rows."""
    table = {FRAMEWORK_LABELS[f]: {d: "" for d in DIMENSIONS} for f in FRAMEWORKS}
    for c in cells:
        if c["framework"] not in FRAMEWORK_LABELS or c["dimension"] not in DIMENSIONS:
            continue
        reviewed = c.get("last_reviewed_by_you") is not None
        text = c["position"] if (reviewed or show_unreviewed) else PLACEHOLDER
        if show_unreviewed and not reviewed:
            text = f"[draft] {text}"
        table[FRAMEWORK_LABELS[c["framework"]]][c["dimension"]] = escape_markdown_dollars(text)
    return pd.DataFrame(table).reindex(list(DIMENSIONS))
