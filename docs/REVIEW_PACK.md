# Review pack, 19 September 2026

Everything in the library is still `draft`. This pack is the shortest path from here to a live Phase 1 site: read each source, confirm the points listed, then run the publish command under it. Nothing gets a review date until you have read the source yourself.

Commands come from `scripts/review.py`:

```bash
python -m scripts.review list                              # what is reviewed, what is not
python -m scripts.review publish --briefing "APS 116"      # one briefing
python -m scripts.review publish --comparison "SR 26-2"    # all 7 cells for one framework
python -m scripts.review unpublish --briefing "APS 116"    # undo
```

## Briefings

### CPS 230 Operational Risk Management

Source: https://www.apra.gov.au/standards/cps-230

- Confirm the dates in the summary against the source: publish 2023-07-17, effective 2025-07-01.
- Confirm nothing has superseded it, and that "who it applies to" still matches.
- Rewrite at least one paragraph in your own words before publishing, so the voice is yours.

```bash
python -m scripts.review publish --briefing "CPS 230 Operational Risk"
```

### APS 220 Credit Risk Management

Source: https://www.apra.gov.au/standards/aps-220

- Confirm the dates in the summary against the source: publish date not stated, effective 2023-01-01.
- Confirm nothing has superseded it, and that "who it applies to" still matches.
- Rewrite at least one paragraph in your own words before publishing, so the voice is yours.

```bash
python -m scripts.review publish --briefing "APS 220 Credit Risk Mana"
```

### APRA letter to industry on artificial intelligence (AI) risk management

Source: https://www.apra.gov.au/apra-letter-to-industry-on-artificial-intelligence-ai

- Confirm the dates in the summary against the source: publish 2026-04-30, effective date not stated.
- Confirm nothing has superseded it, and that "who it applies to" still matches.
- Rewrite at least one paragraph in your own words before publishing, so the voice is yours.

```bash
python -m scripts.review publish --briefing "APRA letter to industry "
```

### Basel Committee minimum capital requirements for market risk (FRTB)

Source: https://www.bis.org/bcbs/publ/d457.htm

- Confirm the dates in the summary against the source: publish 2019-01-14, effective 2023-01-01.
- Confirm nothing has superseded it, and that "who it applies to" still matches.
- Rewrite at least one paragraph in your own words before publishing, so the voice is yours.
- Applicability note to check: Not live in Australia; EU temporary relief from 1 January 2027 for three years

```bash
python -m scripts.review publish --briefing "Basel Committee minimum "
```

### US revised guidance on model risk management (SR 26-2)

Source: https://www.federalreserve.gov/supervisionreg/srletters/SR2602.pdf

- Confirm the dates in the summary against the source: publish 2026-04-17, effective date not stated.
- Confirm nothing has superseded it, and that "who it applies to" still matches.
- Rewrite at least one paragraph in your own words before publishing, so the voice is yours.
- Applicability note to check: Most relevant above USD 30b in total assets
- Supersedes claim to check: SR 11-7; SR 21-8

```bash
python -m scripts.review publish --briefing "US revised guidance on m"
```

### PRA SS1/23 Model risk management principles for banks

Source: https://www.bankofengland.co.uk/prudential-regulation/publication/2023/may/model-risk-management-principles-for-banks-ss

- Confirm the dates in the summary against the source: publish 2023-05-17, effective 2024-05-17.
- Confirm nothing has superseded it, and that "who it applies to" still matches.
- Rewrite at least one paragraph in your own words before publishing, so the voice is yours.
- Applicability note to check: Firms with internal model approval (IRB, IMA or IMM); applied proportionately

```bash
python -m scripts.review publish --briefing "PRA SS1/23 Model risk ma"
```

### OSFI Guideline E-23 Model Risk Management (2027)

Source: https://www.osfi-bsif.gc.ca/en/guidance/guidance-library/guideline-e-23-model-risk-management-2027

- Confirm the dates in the summary against the source: publish 2025-09-11, effective 2027-05-01.
- Confirm nothing has superseded it, and that "who it applies to" still matches.
- Rewrite at least one paragraph in your own words before publishing, so the voice is yours.
- Applicability note to check: All federally regulated financial institutions; applied proportionately

```bash
python -m scripts.review publish --briefing "OSFI Guideline E-23 Mode"
```

### APS 116 Capital Adequacy: Market Risk (and APG 116)

Source: https://www.apra.gov.au/standards/aps-116

