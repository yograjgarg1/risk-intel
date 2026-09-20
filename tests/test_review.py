"""The review/publish helper: JSON stays the source of truth."""
import json
from datetime import date

import pytest

from scripts import review


@pytest.fixture()
def files(tmp_path, monkeypatch):
    briefings = [
        {"title": "APS 116 Capital Adequacy: Market Risk", "status": "draft", "last_reviewed_by_you": None},
        {"title": "CPS 230 Operational Risk Management", "status": "draft", "last_reviewed_by_you": None},
    ]
    cells = [
        {"framework": "SR 26-2", "dimension": "Validation", "last_reviewed_by_you": None},
        {"framework": "APRA", "dimension": "Validation", "last_reviewed_by_you": None},
    ]
    b_path, c_path = tmp_path / "b.json", tmp_path / "c.json"
    b_path.write_text(json.dumps(briefings), encoding="utf-8")
    c_path.write_text(json.dumps(cells), encoding="utf-8")
    monkeypatch.setattr(review, "SEED_FILE", b_path)
    monkeypatch.setattr(review, "COMPARISON_FILE", c_path)
    monkeypatch.setattr(review, "reset_and_seed", lambda *a, **k: (0, 0))
    monkeypatch.setenv("RISK_INTEL_DB", str(tmp_path / "r.db"))
    return b_path, c_path


def test_publish_one_briefing_by_substring(files, capsys):
    b_path, _ = files
    assert review.main(["publish", "--briefing", "aps 116", "--date", "2026-09-20"]) == 0
    rows = json.loads(b_path.read_text())
    published = [r for r in rows if r["status"] == "published"]
    assert [r["title"] for r in published] == ["APS 116 Capital Adequacy: Market Risk"]
    assert published[0]["last_reviewed_by_you"] == "2026-09-20"
    assert "Published 1 item" in capsys.readouterr().out


def test_publish_all_and_unpublish_round_trip(files):
    b_path, c_path = files
    review.main(["publish", "--briefing", "all", "--comparison", "all", "--date", "2026-09-20"])
    assert all(r["status"] == "published" for r in json.loads(b_path.read_text()))
    assert all(c["last_reviewed_by_you"] == "2026-09-20" for c in json.loads(c_path.read_text()))

    review.main(["unpublish", "--briefing", "all", "--comparison", "all"])
    rows = json.loads(b_path.read_text())
    assert all(r["status"] == "draft" and r["last_reviewed_by_you"] is None for r in rows)
    assert all(c["last_reviewed_by_you"] is None for c in json.loads(c_path.read_text()))


def test_publish_comparison_by_framework(files):
    _, c_path = files
    review.main(["publish", "--comparison", "SR 26-2", "--date", "2026-09-20"])
    cells = json.loads(c_path.read_text())
    assert [c["framework"] for c in cells if c["last_reviewed_by_you"]] == ["SR 26-2"]


def test_no_match_returns_nonzero_and_changes_nothing(files, capsys):
    b_path, _ = files
    before = b_path.read_text()
    assert review.main(["publish", "--briefing", "nothing like this"]) == 1
    assert b_path.read_text() == before
    assert "Nothing matched" in capsys.readouterr().out


def test_requires_a_target(files):
    with pytest.raises(SystemExit):
        review.main(["publish", "--date", "2026-09-20"])


def test_defaults_to_today(files):
    b_path, _ = files
    review.main(["publish", "--briefing", "CPS 230"])
    rows = json.loads(b_path.read_text())
    cps = next(r for r in rows if r["title"].startswith("CPS 230"))
    assert cps["last_reviewed_by_you"] == date.today().isoformat()


def test_list_reports_progress(files, capsys):
    review.main(["publish", "--comparison", "APRA", "--date", "2026-09-20"])
    capsys.readouterr()
    assert review.main(["list"]) == 0
    out = capsys.readouterr().out
    assert "Comparison cells: 1 of 2 reviewed" in out
    assert "APRA: 1 of 1" in out
    assert "not reviewed" in out  # the briefings are still drafts


def test_published_content_carries_a_review_date():
    """Guard: `published` and a review date travel together, and no cell is left TO CONFIRM.

    Content is only ever published by a human running scripts.review, so a
    published briefing without a date (or a dated draft) means something was
    hand-edited.
    """
    from scripts.seed import COMPARISON_FILE, SEED_FILE

    briefings = json.loads(SEED_FILE.read_text(encoding="utf-8"))
    cells = json.loads(COMPARISON_FILE.read_text(encoding="utf-8"))
    assert briefings and cells
    for b in briefings:
        assert b["status"] in {"draft", "published"}, b["title"]
        assert (b["status"] == "published") == bool(b["last_reviewed_by_you"]), b["title"]
    assert not any("TO CONFIRM" in c["position"] for c in cells)
