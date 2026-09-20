# Changelog

## 0.9.0 (20 September 2026)

- **`docs/DEPLOY.md` now covers the no-git route:** creating the GitHub account, showing hidden files in Explorer so `.github`, `.streamlit` and `.gitignore` actually upload, and dragging the folder contents rather than the folder.

## 0.8.0 (20 September 2026)

SR 26-2 sharpened, ready for review.

- **Three SR 26-2 cells rewritten** after a close read of how the guidance differs from SR 11-7: materiality (model purpose together with model exposure) now drives how much oversight a model gets, with immaterial models monitored rather than validated; the at-least-annual validation cadence is gone and validators need "sufficient independence to maintain objectivity" rather than a prescribed structure; and the guidance states it does not set enforceable standards.
- **The SR 26-2 briefing** carries the same three points, plus the lighter vendor-model expectations (the explicit contingency planning requirement was dropped).
- **`docs/SOURCE_CHECK_SR26-2.md`:** the seven cells side by side with what to confirm in the source, and the publish commands.

## 0.7.0 (20 September 2026)

First content published.

- **CPS 230 and APS 116 published**, both reviewed against the source and dated 20 September 2026. The public site now shows two briefings; the other six stay draft and invisible.
- **Test guards updated** for a library that has published content: `published` and a `last_reviewed_by_you` date must travel together in both directions (a dated draft fails too), and the facets test now checks that the public filter options only offer values a visitor can reach.
- The reset test no longer uses `status` as its canary, since status is now legitimately mixed; it checks that a hand-edited field is rebuilt from the JSON instead.

## 0.6.0 (20 September 2026)

Source check on the first two briefings, ahead of publishing them.

- **CPS 230 corrected:** the exemption list is seven categories of non-traditional service provider, not four (adding operators of clearing and settlement facilities, operators of payment systems and schemes, and financial messaging infrastructures); the standard commenced 1 July 2025 with the amended version commencing 1 July 2026; transitional relief for pre-existing contracts ends at the earlier of contract renewal or 1 July 2026. Added the notification windows (72 hours, 24 hours, 20 business days) and board accountability. `effective_date` moved to 2026-07-01.
- **APS 116 corrected:** counterparty credit risk goes to APS 112 or APS 113 under paragraph 8, not APS 180. Paragraph numbers for model approval removed, because the January 2025 version renumbered them; the APRA validation cell in the comparison table was corrected the same way.
- **`docs/SOURCE_CHECK_2026-09-20.md`:** the claim-by-claim check, what changed, and what still needs Yograj's own read before publishing.

## 0.5.0 (19 September 2026)

Deploy readiness. Nothing here changes behaviour; it removes the friction between the repo and a live link.

- **Main page renamed** to `frontend/Briefing_library.py`, so the Streamlit sidebar reads "Briefing library" instead of "streamlit app". The deploy main file path changes with it.
- **CI:** `.github/workflows/tests.yml` runs pytest on every push and pull request.
- **Streamlit config:** `.streamlit/config.toml` pins the light base theme and the project's accent colour, and turns usage stats off. `.streamlit/secrets.toml` added to `.gitignore`.
- **Licence:** MIT for the code, with a note that the briefings are original summaries and the linked regulatory documents belong to the issuing regulators.
- **`docs/DEPLOY.md`:** the walk-through from an unpublished repo to a live app, including the `RISK_INTEL_CONTACT` repository secret and enabling the weekly source check.

## 0.4.0 (19 September 2026)

Phase 1 content work: everything is drafted and source-checked, and publishing is now one command.

