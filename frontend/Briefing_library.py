"""Streamlit front end for the briefing library.

Run the API first (uvicorn app.main:app), then:
    streamlit run frontend/Briefing_library.py

If RISK_INTEL_API is not reachable, the app reads the SQLite database
directly, so a single Streamlit deployment also works for a portfolio demo.
On startup the database is built from the seed JSON files if it is missing
or empty, so the .db file never needs to be committed.

Drafts are hidden unless SHOW_DRAFTS=1 is set (do this locally, never on
the public deployment).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import httpx
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app import db  # noqa: E402
from frontend.settings import escape_markdown_dollars as esc, show_drafts  # noqa: E402
from scripts.seed import ensure_seeded  # noqa: E402

API_URL = os.environ.get("RISK_INTEL_API", "http://127.0.0.1:8000")
DISCLAIMER = (
    "Informational and educational only. Not regulatory, legal or financial advice, "
    "and not a substitute for reading the source documents or an APRA-aligned review."
)

st.set_page_config(page_title="Model & Market Risk Intelligence", page_icon="📚", layout="wide")
SHOW_DRAFTS = show_drafts()


@st.cache_resource
def prepare_database() -> bool:
    return ensure_seeded()


prepare_database()


@st.cache_data(ttl=60)
def api_available() -> bool:
    try:
        return httpx.get(f"{API_URL}/health", timeout=2).status_code == 200
    except httpx.HTTPError:
        return False


@st.cache_data(ttl=60)
def load_facets(status: str | None) -> dict:
    if api_available():
        params = {"status": status} if status else {}
        return httpx.get(f"{API_URL}/facets", params=params, timeout=10).json()
    db.init_db()
    with db.connect() as conn:
        return db.facet_values(conn, status=status)


@st.cache_data(ttl=60)
def load_briefings(topics: tuple[str, ...], jurisdiction: str | None, doc_type: str | None,
                   status: str | None, q: str | None) -> list[dict]:
    if api_available():
        params: list[tuple[str, str]] = [("topic", t) for t in topics]
        for key, value in (("jurisdiction", jurisdiction), ("document_type", doc_type),
                           ("status", status), ("q", q)):
            if value:
                params.append((key, value))
        resp = httpx.get(f"{API_URL}/briefings", params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    with db.connect() as conn:
        return db.list_briefings(conn, topics=list(topics), jurisdiction=jurisdiction,
                                 document_type=doc_type, status=status, q=q)


def fmt_date(value: str | None) -> str:
    return value if value else "Not stated"


# ---------------------------------------------------------------- sidebar
facets = load_facets(None if SHOW_DRAFTS else "published")
with st.sidebar:
    st.header("Filter")
    q = st.text_input("Search", placeholder="e.g. validation, FRTB, inventory").strip() or None
    topics = st.multiselect("Topics (all must match)", facets["topics"])
    jurisdiction = st.selectbox("Jurisdiction", ["All"] + facets["jurisdictions"])
    doc_type = st.selectbox("Document type", ["All"] + facets["document_types"])
    if SHOW_DRAFTS:
        status_choice = st.radio("Status", ["All", "published", "draft"], horizontal=True)
        st.caption("Drafts visible (SHOW_DRAFTS=1)")
    else:
        status_choice = "published"
    st.divider()
    st.caption(f"Data source: {'API at ' + API_URL if api_available() else 'local SQLite (API offline)'}")

rows = load_briefings(
    tuple(topics),
    None if jurisdiction == "All" else jurisdiction,
    None if doc_type == "All" else doc_type,
    None if status_choice == "All" else status_choice,
    q if q and len(q) >= 2 else None,
)

# ------------------------------------------------------------------- main
st.title("Model & Market Risk Intelligence")
st.write(
    "Plain-language briefings on Australian and global model-risk and market-risk guidance, "
    "written for risk graduates and small risk teams."
)
st.info(DISCLAIMER)

if not rows:
    if not SHOW_DRAFTS and not any((q, topics, jurisdiction != "All", doc_type != "All")):
        st.warning("No briefings are published yet. Check back soon.")
    else:
        st.warning("No briefings match these filters.")
    st.stop()

st.caption(f"{len(rows)} briefing(s)")

for b in rows:
    badge = "🟢 Published" if b["status"] == "published" else "🟡 Draft, not yet reviewed"
    with st.expander(f"**{b['title']}**  ·  {b['source_name']}  ·  {b['jurisdiction']}"):
        st.caption(f"{badge}  |  {b['document_type'].title()}  |  Tags: {', '.join(b['topic_tags'])}")
        if b.get("supersedes"):
            st.caption(f"Supersedes: {b['supersedes']}")
        if b.get("applicability_note"):
            st.caption(f"Applicability: {esc(b['applicability_note'])}")
        c1, c2, c3 = st.columns(3)
        c1.metric("Published", fmt_date(b.get("publish_date")))
        c2.metric("Effective", fmt_date(b.get("effective_date")))
        c3.metric("Last reviewed", fmt_date(b.get("last_reviewed_by_you")))
        st.subheader("Summary")
        st.markdown(esc(b["plain_language_summary"]))
        st.subheader("Why it matters")
        st.markdown(esc(b["why_it_matters"]))
        st.subheader("Who it applies to")
        st.markdown(esc(b["who_it_applies_to"]))
        st.link_button("Read the source document", b["source_url"])
