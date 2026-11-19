# Acquisition endpoint policy for equity backtests — APPROVED

Status: **approved by the repository owner on 2026-11-19**. It is enforced in `evaluation/validation_gate.py` (`acquired_documented` labels need `event_date`, `value_basis`, a source and a matched `horizon_years`). Approval fixes the endpoint rule only; it does not lift any other gate blocker, and no cohort has been scored with it.

## Problem

Five-year equity market cap is the primary target. An acquired issuer has no market cap at the target date, but its shareholders received an observable payment. Dropping such issuers selects survivors. Scoring them as zero treats a premium sale as a wipeout. In the two cloud rosters, 6 of 24 issuers were acquired within five years: 5 of 10 in cloud2015 and 1 of 14 in cloud2020. Every deal was at or above the issuer's May-2015 market cap (`python -m evaluation.saas_exit`).

## Proposed rule

1. **Event record.** For each issuer, record the first terminal event inside the window: acquisition close, bankruptcy filing or delisting. Record its date τ, the consideration per share and the value basis. Sources go in `data/stage4_exit_events.csv` or its successors.
2. **Label.** For an acquisition, the label is the **equity value paid**: per-share consideration × fully diluted shares at close. If only a headline transaction value is sourced, use it only when it is identified as equity value. An enterprise-value headline is converted using the last pre-close reported net cash, and that conversion is flagged. Stock consideration is valued at the acquirer's closing price on τ. For a bankruptcy or liquidation, the label is the documented recovery to common equity, which is zero only when legally evidenced.
3. **Prediction.** The model's equity value at horizon k = max(1, round(τ − origin in years)), from the same frozen run (`predict_value(..., horizon=k)`). Predictions are never re-run after τ is known.
4. **Scoring.** Report three sets: standalone five-year endpoints, event endpoints (matched horizon), and the pooled set used by the gate. Report coverage for each. An issuer with neither a five-year market cap nor a sourced event label makes the cohort ineligible for release scoring; it is not dropped.
5. **No compounding to the target date.** Carrying consideration forward would require a reinvestment-return assumption that the model does not make. Matching the horizon avoids it.

## Known weaknesses

- A rounded horizon creates up to six months of timing mismatch.
- Takeover premia mean event labels are systematically above a contemporaneous standalone market cap, so pooled bias is not comparable with a standalone-only bias.
- Headline values in the current events file mix equity and enterprise bases (flagged per row). Before any release scoring they must be replaced with per-share × diluted share counts from the merger proxy.
