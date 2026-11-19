# Stage 4 margin-path component — preregistration

Written on 2026-11-19, before any development comparison was computed and before any stage-4 outcome was opened. This preregisters one component only: the five-year free-cash-flow margin path. Equity market cap, the release gate and every other component are unchanged and remain BLOCKED.

## Why this component first

The engine revision showed that, on the exposed cloud cohort, the model ranks five-year revenue and FCF well but not market caps. The base case's largest single open assumption is the margin path: compute cost ratio 48% against an observed 56.6%, and other opex 25% against 47.2%. A margin component can be tested on fundamentals without depending on market multiples.

## Target

FCF margin = (operating cash flow − purchases of property and equipment − capitalized software payments) / revenue. It is measured in the fiscal year whose end date falls in the target calendar year: 2020 for the cloud2015 episode and 2025 for cloud2020. This is a CFO-based proxy, not FCFF. SBC is not deducted. An SBC-adjusted margin is reported as an auxiliary metric only.

## Inputs (origin-known only)

Inputs come from the latest annual filing (10-K / 20-F / 40-F) **filed on or before** the origin date, 2015-12-31 or 2020-12-31: revenue, prior-year revenue, CFO, capex, capitalized software and SBC, using original-vintage XBRL facts from that filing (`data/stage4_origin_inputs.csv`). Later restatements are not used. Values are single-source (SEC XBRL); a second reconciliation against the filing HTML is still pending.

Horizon h = years from the input fiscal-year end to the same month-day in the target year.

## Development data

`data/margin_dev_panel.csv` contains seven observations from previously exposed families only: Salesforce and ServiceNow (2015→2020); Adobe, Salesforce, PayPal, ServiceNow and Shopify (2020→2025). The same input and target rules apply. This is far too small to estimate anything with confidence, so the candidate models have at most one fitted parameter.

## Candidates (fixed now)

| id | prediction | fitted on dev |
|---|---|---|
| hold | m_T = m_0 | none |
| fade15 | m_T = m_0 + (0.15 − m_0)·min(h/10, 1) (the pre-revision engine) | none |
| pooled | m_T = mean development target margin | the mean |
| converge | m_T = m* + (m_0 − m*)·2^(−h/3); half-life fixed at 3 years a priori | m* |
| leverage | m_T = m_0 + b·max(0, ln(R_0/R_−1)) | b |

## Loss and selection rule (fixed now)

The primary loss is the equal-weight mean absolute error in margin percentage points under leave-one-*family*-out on the development panel (5 families, 7 observations). The candidate with the lowest LOO MAE is selected. If its MAE is not at least 1.0 percentage point lower than `hold`, `hold` is selected instead (simplicity rule). The selected model is then refit on all seven development observations.

## Frozen predictions

Predictions for **all** candidates on all 17 stage-4 issuers are written to `evaluation/stage4_margin_predictions.csv`. The SHA-256 of the predictions, the inputs, the code and this file go into `evaluation/stage4_margin_freeze.json`. Only the selected model is primary; the others are reported but cannot replace it after labels are opened.

## Endpoints, coverage and promotion threshold (fixed now)

- An issuer with no standalone annual filing covering the target fiscal year (acquired, merged or delisted before then) has **no margin label**. It is counted in coverage and never imputed as zero. Survival and acquisition are separate components.
- The primary stage-4 metric is MAE in margin points over standalone endpoints. Signed bias, Spearman rank correlation and per-episode results are also reported.
- **Promotion threshold:** the selected model must have a lower stage-4 MAE than both `hold` and `pooled`, in the pooled sample and in each episode separately, with at least 8 scored issuers. Otherwise the component is not promoted and the engine's margin assumptions stay as scenario inputs.
- Opening labels retires this roster for margin-component testing. Any later change needs a new roster.

## Known limitations, disclosed before scoring

- The modeler (an LLM) has general training knowledge of these companies' post-origin history, so this is not a blind test with respect to the modeler. Mitigations: parameters are fitted only on the development panel, the rule is mechanical, and predictions are hashed before labels are opened. Independent custody of the labels is still required by the protocol and is not provided here.
- While collecting data, an XBRL `frames` request (later discarded for vintage reasons) returned accession numbers dated 2016–2022, and an EDGAR company search listed later filing dates. This revealed that some issuers were still filing in those years, which is weak survival information. No margin, revenue or market value after the origin was used.
- The two episodes are both cloud software; the protocol's two-technology-cycle requirement is not met by this roster.
