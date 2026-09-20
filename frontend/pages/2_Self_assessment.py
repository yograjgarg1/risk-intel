"""Phase 3: model risk governance maturity self-assessment (stateless)."""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.assessment import MAX_ANSWER, load_questionnaire, score  # noqa: E402
from frontend.settings import escape_markdown_dollars as esc  # noqa: E402

st.set_page_config(page_title="Model risk self-assessment", page_icon="📚", layout="wide")

DISCLAIMER = (
    "Informational and educational only. Not regulatory, legal or financial advice, "
    "and not a substitute for an APRA-aligned review. Nothing you enter is stored."
)
BAND_ICONS = {
    "Foundational": "🔴", "Developing": "🟠", "Established": "🟡", "Advanced": "🟢",
}

q = load_questionnaire()
scale = dict(q.answer_scale)

st.title("How mature is your model risk governance?")
st.info(DISCLAIMER)
st.write(
    f"{len(q.questions)} questions across {len(q.categories)} areas. Each answer maps to the "
    "frameworks that expect it, so the result doubles as a cross-reference to SR 26-2, "
    "SS1/23, E-23 and APRA's expectations."
)

answers: dict[str, int] = {}
with st.form("self_assessment"):
    for key, label in q.categories.items():
        items = [item for item in q.questions if item.category == key]
        if not items:
            continue
        st.subheader(label)
        for item in items:
            answers[item.id] = st.select_slider(
                esc(item.question_text),
                options=list(range(MAX_ANSWER + 1)),
                value=0,
                format_func=lambda v: f"{v} · {scale[v]}",
                key=f"q_{item.id}",
                help=f"Expected by: {', '.join(item.framework_refs)}",
            )
    submitted = st.form_submit_button("Score my answers", type="primary")

if not submitted:
    st.caption("Answer every question, then score. Weightings favour inventory and validation.")
    st.stop()

result = score(answers, q)
icon = BAND_ICONS.get(result.band, "")

left, right = st.columns([1, 2])
left.metric("Weighted score", f"{result.percent}%", help=f"{result.weighted_score} of {result.max_weighted_score}")
right.subheader(f"{icon} {result.band}")
right.write(result.band_note)
st.progress(min(result.percent / 100, 1.0))

if result.has_critical_gap:
    gaps = ", ".join(c.label.lower() for c in result.critical_gaps)
    st.error(
        f"Critical gap flagged in {gaps}. A weak answer here matters more than the total: "
        "every framework in the comparison expects an inventory and independent validation."
    )

st.subheader("By area")
for c in sorted(result.categories, key=lambda c: c.percent):
    flag = " · critical gap" if (c.is_critical and c.weak_question_ids) else ""
    with st.expander(f"{c.label} — {c.percent}%{flag}", expanded=bool(flag)):
        if not c.weak_question_ids:
            st.write("No weak answers in this area.")
            continue
        st.write("Weak answers (0 or 1):")
        for qid in c.weak_question_ids:
            item = q.by_id(qid)
            st.markdown(f"- {esc(item.question_text)}  \n  Expected by: {', '.join(item.framework_refs)}")
        if c.frameworks:
            st.caption(f"Frameworks touching these gaps: {', '.join(c.frameworks)}")

st.caption(
    "Bands: Foundational under 40%, Developing 40% to under 65%, "
    "Established 65% to under 85%, Advanced 85% and above."
)
