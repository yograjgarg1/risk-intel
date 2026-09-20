"""Model risk framework comparison: SR 26-2 vs SS1/23 vs E-23 vs APRA."""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app import db  # noqa: E402
from app.models import FRAMEWORKS  # noqa: E402
from frontend.comparison_table import FRAMEWORK_LABELS, build_table  # noqa: E402
from frontend.settings import show_drafts  # noqa: E402
from scripts.seed import ensure_seeded  # noqa: E402

st.set_page_config(page_title="Model risk comparison", page_icon="📚", layout="wide")
SHOW_DRAFTS = show_drafts()
ensure_seeded()

with db.connect() as conn:
    cells = db.list_comparison(conn)

st.title("How four regulators approach model risk")
st.write(
    "The US, UK and Canada each have a dedicated model risk framework. Australia does not: "
    "APRA's expectations are spread across several standards and supervisory letters."
)
st.info(
    "Informational and educational only. Not regulatory, legal or financial advice. "
    "Read the source documents before relying on any cell."
)
if SHOW_DRAFTS:
    st.caption("Showing unreviewed cells, marked [draft] (SHOW_DRAFTS=1).")

st.table(build_table(cells, SHOW_DRAFTS))

st.subheader("Sources and review dates")
visible = [c for c in cells if SHOW_DRAFTS or c.get("last_reviewed_by_you")]
if not visible:
    st.write("Cells appear here once they have been checked against the source.")
for fw in FRAMEWORKS:
    rows = [c for c in visible if c["framework"] == fw]
    if not rows:
        continue
    with st.expander(FRAMEWORK_LABELS[fw]):
        for c in rows:
            reviewed = c.get("last_reviewed_by_you") or "not yet reviewed"
            st.markdown(
                f"**{c['dimension']}**: [source]({c['source_url']}) · "
                f"as of {c.get('as_of') or 'not stated'} · reviewed {reviewed}"
            )