- **Comparison cells resolved:** all eight `TO CONFIRM` cells were checked against primary sources and rewritten. Notable: SR 26-2 ties validation quality to the rigour of the review rather than to organisational structure, and frames roles around developers, validators and users instead of a board hierarchy; SS1/23's April 2026 update (LIAF01/26, 23 April 2026) clarified that its expectations are not conditions for internal model approval and gave firms 12 months from a first internal model permission to comply; E-23 names AI/ML inside the model definition itself; the APRA validation cell now cites APS 113 paragraph 27, APG 113, APS 113 paragraphs 52 to 56 and APS 116 paragraphs 14 to 17.
- **New briefing:** APS 116 Capital Adequacy: Market Risk (and APG 116), backlog item 1. The library is now 8 briefings.
- **FRTB finding:** the APS 116 in force since 1 January 2025 is the pre-FRTB framework (VaR, stressed VaR, incremental risk charge, backtesting plus factor), while APRA's market risk review page still shows the October 2021 timeline that pointed at 1 January 2025 for the FRTB-aligned standards. FRTB is not live in Australia and there is no current published date.
- **Review helper:** `scripts/review.py` (`list`, `publish`, `unpublish`) sets `last_reviewed_by_you`, flips `status` and rebuilds the database from the JSON, which stays the source of truth.
- **Review pack:** `docs/REVIEW_PACK.md` lists, per briefing and per framework, what to confirm and the exact command to run afterwards.
- **Tests:** 56 to 64, including a guard that no content ships pre-reviewed and that no `TO CONFIRM` text is left in the comparison data.

## 0.3.0 (19 September 2026)

Build plan v2.3, Prompt 4 (Phase 3 self-assessment).

- **Self-assessment:** new Streamlit page `frontend/pages/2_Self_assessment.py` with 15 weighted questions across governance, inventory, documentation, validation, monitoring, and AI and third-party models. Questions, weights, bands and the answer scale live in `data/assessment_questions.json`; each question lists the frameworks that expect it.
- **Scoring:** `app/assessment.py` holds the logic, with no Streamlit or database dependency. Answers run 0 to 3, weighted and expressed as a percentage of the maximum, banded Foundational (under 40%), Developing (40% to under 65%), Established (65% to under 85%), Advanced (85% and above).
- **Critical-gap flag:** a 0 or 1 on any inventory or validation question is flagged next to the band and never changes it, so a high total cannot hide a missing inventory or validation that is not independent.
- **Stateless:** answers are never written to the database.
- **Tests:** 32 to 56, covering band boundaries (39.9, 40, 64.9, 65, 84.9, 85), weighting, the critical-gap flag on an otherwise Advanced result, and rejection of missing, unknown or out-of-range answers.

## 0.2.0 (15 September 2026)

Build plan v2.3, Prompts 1, 2 and 2b, plus the code half of Prompt 3.

- **Briefings:** new optional `supersedes` and `applicability_note` fields. `init_db()` adds them to existing databases with `ALTER TABLE`, so no data is lost. Filled in for SR 26-2, SS1/23, E-23 and FRTB.
- **Model risk comparison:** new `framework_comparison` table, unique on (framework, dimension). `data/framework_comparison.json` holds 28 draft cells (4 frameworks by 7 dimensions); cells marked `TO CONFIRM` need the source checked. New `GET /comparison` endpoint (`reviewed_only`) and Streamlit page `frontend/pages/1_Model_risk_comparison.py`.
- **Seeding:** `scripts.seed` loads both JSON files. `--reset` now empties only `briefings` and `framework_comparison`; before, it deleted the whole database file, including the ingestion queue.
- **Deploy readiness:** Streamlit builds the database from the seed files on startup when it is missing or empty. Drafts and unreviewed comparison cells are hidden unless `SHOW_DRAFTS=1`. Filter options only list values from visible briefings (`GET /facets?status=`).
- **Ingestion:** the User-Agent contact comes from `RISK_INTEL_CONTACT`, and live fetches refuse to run without it. The GitHub Actions workflow reads it from a repository secret.
- **Tests:** 14 to 32.
- **Display fix:** dollar amounts such as $30b are escaped so Streamlit does not render them as maths.

## 0.1.0

Phase 0 scaffold with 7 draft briefings, and the Phase 2 ingestion script.
