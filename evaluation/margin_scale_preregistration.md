# Margin-at-scale study: preregistration (development/diagnostic)

Registered 2026-11-19 before any model in this study was fitted. All labels
are public historical filings already visible to the author, so every result
here is **development/diagnostic**, never a blind test.

## Purpose
Replace the hand-set scenario cost ratios (`cost_ratio`, `other_ratio`) and
WACC in `models/valuation.py` with distributions estimated from comparables.

## Data
- `data/margin_scale_panel.csv`: annual revenue, operating income and cost of
  revenue from SEC XBRL company facts (latest filed value per fiscal year end),
  40 listed software/cloud/internet/semiconductor issuers chosen by the author
  (survivor-biased: all are listed in 2026), plus three cloud segments taken
  from filed 10-K segment tables: AWS (Amazon), Google Cloud (Alphabet, latest
  recast values), Microsoft Intelligent Cloud (as reported; FY24-26 recast).
- `data/wacc_inputs.csv`, `data/wacc_market.csv`: 5-year betas, D/E, risk-free
  rate and Damodaran implied ERP as of November 2026.

## Target A: five-year-ahead operating margin
- Example: issuer-year t with revenue >= $0.05B and an observation at t+5.
- Label: operating income / revenue at t+5 (percentage points).
- Features (all known at t): margin_t, log revenue_t, revenue growth t-1->t
  (clipped to [-0.5, 3]), margin change t-1->t, gross margin_t (missing allowed).
- Split: leave-one-issuer-out (Amazon and AWS, Alphabet and Google Cloud,
  Microsoft and Intelligent Cloud are grouped as one family each).
- Loss/metric: mean absolute error in pp; also bias.
- Baselines: hold (margin_t), pooled training mean, linear partial adjustment
  (OLS of label on margin_t).
- Candidates: ridge on all features, scale-convergence model
  (label = margin_t + lambda*(a + b*log revenue_t - margin_t)), histogram
  gradient boosting (max_depth 3, 200 iterations, lr 0.05), Gaussian process
  (RBF + white noise on standardized features), small MLP (16-16, adam,
  early stopping) as the deep-learning check.
- Selection rule: lowest LOO-issuer MAE; a candidate is promoted only if it
  beats the best baseline by at least 1.0 pp. Hyperparameters above are fixed;
  no tuning on these folds.
- Seed 0.

## Target B: steady-state operating margin m*
- Eligible issuers: entities in the panel whose latest fiscal-year revenue is
  >= $20B and whose business is software, cloud or internet platform
  (excludes IT services ACN/CTSH, retail-dominated AMZN consolidated,
  marketplaces UBER/ABNB/BKNG/EBAY, payments PYPL, hardware NVDA/ANET).
- m*_i = mean operating margin of issuer i over its last three fiscal years.
- Scenario mapping: bear/base/bull = 10th/50th/90th percentile of m*_i;
  Monte Carlo draws m* from the empirical distribution with uniform jitter
  between neighbours.
- Split of total costs 1-m* into compute vs other: compute share of operating
  costs from Microsoft Intelligent Cloud FY2024-FY2026 (cost of revenue /
  (cost of revenue + operating expenses)); bear/base/bull = max/mean/min.

## Target C: discount rate
- CAPM: r_e = r_f + beta_L * ERP, beta_L relevered from the median unlevered
  peer beta (Hamada, tax 25%) at Anthropic's D/E (adjusted convertibles /
  IPO-terms equity). WACC = equity/debt weighted with after-tax cost of debt
  r_f + 1%. bear/base/bull = peer beta 75th/50th/25th percentile.
- ERP sensitivity uses Damodaran's low/high implied variants.

## Not changed by this study (still hand-set, labeled as such)
Customer-state parameters (startup, trial, conversion, rollout, volume, price,
share, new, subscription growth, ceilings, cannibalisation), capex ratio and
terminal growth.

## Addendum 2026-11-19 (registered before computing the quantities below)

Problem: the bull/bear scenarios move every parameter to its extreme at once
(one common factor), so "bull" combines top-decile revenue, top-decile margin,
bottom-quartile WACC and the most favourable lifecycle values. That is a
stress corner, not a 90th-percentile outcome.

Change to the production Monte Carlo (`simulate`):
1. Four parameter blocks with separate factors: revenue (customer-state
   scenario parameters and blended inputs), cost (cost_ratio, other_ratio,
   capex), discount (wacc), lifecycle (terminal_growth, exit, decline, renew).
2. Revenue dispersion from comparables: issuer-years with revenue >= $50B in
   `data/margin_scale_panel.csv`; 4-year forward revenue multiple quantiles
   q10/q50/q90. The revenue factor at the 10th/90th percentile is the value
   at which the model's year-5/year-1 revenue multiple equals
   base x q10/q50 and base x q90/q50 (bisection).
3. Cost block: z = +-1 at the estimated P90/P10 (Target B). Discount block:
   z = +-1 at the beta quartiles (Target C). Lifecycle block: unchanged
   hand-set triangular factor.
4. Dependence: Gaussian copula; revenue-cost correlation = Spearman rank
   correlation between 4-year revenue multiple and the margin change over the
   same 4 years in the panel; other pairs independent.
5. Reported bear/base/bull become the P10/P50/P90 of the simulated equity;
   the all-extremes corner is kept as a labelled stress test.
