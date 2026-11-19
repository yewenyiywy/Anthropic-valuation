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
Missing states trigger the reconstruction procedure below; aggregate restrictions
are not eligible training data or performance evidence for the production model.

### 1A. Model identity and missing-data contract (mandatory)

Before any numerical fitting, freeze a production model contract defining the
entrypoint, component list, state dimensions and transitions, customer birth,
survival, retention, pilot conversion, competition, mutually exclusive billing,
demand ceilings, pricing, commitments, cash-flow and lifecycle continuation.
Use exactly this architecture for Anthropic and every historical company; only
company-specific input distributions and trained parameters may change. A call
to the same entrypoint with identity transition matrices, disabled births,
infinite ceilings, neutral competition or a replacement cash-flow callback is
not proof of identity. Zero or identity values must be independently justified
by issuer evidence, never used as placeholders to bypass a missing mechanism.
If a new architecture removes a mechanism, revise the production model itself,
document the economic justification and restart preregistration; do not remove
it for historical tests only.

Apply the following sequence before training or evaluation:

1. Obtain dated issuer-specific reports, customer metrics and original filings;
   reconcile independently. Record observed versus unobserved fields and masks.
2. Reconstruct indirect states from origin-known evidence using identifiable
   constraints (revenue reconciliation, churn/cohort disclosures, market shares,
   downstream customer population). Use a likelihood or prior with uncertainty,
   not arbitrary point constants. Validate reconstruction on firms with observed
   states by masking them and comparing reconstructed distributions to truth.
3. If incomplete, use multiple stochastic imputations/posterior draws trained
   only on earlier development issuers inside each fold. Freeze the generator,
   feature availability, priors, seed, diagnostics and sensitivity bounds before
   evaluation; propagate imputation uncertainty through the intact engine. Never
   condition generated inputs on future realized revenue, cash flow or equity.
4. Fully synthetic firms/labels are simulation, recovery and stress tests only;
   they do not contribute to historical WAPE or empirical release claims.
   Imputed inputs paired with genuine historical labels are a separate empirical
   tier, not fully observed backtests. Report observed-only and imputed separately.
5. If reconstruction cannot be validated or states remain unidentified, stop
   the claimed production evaluation. Seek better-observed cohorts using an
   origin-known eligibility rule; register the entire universe, exclusions and
   missingness including failed/merged firms. No survivor-only cherry-picking.

Capture per-company execution evidence: frozen input/checkpoint hashes, active
component and state traces, mechanism-level ablations, state/revenue accounting,
finite constraints, and provenance for any structural zero. Verify the
historical and Anthropic traces against the same contract. Legacy aggregate
joint-engine experiments are archived as surrogate diagnostics only. Their
losses must not train, calibrate, select or validate the production model.

## 2. Training / 参数训练

Use chronological development folds with issuer-family separation, and a five-year
label embargo (training labels must already be published before the next fold's
forecast origin). Fit scaling, imputation, covariance shrinkage, factor selection,
and hyperparameters inside each fold. Use nested validation; never fit using
test labels. Record all experiments, including failures, with parameter bounds,
objective, random seeds, hashes and reproducible commands. Fit revenue, margin,
FCFF, survival/renewal, WACC and capital structure components on their appropriate
training labels. Optimize equity market-cap error separately; revenue-only tuning
does not qualify.

Before fitting, inspect the Jacobian of all observables with respect to scaled
parameters, its singular values, rank and near-null directions. Check exact
invariances and distinguish local rank from global identification. Do not claim
separate estimated parameters when only their product or sum is identifiable.
Constrain them with independent as-of measurements, estimate identifiable
composites, or carry the unidentified direction as uncertainty. Regularization
does not create information. Repeat rank and sensitivity checks across folds and
relevant operating regimes; do not use synthetic recovery as historical evidence.

Use a zero-safe primary loss:

```math
L=\frac{1}{n}\sum_i|\log(1+\widehat V_i)-\log(1+V_i)|+\lambda\|\theta\|_2^2
```

All values in USD B; nonnegative market caps; zero for a documented terminal
equity wipeout only. M&A/de-listing require separately documented outcomes and
coverage, not zero by default. Monetary predictions and labels use identical dates.
Compare flat market cap and constant P/S using only origin-known inputs.

## 3. Post-training / 独立评测

Freeze exact production code and fitted parameters before independent scoring.
Run the identical frozen production architecture with every applicable mechanism
active, using evidence-based company profiles under section 1A. An entrypoint
name alone is insufficient; independently review trace evidence. Evaluate five-year revenue,
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
