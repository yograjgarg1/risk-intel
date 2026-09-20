from datetime import date
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture()
def ingest(tmp_path, monkeypatch):
    monkeypatch.setenv("RISK_INTEL_DB", str(tmp_path / "ingest.db"))
    from ingestion import check_sources

    return check_sources


def test_parse_apra_listing(ingest):
    html = (FIXTURES / "apra_listing_sample.html").read_text()
    src = ingest.Source("APRA", "https://www.apra.gov.au/news-and-publications", "apra_html", None)
    items = ingest.parse_apra_html(html, src)
    assert [i.title for i in items][:2] == [
        "APRA finalises targeted amendments to CPS 230",
        "Quarterly Superannuation Product Statistics",
    ]
    assert items[0].url == "https://www.apra.gov.au/news-and-publications/apra-finalises-targeted-amendments-cps-230"
    assert items[0].detected_date == date(2026, 4, 30)
    # pagination / filter links are ignored
    assert all("?" not in i.url for i in items)


def test_parse_rss_rdf(ingest):
    xml = (FIXTURES / "rba_rss_sample.xml").read_text()
    src = ingest.Source("RBA-speeches", "https://example.org/rss", "rss", None)
    items = ingest.parse_rss(xml, src)
    assert len(items) == 2
    assert items[0].detected_date == date(2026, 9, 3)


def test_relevance_filter(ingest):
    src = ingest.Source("APRA", "x", "apra_html", ingest.RISK_KEYWORDS)
    keep = ingest.FoundItem("APRA", "APRA finalises targeted amendments to CPS 230", "u1", None)
    drop = ingest.FoundItem("APRA", "Quarterly Superannuation Product Statistics", "u2", None)
    assert ingest.is_relevant(keep, src)
    assert not ingest.is_relevant(drop, src)
    bcbs = ingest.Source("Basel Committee", "x", "rss", None, title_must_contain="basel committee")
    assert ingest.is_relevant(ingest.FoundItem("B", "Basel Committee publishes X", "u", None), bcbs)
    assert not ingest.is_relevant(ingest.FoundItem("B", "BIS Annual Economic Report", "u", None), bcbs)


def test_run_queues_once_and_never_publishes(ingest):
    html = (FIXTURES / "apra_listing_sample.html").read_text()
    src = ingest.Source("APRA", "https://www.apra.gov.au/news-and-publications", "apra_html", ingest.RISK_KEYWORDS)
    first = ingest.run([src], fetcher=lambda s: html, today=date(2026, 5, 15))
    assert first["APRA"] == 2  # CPS 230 item + undated capital item; stats item filtered; old item too old
    second = ingest.run([src], fetcher=lambda s: html, today=date(2026, 5, 16))
    assert second["APRA"] == 0  # duplicates ignored

    from app import db
    with db.connect() as conn:
        assert conn.execute("SELECT COUNT(*) FROM briefings").fetchone()[0] == 0
        assert conn.execute("SELECT COUNT(*) FROM pending_review").fetchone()[0] == 2


def test_fetch_failure_does_not_crash(ingest):
    def boom(_):
        raise ConnectionError("site down")

    src = ingest.Source("APRA", "x", "apra_html", None)
    assert ingest.run([src], fetcher=boom) == {"APRA": -1}