- Confirm the dates in the summary against the source: publish 2025-01-01, effective 2025-01-01.
- Confirm nothing has superseded it, and that "who it applies to" still matches.
- Rewrite at least one paragraph in your own words before publishing, so the voice is yours.
- Applicability note to check: ADIs with trading book activity or foreign exchange or commodity positions; foreign ADIs and purchased payment facility providers are excluded

```bash
python -m scripts.review publish --briefing "APS 116 Capital Adequacy"
```

## Comparison cells

All 28 cells were written on 19 September 2026 from the primary sources listed below. They still need your read before they show publicly. Publish a framework at a time, once you have read that framework's source end to end.

### SR 26-2

| Dimension | Position (abridged) | Source |
|---|---|---|
| Definition of a model | Narrowed to complex quantitative methods grounded in statistical, economic or financial theory. Simple calculations and deterministic rule-based proce... | https://www.federalreserve.gov/supervisionreg/srletters/SR2602.htm |
| Scope and threshold | Described as most relevant to banking organisations above USD 30 billion in total assets, plus smaller institutions with significant model risk. | https://www.federalreserve.gov/supervisionreg/srletters/SR2602.htm |
| AI treatment | Generative and agentic AI are excluded as novel and rapidly evolving; the agencies signal separate future work. | https://www.federalreserve.gov/supervisionreg/srletters/SR2602.htm |
| Model inventory | Expects a comprehensive set of information on models under development or in use, detailed enough to understand model risk at both the individual and ... | https://www.federalreserve.gov/supervisionreg/srletters/SR2602a1.pdf |
| Validation | Validation covers conceptual soundness, outcomes analysis and ongoing monitoring. Quality is said to rest on the rigour and effectiveness of the revie... | https://www.federalreserve.gov/supervisionreg/srletters/SR2602a1.pdf |
| Governance | Written around the roles of model developers, validators and users rather than a prescribed board and senior management hierarchy, a step back from SR... | https://www.federalreserve.gov/supervisionreg/srletters/SR2602a1.pdf |
| Effective date | Issued 17 April 2026 by the Fed, OCC and FDIC. Supersedes SR 11-7 (2011) and SR 21-8. | https://www.federalreserve.gov/supervisionreg/srletters/SR2602.htm |

```bash
python -m scripts.review publish --comparison "SR 26-2"
```

### SS1/23

| Dimension | Position (abridged) | Source |
|---|---|---|
| Definition of a model | "A quantitative method that applies statistical, economic, financial, or mathematical theories, techniques, and assumptions to process input data into... | https://www.bankofengland.co.uk/-/media/boe/files/prudential-regulation/supervisory-statement/2023/ss123.pdf |
| Scope and threshold | UK-incorporated banks, building societies and PRA-designated investment firms with internal model approval for regulatory capital. Third-country branc... | https://www.bankofengland.co.uk/-/media/boe/files/prudential-regulation/supervisory-statement/2023/ss123.pdf |
| AI treatment | No separate AI regime. Risk tiering (Principle 1.3c) must weigh interpretability, explainability, transparency and the potential for designer or data ... | https://www.bankofengland.co.uk/-/media/boe/files/prudential-regulation/supervisory-statement/2023/ss123.pdf |
| Model inventory | Firms must keep a model inventory and tier models by risk. | https://www.bankofengland.co.uk/prudential-regulation/publication/2023/may/model-risk-management-principles-for-banks-ss |
| Validation | Principle 4: independent model validation. | https://www.bankofengland.co.uk/prudential-regulation/publication/2023/may/model-risk-management-principles-for-banks-ss |
| Governance | Principle 2: a senior manager holds overall responsibility for model risk management, with regular reporting to the board audit committee. | https://www.bankofengland.co.uk/prudential-regulation/publication/2023/may/model-risk-management-principles-for-banks-ss |
| Effective date | Effective 17 May 2024. LIAF01/26 (23 April 2026) clarified that the expectations are not conditions for internal model approval and gave firms 12 mont... | https://www.bankofengland.co.uk/prudential-regulation/publication/2026/april/low-impact-amendments-finalisation-april-2026 |

```bash
python -m scripts.review publish --comparison "SS1/23"
```

### E-23

