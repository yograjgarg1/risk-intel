# Source check: CPS 230 and APS 116

20 September 2026. Checklist step 1. I re-read both sources and checked the drafts claim by claim. Corrections are already applied to `data/seed_briefings.json`. What is left is your read, which is the part that earns the review date.

## CPS 230 Operational Risk Management

Source: https://www.apra.gov.au/standards/cps-230
Amendments: https://www.apra.gov.au/news-and-publications/apra-finalises-targeted-amendments-cps-230-operational-risk-management

| Claim in the draft | What the source says | Status |
|---|---|---|
| Single cross-industry operational risk standard | Applies to ADIs, general insurers, life companies, private health insurers and RSE licensees | Confirmed |
| Three obligations: controls, critical operations, service providers | Operational risk management, business continuity with tolerance levels, service provider management | Confirmed |
| Board approves tolerance levels | Board is "ultimately accountable" for oversight, approves business continuity plans and tolerance levels | Confirmed, now stated as board accountability across all three |
| Replaced older outsourcing and business continuity standards | Confirmed by APRA's operational risk page | Confirmed |
| Amendments finalised 30 April 2026 | Confirmed, covering CPS 230, CPG 230 and the material service provider register template | Confirmed |
| Exemptions for "government agencies, regulators, central banks and financial market exchanges" | Seven categories, not four: the four above plus operators of clearing and settlement facilities, operators of payment systems and schemes, and financial messaging infrastructures | **Corrected**, all seven now listed |
| "The current version commences 1 July 2026" | The standard commenced 1 July 2025; the amended version commences 1 July 2026 | **Corrected**, both dates now stated |
| Transition ends 1 July 2026 | Pre-existing service provider contracts get relief until the earlier of contract renewal or 1 July 2026 | **Corrected**, the renewal trigger was missing |
| Not previously mentioned | Notification windows: 72 hours for a material operational incident, 24 hours for a critical operation beyond tolerance, 20 business days for a material service arrangement | **Added**, concrete and quotable |
| `effective_date` was 2025-07-01 | The version in force from 1 July 2026 is the current one | **Changed to 2026-07-01** |

## APS 116 Capital Adequacy: Market Risk (and APG 116)

Source: https://www.apra.gov.au/standards/aps-116

| Claim in the draft | What the source says | Status |
|---|---|---|
| Commenced 1 January 2025 | Confirmed | Confirmed |
| Applies to ADIs except foreign ADIs, PPF providers, and those with no trading book, FX or commodity positions | Confirmed | Confirmed |
| Standard method, internal model approach, or a combination with approval | Confirmed | Confirmed |
| Standard method charges: interest rate maturity or duration ladder, 8% equity specific and general, 8% FX net open position and gold, 15% commodities plus 3% spread | Confirmed | Confirmed |
| Internal models: 60-day average VaR times a multiplier of at least 3.0 plus the previous day's VaR, same for stressed VaR, plus incremental risk charge and comprehensive risk measure | Confirmed. Minimum multiplication factor is three; the plus factor runs zero to one on backtesting performance; stressed VaR and the IRC are both mandatory | Confirmed |
| Model approval and material changes need APRA sign-off | Confirmed. I removed the paragraph numbers: the January 2025 version renumbered them, and a wrong citation is worse than none | **Corrected** |
| "Counterparty credit risk sits under APS 112 or APS 180" | Paragraph 8 sends counterparty credit risk to **APS 112 or APS 113**, depending on the credit risk approach used | **Corrected**, this was wrong |
| FRTB is not live in Australia | The in-force standard is the VaR and stressed VaR framework, not Expected Shortfall, so yes | Confirmed, with the caveat below |

The same paragraph-number correction was applied to the APRA validation cell in the comparison table.

## What only you can do

1. **Read both sources.** CPS 230 is about 20 pages; APS 116 is longer but you only need the body and Attachment C. Skim for anything the table above does not cover.
2. **Reword a paragraph in each summary in your own voice.** They are accurate but they are my sentences, and the site's value is that a person wrote it.
3. **Confirm the FRTB timeline.** I could only find APRA's October 2021 timeline, whose 1 January 2025 date passed without FRTB arriving. Check the latest policy priorities paper before publishing the claim that there is no current date.
4. **Check nothing has moved since 19 September**, particularly on APRA's news page.

## Then publish

```bash
python -m scripts.review publish --briefing "CPS 230 Operational Risk"
python -m scripts.review publish --briefing "APS 116"
python -m scripts.review list
streamlit run frontend/Briefing_library.py
```

The site will then show exactly two briefings, and the comparison page will still show "Under review" in every cell until you publish a framework.
