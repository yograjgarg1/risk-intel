import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("RISK_INTEL_DB", str(tmp_path / "test.db"))
    from app.main import app
    from scripts.seed import seed

    seed(tmp_path / "test.db")
    with TestClient(app) as c:
        yield c


NEW = {
    "title": "Test briefing on model inventories",
    "source_name": "APRA",
    "source_url": "https://www.apra.gov.au/example",
    "jurisdiction": "Australia",
    "topic_tags": ["model risk", "Model Risk", " inventory "],
    "document_type": "speech",
    "publish_date": "2026-01-01",
    "plain_language_summary": "A test summary that is long enough to validate.",
    "why_it_matters": "It is a test.",
    "who_it_applies_to": "Nobody",
}


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_seed_loaded(client):
    rows = client.get("/briefings").json()
    assert len(rows) == 8
    # Published briefings must carry a review date; drafts must not.
    for r in rows:
        assert (r["status"] == "published") == bool(r["last_reviewed_by_you"]), r["title"]
    assert any(r["status"] == "draft" for r in rows)


def test_create_and_get(client):
    r = client.post("/briefings", json=NEW)
    assert r.status_code == 201
    body = r.json()
    assert body["topic_tags"] == ["model risk", "inventory"]  # de-duplicated, trimmed
    got = client.get(f"/briefings/{body['id']}").json()
    assert got["title"] == NEW["title"]


def test_duplicate_rejected(client):
    assert client.post("/briefings", json=NEW).status_code == 201
    assert client.post("/briefings", json=NEW).status_code == 409


def test_validation(client):
    bad = dict(NEW, source_url="not a url")
    assert client.post("/briefings", json=bad).status_code == 422
    bad = dict(NEW, status="live")
    assert client.post("/briefings", json=bad).status_code == 422


def test_filter_topic_and_jurisdiction(client):
    rows = client.get("/briefings", params={"topic": "model risk"}).json()
    assert {r["jurisdiction"] for r in rows} == {"Australia", "United States", "United Kingdom", "Canada"}
    rows = client.get("/briefings", params=[("topic", "model risk"), ("topic", "AI")]).json()
    assert {r["title"][:4] for r in rows} == {"APRA", "OSFI"}
    rows = client.get("/briefings", params={"jurisdiction": "australia"}).json()
    assert len(rows) == 4  # CPS 230, APS 220, AI letter, APS 116


def test_search(client):
    rows = client.get("/briefings", params={"q": "expected shortfall"}).json()
    titles = {r["title"] for r in rows}
    assert any("FRTB" in t for t in titles)
    assert any("APS 116" in t for t in titles)  # the Australian contrast with FRTB
    rows = client.get("/briefings", params={"q": "stressed var"}).json()
    assert [r["title"] for r in rows] == ["APS 116 Capital Adequacy: Market Risk (and APG 116)"]


def test_not_found(client):
    assert client.get("/briefings/9999").status_code == 404


def test_facets(client):
    f = client.get("/facets").json()
    assert "model risk" in f["topics"]
    assert "Australia" in f["jurisdictions"]


def test_facets_by_status(client):
    published = client.get("/facets", params={"status": "published"}).json()
    drafts = client.get("/facets", params={"status": "draft"}).json()
    # The public facets only offer values a visitor can actually reach.
    assert published["jurisdictions"] == ["Australia"]
    assert "CPS 230" in published["topics"] and "SR 26-2" not in published["topics"]
    assert "Canada" in drafts["jurisdictions"]
