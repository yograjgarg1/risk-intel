"""Prompt 2b: auto-seed on a fresh deployment and draft gating."""
import pytest


@pytest.fixture()
def db_path(tmp_path, monkeypatch):
    path = tmp_path / "fresh" / "deploy.db"
    monkeypatch.setenv("RISK_INTEL_DB", str(path))
    return path


def test_ensure_seeded_builds_missing_database(db_path):
    from app import db
    from scripts.seed import ensure_seeded

    assert not db_path.exists()
    assert ensure_seeded() is True
    assert ensure_seeded() is False  # second start does nothing
    with db.connect() as conn:
        assert db.count_rows(conn, "briefings") == 8
        assert db.count_rows(conn, "framework_comparison") == 28


@pytest.mark.parametrize("value, expected", [
    (None, False), ("", False), ("0", False), ("1", True), ("true", True), ("YES", True),
])
def test_show_drafts_flag(monkeypatch, value, expected):
    from frontend.settings import show_drafts

    if value is None:
        monkeypatch.delenv("SHOW_DRAFTS", raising=False)
    else:
        monkeypatch.setenv("SHOW_DRAFTS", value)
    assert show_drafts() is expected


def _cells():
    return [
        {"framework": "APRA", "dimension": "AI treatment", "position": "Reviewed text",
         "last_reviewed_by_you": "2026-09-15"},
        {"framework": "E-23", "dimension": "AI treatment", "position": "Unreviewed text",
         "last_reviewed_by_you": None},
    ]


def test_comparison_table_hides_unreviewed_publicly():
    from frontend.comparison_table import PLACEHOLDER, build_table

    t = build_table(_cells(), show_unreviewed=False)
    assert list(t.columns)[0].startswith("US")
    assert t.loc["AI treatment", "Australia: APRA (distributed)"] == "Reviewed text"
    assert t.loc["AI treatment", "Canada: OSFI E-23"] == PLACEHOLDER
    assert "Unreviewed" not in t.to_string()


def test_comparison_table_marks_drafts_locally():
    from frontend.comparison_table import build_table

    t = build_table(_cells(), show_unreviewed=True)
    assert t.loc["AI treatment", "Canada: OSFI E-23"] == "[draft] Unreviewed text"
    assert t.shape == (7, 4)


def test_live_fetch_requires_contact(monkeypatch):
    from ingestion import check_sources

    monkeypatch.delenv("RISK_INTEL_CONTACT", raising=False)
    with pytest.raises(RuntimeError, match="RISK_INTEL_CONTACT"):
        check_sources.user_agent()
    monkeypatch.setenv("RISK_INTEL_CONTACT", "set-your-email@example.com")
    with pytest.raises(RuntimeError):
        check_sources.user_agent()
    monkeypatch.setenv("RISK_INTEL_CONTACT", "someone@uq.net.au")
    assert "someone@uq.net.au" in check_sources.user_agent()


def test_dollar_amounts_are_escaped():
    from frontend.comparison_table import build_table
    from frontend.settings import escape_markdown_dollars

    assert escape_markdown_dollars("SFI at $30b+ and MSFI at $300b+") == r"SFI at \$30b+ and MSFI at \$300b+"
    assert escape_markdown_dollars(r"already \$5") == r"already \$5"
    cell = [{"framework": "APRA", "dimension": "Scope and threshold",
             "position": "SFI at $30b+", "last_reviewed_by_you": "2026-09-15"}]
    assert build_table(cell, False).loc["Scope and threshold", "Australia: APRA (distributed)"] == r"SFI at \$30b+"
