# Source check: SR 26-2 (US model risk guidance)

20 September 2026. Checklist step 3. These are the seven cells that fill the US column of the comparison page. I checked each against the SR 26-2 attachment and a law-firm summary of what changed from SR 11-7, and sharpened three of them today. Read the guidance, confirm the table, then publish the column.

Primary source: https://www.federalreserve.gov/supervisionreg/srletters/SR2602.htm
Attachment (the guidance itself): https://www.federalreserve.gov/supervisionreg/srletters/SR2602a1.pdf
What changed from SR 11-7: https://www.sullcrom.com/insights/memo/2026/April/OCC-Fed-FDIC-Issue-Revised-Guidance-Model-Risk-Management

## The seven cells

| Dimension | What the cell says | What to confirm |
|---|---|---|
| Definition of a model | Narrowed to complex quantitative methods grounded in statistical, economic or financial theory. Simple calculations and deterministic rule-based processes are out. | That the definition turns on "complex" quantitative method, and that simple arithmetic and deterministic rule-based processes are named as exclusions. |
| Scope and threshold | Described as most relevant to banking organisations above USD 30 billion in total assets, plus smaller institutions with significant model risk. | The USD 30 billion figure, and the wording that smaller institutions with significant model risk are still in view. |
| AI treatment | Generative and agentic AI are excluded as novel and rapidly evolving; the agencies signal separate future work. | That generative and agentic AI are excluded as novel and rapidly evolving, and what the agencies say banks should do with them instead. |
| Model inventory | Expects a comprehensive set of information on models under development or in use, detailed enough to understand model risk individually and in aggregate. Oversight scales with materiality, which is set by model purpose together with model exposure: an immaterial model can be monitored rather than fully validated. | The materiality framing (purpose together with exposure) and that immaterial models can be monitored rather than validated. |
| Validation | Covers conceptual soundness, outcomes analysis and ongoing monitoring, carried out by people with sufficient independence to maintain objectivity. Quality is said to rest on the rigour of the review rather than on organisational structure, and SR 11-7's at-least-annual validation cadence is gone: frequency now follows materiality. | The phrase about independence sufficient to maintain objectivity, and that no fixed validation frequency is prescribed. |
| Governance | Principles-based: model risk management "benefits from clear roles and responsibilities with well-defined accountability", framed around developers, validators and users. SR 11-7's prescriptive board approval and annual policy review are not carried over, and the guidance states it does not set enforceable standards. | That roles and accountability replaced SR 11-7's board approval and annual policy review, and the sentence saying the guidance is not enforceable. |
| Effective date | Issued 17 April 2026 by the Fed, OCC and FDIC. Supersedes SR 11-7 (2011) and SR 21-8. | Issue date 17 April 2026 and that it supersedes both SR 11-7 and SR 21-8. |

## What changed in these cells today

Three cells were rewritten after reading a detailed comparison with SR 11-7. The new points, all worth having in an interview:

- **Materiality drives oversight.** Model purpose together with model exposure sets materiality, and an immaterial model can be monitored rather than fully validated. SR 11-7 treated materiality as a general consideration only.
- **The annual cadence is gone.** SR 11-7 expected review or validation at least annually. SR 26-2 leaves frequency to materiality, and asks for validators with "sufficient independence to maintain objectivity" rather than a prescribed structure.
- **It is explicitly not enforceable.** The guidance states it does not set enforceable standards and that non-compliance will not by itself draw supervisory criticism. That is a genuine change in posture and an easy thing to be wrong about.

The SR 26-2 briefing in the library now carries these points too, so read it again before you publish it.

## Then publish

```bash
python -m scripts.review publish --comparison "SR 26-2"
python -m scripts.review publish --briefing "US revised guidance"   # optional, the briefing itself
python -m scripts.review list
```

Publishing the column lights up the US side of the comparison page. The other three columns keep showing "Under review" until you read those sources, which is the honest state of play and looks deliberate rather than broken.