| Dimension | Position (abridged) | Source |
|---|---|---|
| Definition of a model | "An application of theoretical, empirical, judgmental assumptions or statistical techniques, including AI/ML methods, which processes input data to ge... | https://www.osfi-bsif.gc.ca/en/guidance/guidance-library/guideline-e-23-model-risk-management-2027 |
| Scope and threshold | All federally regulated financial institutions, including foreign bank branches and foreign insurance company branches, applied in proportion to size,... | https://www.osfi-bsif.gc.ca/en/guidance/guidance-library/guideline-e-23-model-risk-management-2027 |
| AI treatment | Explicitly in scope, with extra attention to explainability, bias and autonomous decision-making. | https://www.osfi-bsif.gc.ca/en/guidance/guidance-library/guideline-e-23-model-risk-management-2027 |
| Model inventory | A comprehensive inventory of every model whose inherent risk is non-negligible, held as the enterprise-level system of record. | https://www.osfi-bsif.gc.ca/en/guidance/guidance-library/guideline-e-23-model-risk-management-2027 |
| Validation | Model review must be independent from model development and confirm that a model is properly specified, working as intended and fit for purpose, acros... | https://www.osfi-bsif.gc.ca/en/guidance/guidance-library/guideline-e-23-model-risk-management-2027 |
| Governance | Enterprise-wide model risk management with senior management oversight; intensity scales with the model risk rating. | https://www.osfi-bsif.gc.ca/en/guidance/guidance-library/guideline-e-23-model-risk-management-2027 |
| Effective date | Final guideline September 2025; effective 1 May 2027. | https://www.osfi-bsif.gc.ca/en/guidance/guidance-library/guideline-e-23-model-risk-management-2027 |

```bash
python -m scripts.review publish --comparison "E-23"
```

### APRA

| Dimension | Position (abridged) | Source |
|---|---|---|
| Definition of a model | No single APRA definition or model risk standard. Model expectations sit inside use-specific standards: APS 113 (IRB credit models), APS 116 (market r... | https://www.apra.gov.au/standards/aps-116 |
| Scope and threshold | Depends on the standard. For banking, the three-tier proportionality framework applies from 1 July 2026: SFI at $30b+ and MSFI at $300b+, with a 12-mo... | https://www.apra.gov.au/news-and-publications/apra-formalises-three-tiered-approach-to-proportionality-banking-prudential |
| AI treatment | 30 April 2026 letter to industry: board AI literacy, full-lifecycle governance, human involvement in high-risk decisions, and supplier transparency an... | https://www.apra.gov.au/apra-letter-to-industry-on-artificial-intelligence-ai |
| Model inventory | No general model inventory standard. The April 2026 AI letter expects an inventory of AI use cases. | https://www.apra.gov.au/apra-letter-to-industry-on-artificial-intelligence-ai |
| Validation | No cross-model validation standard. For IRB credit models, APS 113 paragraph 27 requires independent review of rating systems by internal audit or a s... | https://www.apra.gov.au/standards/aps-113 |
| Governance | CPS 220 (risk management framework, board accountability) and CPS 230 (operational risk, including service providers that run models and data). | https://www.apra.gov.au/standards/cps-230 |
| Effective date | No single date. APS 116 current version from 1 January 2025; AI letter 30 April 2026; CPS 230 current version from 1 July 2026. | https://www.apra.gov.au/standards/cps-230 |

```bash
python -m scripts.review publish --comparison "APRA"
```

## What was checked on 19 September 2026

| Cell | Where it came from |
|---|---|
| SR 26-2 inventory, validation, governance | SR 26-2 attachment (federalreserve.gov/supervisionreg/srletters/SR2602a1.pdf): a comprehensive set of information on models in use or under development; validation covering conceptual soundness, outcomes analysis and ongoing monitoring, with quality resting on the rigour of the review rather than organisational structure; roles framed around developers, validators and users rather than a board hierarchy |
| SS1/23 definition, AI, scope, effective date | SS1/23 PDF and LIAF01/26 (23 April 2026), which clarified that the expectations are not conditions for internal model approval and gave 12 months from a first internal model permission to comply |
| E-23 definition, inventory, validation, scope | OSFI E-23 (2027) full text: definition naming AI/ML methods, inventory of models with non-negligible inherent risk as the enterprise system of record, review independent from development, foreign bank and insurance branches in scope |
| APRA validation | APS 113 paragraph 27 (independent review by internal audit), APG 113 (model risk policy, model register, change log, issues register), APS 113 paragraphs 52 to 56 (annual attestation), APS 116 paragraphs 14 to 17 (APRA approval for internal model use) |

## One finding worth carrying into interviews

APRA's market risk review page still shows the October 2021 timeline, which pointed to the FRTB-aligned standards commencing on 1 January 2025. The APS 116 that actually commenced on 1 January 2025 is the pre-FRTB framework: VaR, stressed VaR, an incremental risk charge and a backtesting plus factor, not Expected Shortfall. So FRTB is not live in Australia and APRA has no current published implementation date. Confirm this against APRA's latest policy priorities before you say it in an interview, because it is the kind of claim an interviewer will test.

