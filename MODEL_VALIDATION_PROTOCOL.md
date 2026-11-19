# Mandatory model development and release protocol / 强制训练评测规范

This adapts train/validation/test isolation, contamination control, experiment
tracking and independent TEVV to financial estimation. It does not imply
that a DCF is an LLM or that one universal LLM training standard exists.
References: [NIST AI RMF](https://airc.nist.gov/airmf-resources/airmf/5-sec-core/),
[NIST blind testbeds](https://pages.nist.gov/ai-technology-evaluation/),
[Google split guidance](https://developers.google.com/machine-learning/crash-course/overfitting/dividing-datasets).

## 0. Preregister / 预注册

Freeze study universe as of each forecast origin, including failed, acquired and
delisted issuers. Record stable issuer IDs and corporate families, dates, selection
source, target (five-year equity market cap, USD B), horizon, loss, baselines,
metrics, model entrypoint, allowable proxies, seed, dependency versions and release
thresholds. Do not change them after seeing holdout outcomes. An independent
custodian must attest that predictions and code were frozen before labels were
accessed; public historical labels already seen are development/diagnostic only.
Market cap is an observable comparator, not intrinsic value truth. Record
corporate actions, distributions, share issuance, and distinguish EV from equity.

## 1. Pre-training / 数据和参数审计

Source every company-specific field to dated primary filings with document/section,
units, fiscal period, publication date and a second independent reconciliation
(or explicitly mark unreconciled). Use publication date <= forecast origin,
not fiscal period alone. Preserve original vintage; later restatements are labeled
and cannot leak into features. Reconcile revenues, EBITDA/EBIT, taxes, D&A, CapEx,
NWC, SBC, cash, debt, lease liabilities, funding and legal entities. Never equate
CFO-CapEx with FCFF. Track observed/estimated/proxy/missing status and uncertainty
for every parameter. Customer states, churn, vendor switching, price/volume,
acquisition, competition and commitments require company-specific evidence.
Missing states block full validation; aggregate restrictions are diagnostics.

## 2. Training / 参数训练

Use chronological development folds with issuer-family separation, and a five-year
label embargo (training labels must already be published before the next fold's
forecast origin). Fit scaling, imputation, covariance shrinkage, factor selection,
and hyperparameters inside each fold. Use nested validation; never fit using
test labels. Record all experiments, including failures, with parameter bounds,
objective, random seeds, hashes and reproducible commands. Fit revenue, margin,
FCFF, survival/renewal, WACC and capital structure components on their appropriate
training labels. Optimize equity market-cap error separately; revenue-only tuning
does not qualify. Use a zero-safe primary loss:

```math
L=\frac{1}{n}\sum_i|\log(1+\widehat V_i)-\log(1+V_i)|+\lambda\|\theta\|_2^2
```

All values in USD B; nonnegative market caps; zero for a documented terminal
equity wipeout only. M&A/de-listing require separately documented outcomes and
coverage, not zero by default. Monetary predictions and labels use identical dates.
Compare flat market cap and constant P/S using only origin-known inputs.

## 3. Post-training / 独立评测

Freeze exact production code and fitted parameters before independent scoring.
Run the same joint engine and same state/cashflow/continuation logic used for
Anthropic, with only evidence-based company profiles. Evaluate five-year revenue,
FCFF (matched definition), equity market cap and survival separately; report
WAPE, signed bias, zero-safe log error, coverage, subgroup results, and uncertainty.
Run baseline comparisons, ablations, residual/covariance checks, regime and
missingness stresses. Report market-cap divergences without claiming they measure
intrinsic value error. No post-test tuning: a revealed test set is retired to
development and a new independent test set is required.

## 4. Release / 发布门禁

Repository-specific minimal gates, fixed before any new final evaluation:
at least ten distinct issuer families across at least two final technology-cycle
cohorts, no overlap with development/exposed families, correct horizon, all
eligible outcomes accounted for, equity WAPE <= 30%, absolute signed bias <= 15%,
WAPE strictly better than both naive baselines. These numerical thresholds are
project policy, not industry standards or a guarantee of generalization.
An independent reviewer must verify source/parameter evidence, freeze records,
training and evaluation logs and full-model execution. Hashes prevent accidental
file changes but cannot independently prove historical blindness or source truth.
The gate is necessary, not sufficient; review evidence must be independently
authenticated. Never represent a failed gate as a validated valuation.

Use `python -m evaluation.validation_gate --audit` for current diagnostics and
`python -m evaluation.validation_gate --manifest PATH` for a release candidate.
The manifest references a preregistration, provenance CSV, predictions CSV,
labels CSV, frozen parameters, code hash, review/freeze evidence and training logs.
See the executable gate and tests for schema. For current historical results,
release is BLOCKED. Anthropic is application-only, never a training label.
