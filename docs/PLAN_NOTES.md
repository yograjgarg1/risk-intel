# Build plan notes (checked 15 September 2026)

Corrections and additions to BUILD_PLAN.md after checking the regulatory content against current sources.

## Corrections to the plan

1. **SR 11-7 has been replaced.** On 17 April 2026 the Federal Reserve, OCC and FDIC issued revised model risk management guidance (Fed SR 26-2), superseding SR 11-7 and SR 21-8. It narrows the definition of a model, is most relevant to banks above USD 30 billion in assets, and excludes generative and agentic AI. Any "global model risk" library needs this, and interview answers should reference SR 26-2, not SR 11-7 alone.
2. **The plan is thin on global model risk guidance.** The pitch says "Australian and global", but the v1 list has no dedicated model risk frameworks. Added: SR 26-2 (US), PRA SS1/23 (UK, effective 17 May 2024, updated April 2026) and OSFI E-23 (Canada, effective 1 May 2027, covers AI).
3. **"APRA model risk expectations" needs a sharper framing.** There is still no single APRA model risk standard. Model expectations sit in APS 113 (IRB credit models), APS 116 (market risk internal models), APS 117 (IRRBB), CPS 220 (risk management), CPS 230 and supervisory letters. The most relevant recent item is APRA's 30 April 2026 letter to industry on AI risk management (inventories, lifecycle governance, performance monitoring).
4. **FRTB is not live in Australia.** The current APS 116 (commenced 1 January 2025) still uses the standard method and internal model approach. APRA's February 2023 policy priorities said revised market risk standards would take effect no earlier than 2026; confirm the current timeline in APRA's latest policy priorities before writing a date. Globally, the EU adopted temporary FRTB relief in June 2026 intended to apply from 1 January 2027 for three years.
5. **The plan omits APS 116 itself.** For a "market risk" platform, APS 116 / APG 116 should be a core briefing alongside the Basel standard.
6. **CPS 230 dates have moved on.** Original commencement was 1 July 2025. APRA finalised targeted amendments on 30 April 2026, and the current version commences 1 July 2026 (also the end of the transition for pre-existing service provider contracts).
7. **APS 220's current version is effective 1 January 2023.**
8. **APRA's tiering is changing.** APRA's December 2025 proportionality proposal would raise the SFI threshold from $20 billion to $30 billion and add a "Most Significant Financial Institution" tier above $300 billion; finalisation is expected by end of 2026. Worth a briefing, because "who it applies to" depends on it.
9. **Ingestion sources.** APRA's News and Publications page has no RSS feed, so it needs HTML parsing. RBA has official RSS feeds. BIS does not list a Basel Committee-only feed, so the script reads the BIS press release feed and keeps Basel Committee items.
10. **GitHub Actions has no persistent database.** The included workflow runs a dry run and prints candidates to the job log. To keep a queue in the cloud, commit the SQLite file back to the repo or move to hosted Postgres.
11. **Positioning overlap.** airiskaware.com already publishes CPS 230 content. The model risk and market risk angle (SR 26-2 vs SS1/23 vs E-23 vs APRA's scattered expectations) is the clearer differentiator; lead with that.

## Seed briefings shipped (all `draft`)

| # | Briefing | Jurisdiction |
|---|---|---|
| 1 | CPS 230 Operational Risk Management | Australia |
| 2 | APS 220 Credit Risk Management | Australia |
| 3 | APRA letter to industry on AI risk management (Apr 2026) | Australia |
| 4 | Basel Committee market risk standard (FRTB) | Global |
| 5 | US revised model risk guidance (SR 26-2) | United States |
| 6 | PRA SS1/23 model risk management principles | United Kingdom |
| 7 | OSFI Guideline E-23 (2027) | Canada |

These were drafted from the sources listed and must be read against the source documents, rewritten in your own words and dated before publishing. The site's credibility rests on `last_reviewed_by_you`.

## Content backlog to reach 15 to 20 briefings

- APS 116 Capital Adequacy: Market Risk and APG 116
- APS 113 Internal Ratings-based Approach (model approval and validation expectations)
- APS 117 Interest Rate Risk in the Banking Book
- CPS 220 Risk Management
- CPS 234 Information Security (model and data platform context)
- APRA proportionality proposal (Dec 2025): SFI and MSFI tiers
- APRA's current policy priorities: market risk and counterparty credit risk timeline
- APS 180 Counterparty Credit Risk
- BCBS 239 Principles for effective risk data aggregation and risk reporting
- EU FRTB temporary relief (June 2026)
- RBA Financial Stability Review (latest edition) market risk themes
- GARP FRM concepts glossary: VaR, Expected Shortfall, backtesting, P&L attribution, model validation, stress testing

## Sources

- APRA CPS 230: https://www.apra.gov.au/standards/cps-230
- APRA CPS 230 amendments (Regulation Tomorrow, May 2026): https://www.regulationtomorrow.com/2026/05/apra-finalises-targeted-amendments-to-cps-230-operational-risk-management/
- APRA APS 220: https://www.apra.gov.au/standards/aps-220
- APRA APS 116: https://www.apra.gov.au/standards/aps-116
- APRA Policy Priorities, February 2023: https://www.apra.gov.au/system/files/2023-02/Information%20paper%20APRA's%20Policy%20Priorities%20-%20February%202023.pdf
- APRA letter on AI: https://www.apra.gov.au/apra-letter-to-industry-on-artificial-intelligence-ai
- APRA proportionate banking framework: https://www.apra.gov.au/%E2%80%8Ba-more-proportionate-banking-prudential-framework
- APRA News and Publications: https://www.apra.gov.au/news-and-publications
- BCBS market risk standard (d457): https://www.bis.org/bcbs/publ/d457.htm
- European Commission FRTB relief (June 2026): https://finance.ec.europa.eu/news/eu-temporarily-amends-prudential-rules-banks-market-risk-2026-06-08_en
- Federal Reserve SR 26-2: https://www.federalreserve.gov/supervisionreg/srletters/SR2602.pdf
- Orrick summary of the 2026 interagency guidance: https://www.orrick.com/en/Insights/2026/04/Agencies-Overhaul-Model-Risk-Management-Guidance-for-Banks-Heres-What-Changed
- PRA SS1/23: https://www.bankofengland.co.uk/prudential-regulation/publication/2023/may/model-risk-management-principles-for-banks-ss
- OSFI E-23: https://www.osfi-bsif.gc.ca/en/guidance/guidance-library/guideline-e-23-model-risk-management-2027
- RBA RSS feeds: https://www.rba.gov.au/updates/rss-feeds.html
- BIS RSS feeds: https://www.bis.org/rss
