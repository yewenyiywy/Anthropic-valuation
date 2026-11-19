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
