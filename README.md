# Anthropic Valuation — Joint-State Lifecycle DCF

**English** · [简体中文](README.zh-CN.md)

Snapshot 2026-11-19 · USD B · **Release gate: BLOCKED** ([§3.1](#31-release-gate)): research estimates, not a validated valuation.

## Results

| Mean | P5 | **P10 (bear)** | **P50 (base)** | **P90 (bull)** | P95 | $P(V<0)$ |
|---:|---:|---:|---:|---:|---:|---:|
| 501.67 | 20.55 | **72.13** | **401.43** | **1,043.01** | 1,345.69 | 3.3% |

1,024 joint draws (§1.5). Stress corners (all blocks at one end, not percentiles):

| | $R_1$ | $R_5$ | $R_{10}$ | EV | $V$ |
|---|---:|---:|---:|---:|---:|
| Bear | 50.67 | 24.88 | 21.68 | −356.80 | −254.99 |
| Base | 100.12 | 221.47 | 328.27 | 392.82 | 494.63 |
| Bull | 115.69 | 396.70 | 734.42 | 2,760.30 | 2,862.11 |

Reverse DCF, $V=1{,}200$ (IPO terms), one lever at a time:

| Lever | Base | Needed |
|---|---:|---:|
| $W$ | 8.86% | 5.67% |
| $g$ | 3% | 6.83% |
| $c^\ast$ | 45.5% | 10.8% |
| All toward bull, $z$ | 0 | 0.47 |
| Capture, demand, acquisition, volume | — | unreachable (max 495–519) |

## 1. Model

**Purpose:** Value equity by discounting explicit cash flows and risk-adjusted continuation cash flows, then adding net cash; averaging paths captures uncertain outcomes. $V$ = equity residual; $FCF_t$ = modeled free cash flow in forecast year $t$; $W$ = annual WACC; $R_{10}$ = year-10 revenue conditioning the tail; $\ell$ = simulation draw; $\widehat V$ = mean equity residual.


```math
V=\underbrace{\sum_{t=1}^{10}\frac{FCF_t}{(1+W)^t}}_{\S1.2}+\underbrace{\sum_{t>10}\frac{\mathbb E[FCF_t\mid R_{10}]}{(1+W)^t}}_{\S1.3}+\underbrace{Cash-Debt}_{\S1.4},\qquad \widehat V=\frac1{1024}\sum_{\ell}V^{(\ell)}\ (\S1.5)
```

### 1.1 Revenue

**Purpose:** Separate business invoices from individual subscriptions so market size and vendor capture constrain recognized revenue. $R_t$ is total revenue; $s_t$ scales enterprise invoices down when demand exceeds the ceiling; $\mathcal R$ converts potential invoice mass into captured Claude revenue.


```math
R_t=s_t\,\mathcal R(L_t+T_t+S_t)+B^{p}_t,\qquad \mathcal R(X)=\sum_{idhv}X_{idhv}r_v,\qquad s_t=\min\Big(1,\frac{C_t}{\mathcal R(L_t+T_t+S_t)}\Big)
```

| Symbol | Meaning | Value |
|---|---|---|
| $L,T,S$ | live-API, pilot, employer-seat invoice tensors | §1.1.2 |
| $r_v$ | Claude revenue share by vendor state | $(1,.6,0,0,0,0,0)$ |
| $C_t$ | enterprise demand ceiling | §1.1.5 |
| $B^p_t$ | personal subscriptions | §1.1.6 |

#### 1.1.1 Start

**Purpose:** Reconcile the disclosed run rate into mutually exclusive starting revenue buckets. $R_0$ is the annualized starting revenue; $\omega$ is consumption share; $A_0$ and $B_0$ are API and subscription pools; $B^p_0$ is the assumed individual portion, leaving the remainder for employer seats.


```math
R_0=81,\qquad \omega=\tfrac{26.300}{33.242}=79.1\%,\qquad A_0=\omega R_0=64.1,\qquad B_0=(1-\omega)R_0=16.9,\qquad B^p_0=0.5B_0
```

Sources: [S-1](https://www.sec.gov/Archives/edgar/data/2130357/000162828026074338/anthropicpbc-sx1ax3.htm), [run rate](https://www.sec.gov/Archives/edgar/data/2130357/000162828026074628/anthropicpbc-fwpjapanprospa.htm). October mix = nine-month mix (proxy).

#### 1.1.2 Customer-state tensor

**Purpose:** Track potential invoice dollars (not customer counts) across business maturity, tenure, financial health and supplier choice, because customers can grow, fail or switch. $X_t$ is the 504-cell state tensor; $\mathcal K$ migrates customer lifecycle/health; $\mathcal G_t$ changes spending; $M$ switches vendors; $A_t$ adds new invoice mass.


```math
X_t=\mathcal K_{Z_t}\big(\mathcal G_t(X_{t-1})\,M_{Z_t}\big)+A_t,\qquad X\in\mathbb R^{8\times3\times3\times7}_{(i,d,h,v)}
```

$i$ lifecycle (seed 0–4+, scale-up, SME, large) · $d$ dwell · $h$ health · $v$ vendor · $Z_t$ macro regime.

**1.1.2.1 Lifecycle kernel $\mathcal K$**

**Purpose:** Convert cumulative startup graduation into conditional transitions while accounting for closure and competing events. $F_k$ = cumulative graduation by age $k$; $U_k$ = mass still at risk; $g_k$ = conditional graduation; $b_k$ = competing non-graduation exit; $h_k$ = closure; effective hazard scales baseline closure by macro and health multipliers.


```math
g_k=\frac{F_k-F_{k-1}}{U_{k-1}},\quad U_k=U_{k-1}(1-g_k-b_k-h_k),\quad h^{\mathrm{eff}}_i=\min(0.95,\,h_i\,m^Z_{\mathrm{death}}m^H_{\mathrm{death}})
```

| | Value |
|---|---|
| $F_{1..4}$ (seed→A) | 10 / 22 / 31 / 36% |
| $h_i$ (early / scale-up / SME / large) | 15.03 / 8.06 / 7.27 / 0.132% (BLS) |
| $m^Z_{\mathrm{death}}$, $m^Z_{\mathrm{grow}}$ (winter/normal/boom) | 1.5/1/0.75 · 0.65/1/1.25 |
| $m^H_{\mathrm{death}}$, spend (distressed/funded/self-sustaining) | 1.6/1/0.55 · 0.75/1/1.10 |

**1.1.2.2 Health** $\;\pi_{h\mid y}\propto\pi_hP(y\mid h)$, $P(y{=}1\mid h)=(.15,.75,.25)$.

**Purpose:** Infer latent financial health from observed funding, since funding can sustain spending without profitability. $\pi_h$ = prior state probability; $y$ = funding indicator; $P(y\mid h)$ = assumed observation likelihood; $\pi_{h\mid y}$ = updated probability.


**1.1.2.3 Macro** $\;P_Z=\begin{pmatrix}.60&.35&.05\\.18&.67&.15\\.08&.42&.50\end{pmatrix}$ (winter, normal, boom).

**Purpose:** A regime Markov chain allows correlated changes in funding, acquisition and survival; $P_Z$ is the annual transition matrix between winter, normal and boom.


**1.1.2.4 Vendors**

**Purpose:** Separate commercial churn from business failure so the same loss is not counted twice. $s_g$ = total retention for group $g$; $h_g$ = business closure hazard; $c$ = conditional commercial churn; $m_c^Z$ = macro churn multiplier; $\delta_w$ = destination mix; $\sigma$ = single/multi-vendor switching probability; $M_{i\to w}$ = transition probability.


```math
c=\Big(1-\frac{s_g}{1-h_g}\Big)m^Z_c,\qquad M_{i\to w}=\begin{cases}c\,\delta_w&\text{exit to }w\\(1-c)\sigma&\text{single}\leftrightarrow\text{multi}\\(1-c)(1-\sigma)&\text{stay}\end{cases}
```

$s_g$ = 69.0/78.7/82.6/92.3% · $\delta$ = .35/.25/.15/.10/.15 (OpenAI, Google, self, other, none) · $\sigma$ = .12 / .04 · $m^Z_c$ = 1.3 / 0.85 · regain .06 / .035 per year.

#### 1.1.3 Growth

**Purpose:** Model price erosion, usage expansion and pilot conversion separately so technological progress need not translate into proportional revenue. $d_t$ fades early growth; $p,q$ are price and volume multipliers; $\mu_t$ combines them; $\alpha_t$ allocates new API mass to pilots; $\phi$ is conversion probability; $\rho$ is rollout spending multiplier (not years); $f,F_t$ adjust funding-driven spending; $H$ is health spending multiplier here; $b$ is subscription growth; $A_t^s$ is new seat invoice mass.


```math
d_t=\max\Big(0,1-\tfrac{t-1}{7}\Big),\quad \mu_t=[1-(1-p)d_t][1+(q-1)d_t],\quad \alpha_t=.1+.5d_t
```

```math
L_t=\mathcal K\big([(L_{t-1}+\phi\rho T_{t-1})F_t\mu_tH]M\big)+(1-\alpha_t)A_t,\quad T_t=\alpha_tA_t,\quad S_t=\mathcal K\big([S_{t-1}F_t(1+bd_t)H]M\big)+A^{s}_t
```

Base: $p$=.78, $q$=1.65, $\phi$=.35, $\rho$=3, $b$=12%, $F_t=1+(f-1)d_t$.

#### 1.1.4 New customers

**Purpose:** Add new enterprise budgets and replace churn while limiting startup-origin spending to available financing. $J_t$ is new invoice mass; $x_Z$ scales acquisition by macro regime; $n$ is early acquisition rate; $\eta$ is mature replacement factor; $s_i$ is customer retention; $J_t^{\mathrm{birth}}$ is the startup-funded portion subject to the funding cap.


```math
J_t=x_Z\big[n\,d_t\,\mathcal R(X_{t-1})+\eta(1-d_t)\textstyle\sum X r_v(1-s_i)\big],\qquad J^{\mathrm{birth}}_t=\min(0.2J_t,\,0.418)
```

$n$=.20, $\eta$=1; $0.418=5049\times2\times.75\times.25\times5\%\times\overline{\text{seed round}}$.

#### 1.1.5 Enterprise ceiling

**Purpose:** Cap enterprise revenue at the industry AI budget times Claude's attainable share, preventing unlimited compounding. $D_{i,t}$ is sector demand; $w_i$ allocates starting demand; $g_i$ is sector growth; $m$ scales growth by scenario; $c_t,c_0,c_{10}$ are current, initial and long-run capture shares (not compute cost ratios).


```math
C_t=c_t\sum_iD_{i,t},\quad D_{i,t}=D_{i,t-1}\big[1.03+(mg_i-.03)\max(0,1-\tfrac{(t-2)^+}{8})\big],\quad c_t=c_0+(c_{10}-c_0)\min(\tfrac t{10},1)
```

$D_{i,0}=176.8\,w_i$ ([Menlo](https://menlovc.com/perspective/2026-the-state-of-enterprise-ai/) × IDC weights) · $g_i$ IDC 2024–28 CAGR · $m$=.7/1/1.5 · $c_0=(81-B_0/2)/176.8=41\%$ · $c_{10}$=15%/41%/50%.

#### 1.1.6 Personal subscriptions

**Purpose:** Bound paid consumer demand by a subscription benchmark and remove overlapping employer-paid demand. $B_t^{\mathrm{raw}}$ is personal revenue before overlap; $e_t,e_0$ are employer coverage now and initially; $\kappa$ is substitution intensity; $N_N$ is Netflix paid memberships (not persons); $k$ is relative attainable membership share; $F_C$ is monthly realized fee; $R_C$ is the consumer ceiling.


```math
B^p_t=\min\Big(B^{\mathrm{raw}}_t\tfrac{1-\kappa e_t}{1-\kappa e_0},\;R_C+(B^p_0-R_C)^+(1-\tfrac t5)^+\Big),\qquad R_C=12N_NkF_C
```

$\kappa$=.8/.5/.2 · $e_t$: .4→.8/.7/.6 · $N_N$=0.325B ([Netflix](https://www.sec.gov/Archives/edgar/data/1065280/000106528025000044/nflx-20241231.htm)) · $k$=5/15/30% · $F_C$=\$13.53/mo.

### 1.2 Free cash flow, $t\le10$

**Purpose:** Convert revenue to a simplified cash-flow proxy while retaining minimum compute obligations and cost convergence. $Y_t$ is pre-tax cash-flow proxy; $K_t$ is committed capacity floor; $c_t,o_t,x_t$ are compute, operating and capex ratios; $\theta_0,\theta^\ast$ are starting and steady ratios; $H$ is convergence half-life; $Y_t^+$ is positive part, preventing assumed loss tax credits. Tax on this proxy is a simplification, not full accrual FCFF.


```math
Y_t=R_t-\max(K_t,\,c_tR_t)-(o_t+x_t)R_t,\qquad FCF_t=Y_t-0.25\,Y_t^+,\qquad \theta_t=\theta^\ast+(\theta_0-\theta^\ast)2^{-t/H}
```

| Symbol | Value |
|---|---|
| $\theta=(c,o,x)$ | compute, other opex, capex ratios |
| $\theta_0$ | (56.6%, 47.2%, 2.8%), reported 9M 2026 |
| $\theta^\ast$ | base (45.5%, 24.0%, 6%), from comparables (§3.6) |
| $H$ | 3 y (§3.2) |
| $K_t$ | commitment floor: $K_1$=70.7, $K_{2..4}$=126.97, $K_{5..19}$=29.95, $K_{20+}$=0 |

### 1.3 Continuation, $t>10$

**Purpose:** Replace deterministic perpetual growth with a lifecycle chain that permits decline, renewal and distress exit. $a_t$ = probability-weighted revenue by issuer state; $P$ = state transition matrix; $e,\delta,u$ = distress exit, decline and renewal probabilities; $\varsigma$ = distress share of delistings; $g$ = long-run survivor growth; $k$ = growth normalization; $\mu$ = state margins; $m$ = mature net cash-flow margin; $S_t$ = survival probability; $A$ = revenue-weighted transition matrix; $B$ = discounted matrix; $I$ = identity.


```math
a_{10}=(R_{10},0,0,0),\quad a_t=a_{t-1}P\,\mathrm{diag}\big(k(1+g),.85k,1.08k(1+g),0\big),\quad \mathbb E[FCF_t]=a_t\mu-S_t\Big(K_t-\tfrac{c\,\mathbf 1^\top a_t}{S_t}\Big)^+
```

```math
P=\begin{pmatrix}1-e-\delta-u&\delta&u&e\\.10&.90-e-u&u&e\\.40&\delta&.60-e-\delta&e\\0&0&0&1\end{pmatrix},\quad \mu=\big(m,.2m,\min(.6,\tfrac43m),0\big),\quad m=.75(1-c^\ast-o^\ast-x^\ast)
```

States: mature, declining, renewed, exited. $k$ sets survivor long-run growth to $g$. Tail beyond 30 years: $a_{30}B(I-B)^{-1}\mu/(1+W)^{30}$, $B=A/(1+W)$.

| | Bear | Base | Bull |
|---|---:|---:|---:|
| $e=[1-.92^{1/5}]\varsigma$ (distress only) | .00827 | .00132 | .0009 |
| $\delta$ / $u$ | .30 / .03 | .20 / .08 | .10 / .15 |
| $m$ | 8.9% | 18.4% | 27.9% |

$\varsigma$: 8% ([Daepp et al.](https://doi.org/10.1098/rsif.2015.0120)), 50% bear (dot-com). 8%/5y delisting: [BCG](https://www.bcg.com/publications/2026/why-do-companies-fail-us-failure-rates).

### 1.4 Equity bridge

**Purpose:** Convert operating enterprise value to equity residual by adding cash and subtracting debt claims; cash and debt are balance-sheet amounts, while dilution must be assessed separately.


```math
Cash-Debt=212.684-110.873\quad(\text{as-adjusted }232.351-109.742\text{ adds }20.80)
```

Dilution unresolved.

### 1.5 Uncertainty

**Purpose:** Draw correlated revenue and margin shocks with separate financing and lifecycle risk, rather than combining every optimistic assumption at once. $n_r,n_m,n_w$ are standard-normal drivers; $\rho$ here is correlation (not rollout); $z_r$ is revenue-block shock; $\bar z_\pm$ maps its tails to peer dispersion; $\Phi$ is normal CDF; $\hat F^{-1}$ maps percentile to empirical margin/WACC; $z_\ell$ is triangular lifecycle shock.


```math
(n_r,n_m)\sim\mathcal N\Big(0,\begin{pmatrix}1&\rho\\\rho&1\end{pmatrix}\Big),\quad n_w\sim\mathcal N(0,1),\quad z_\ell\sim\mathrm{Tri}(-1,0,1),\quad Z_t\sim P_Z
```

```math
z_r=\frac{n_r}{1.2816}\bar z_{\pm},\qquad m^\ast=\hat F_m^{-1}(\Phi(n_m)),\qquad W=\hat F_W^{-1}(\Phi(n_w))
```

| Symbol | Value |
|---|---|
| $\bar z_{\pm}$ | −0.312 / +0.630: sets $R_5/R_1$ at base × (1.28, 2.38)/1.80, the q10/q90 over q50 of ≥\$50B comparables' 4-year revenue multiples |
| $\hat F^{-1}_m,\hat F^{-1}_W$ | empirical comparable quantiles (§3.6) |
| $\rho$ | .334 (Spearman .32, revenue growth vs margin change) |
| $z_\ell$ | lifecycle block: $g$, $e$, $\delta$, $u$ (hand-set) |

Macro only: mean 402.88, P5–P95 242.27–519.67. Single common factor: P90 1,177.01.

## 2. Parameters

| | Bear | Base | Bull | Source |
|---|---:|---:|---:|---|
| Early / scale-up / SME / large | 30/30/25/15% | 15/25/30/30% | 5/15/30/50% | hand-set |
| Pilot share; success / rollout | 25%; .20/2 | 30%; .35/3 | 20%; .50/4 | hand-set |
| Volume $q$ / price $p$ | 1.45/.65 | 1.65/.78 | 1.85/.88 | hand-set |
| Acquisition $n$ / replacement $\eta$ | .10/.50 | .20/1 | .30/1.25 | hand-set |
| Subscription growth $b$ | 3% | 12% | 22% | hand-set |
| $c^\ast$ / $o^\ast$ / $x^\ast$ | .589/.233/.06 | .455/.240/.06 | .345/.233/.05 | §3.6 ($x^\ast$ hand-set) |
| $c_{10}$ | 15% | 41% | 50% | hand-set |
| $g$ | 2.5% | 3% | 3.5% | hand-set |
| $W$ | 9.38% | 8.86% | 7.68% | §3.6 |

## 3. Evidence

All evidence below is development or diagnostic unless marked scored-once.

### 3.0 Data

| Set | Check | Result |
|---|---|---|
| SEC figures in §3.2–3.4 | XBRL vintage vs filed document | 205/205 match ([record](data/sec_reconciliation.csv)) |
| Acquisitions | two independent sources | all except NetSuite equity ([events](data/stage4_exit_events.csv)) |
| Legacy data | filed document; second site for market caps | 295/295 SEC match; PayPal cash fixed (13.002→13.083); 8 dead links replaced ([record](data/legacy_reconciliation.csv)) |
| Pending | — | IDC sector split, JPM/ITU, Cisco/CMGI/VeriSign 1998–99 |

### 3.1 Release gate

**Purpose:** Require reproducible independent five-year equity performance before calling the model validated. $N_{\rm fam}$ and $N_{\rm cycle}$ count independent issuer families and cycles; WAPE measures aggregate absolute error; bias measures signed aggregate error; flat and constant P/S are naive benchmarks.


```math
\text{release}\iff N_{\text{fam}}\ge10\ \wedge\ N_{\text{cycle}}\ge2\ \wedge\ \mathrm{WAPE}_V\le30\%\ \wedge\ |\mathrm{bias}_V|\le15\%\ \wedge\ \mathrm{WAPE}_V<\min(\text{flat},\ \text{const }P/S)
```

Current blockers (`python -m evaluation.validation_gate --audit`):

| # | Blocker | State |
|---|---|---|
| 1 | Untouched final test | cloud2018 roster rule frozen ([rule](evaluation/final2018/roster_rule.md)); roster not drawn |
| 2 | Full-model equity-loss training | not started |
| 3 | Validated company profiles (12 inputs) | 0 of 17 |
| 4 | Production-model contract and trace | not started |
| 5 | Frozen manifest, independent reviewer | reviewer unassigned |

Acquired issuers score on equity paid at close at horizon $\max(1,\mathrm{round}(\tau))$ ([policy](evaluation/acquisition_endpoint_policy.md), approved).

### 3.2 Margin path

**Purpose:** Test how cash-flow margins evolve using historical issuers; $m$ is CFO net of capex and capitalized software divided by revenue, a cash-flow proxy rather than FCFF. $H$ is the convergence half-life.


```math
m=\frac{CFO-\text{capex}-\text{cap. software}}{\text{revenue}}
```

Stage-4, scored once ([prereg](evaluation/stage4_margin_preregistration.md), [score](evaluation/stage4_margin_score.json)), 11 issuers, MAE pp:

| Model | Dev LOO | Stage-4 | 2015 | 2020 |
|---|---:|---:|---:|---:|
| Hold | 9.64 | 23.44 | 18.60 | 25.26 |
| Fade to 15% | 11.12 | 15.07 | 13.39 | 15.69 |
| Pooled mean | 9.28 | 8.63 | 11.45 | 7.57 |
| Converge, $H$=3 | 8.56 | **6.77** | 10.10 | 5.52 |
| Leverage (prereg pick) | **4.94** | 8.87 | 5.99 | 9.94 |

Pick not promoted (lost to pooled mean). 18-obs SBC-adjusted: median 11.1%, P90 24.4%; $H$=3 to 18.1% LOO 7.26 vs hold 16.56.

### 3.3 Growth and exits

**Purpose:** Test growth decay and distinguish acquisitions from distress exits. $g_0,g_t,g_\infty$ are initial, current and steady log growth; $H_g$ is growth half-life; $h$ is the forecast horizon; $R_h/R_0$ is cumulative revenue growth.


```math
g_t=g_\infty+(g_0-g_\infty)2^{-t/H_g},\qquad \ln\tfrac{R_h}{R_0}=\textstyle\sum_{t\le h}g_t
```

| LOO MAE, log revenue (18 obs) | Flat | Hold $g_0$ | Engine fade | Fit $H_g$=4, $g_\infty$=6.5% |
|---|---:|---:|---:|---:|
| | 1.436 | 0.660 | 0.242 | 0.221 |

Anthropic $g_0\approx2.57$ vs panel max 0.63: out of support.

| 5-year roster | n | Acquired | Bankrupt |
|---|---:|---:|---:|
| Cloud 2015 | 10 | 5 | 0 |
| Cloud 2020 | 14 | 1 | 0 |
| Dot-com 1999 | 18 | 2 | 2 |

Acquisitions paid 1.0–2.2× prior cap ⇒ $e$ counts distress only.

### 3.4 Equity backtest, cloud 2020 (exposed, diagnostic)

**Purpose:** Diagnose whether forecasts reproduce observed market capitalizations rather than only revenues; Spearman measures rank agreement, and P/FCF is price divided by cash flow.


| | Model | Flat cap | Const $P/S$ |
|---|---:|---:|---:|
| $V$ WAPE / bias | 71.17% / −49.37% | 58.82% / +17.73% | 124.89% / +124.89% |
| $V$ Spearman | −0.3 | −0.6 | −0.6 |
| $R$ / FCF WAPE | 16.25% / 37.91% | — | — |

Fundamentals right, multiples not (2025 P/FCF 10–104×).

### 3.5 Other experiments (none promoted)

| Experiment | Result |
|---|---|
| 1999 FY2000 nowcast | MAPE 21.54% (flat 50.23%) |
| 5-year saturation, leave-issuer-out | WAPE 41.08% (flat 61.19%) |
| External 1999 cohort | WAPE 60.21% (flat 69.97%) |
| Joint engine, aggregate restriction | $V$ WAPE 86.19% |
| Equity-loss training transfer | 88.48 / 61.40 / 65.63% (flat 58.82%) |

Sensitivity, base 494.63: no health 317.36 · no duration 499.11 · no vendors 404.64 · all off 259.22 · winter/boom 145.51/524.66 · cost jump 583.92 · $H$=6.8: 417.5.

### 3.6 Comparable calibration ([prereg](evaluation/margin_scale_preregistration.md))

**Purpose:** Estimate sustainable cost endpoints and discount rates from comparable businesses, and compare forecasting methods using family-held-out data. Hold = unchanged margin; mean = pooled average; linear/convergence = mean reversion; ridge = regularized regression; GBM = boosted trees; GP = Gaussian process; MLP = neural network. $m_t$ is observed margin; $m^\ast_i$ is peer three-year average operating margin; $OI_{it}$ is operating income; $s$ is compute-cost allocation proxy; $T$ is last observed year. CAPM: $\beta_L,\beta_u$ are levered/unlevered beta; $D,E$ are debt/equity capital; $t$ here is tax rate; $r_f$ risk-free rate; ERP equity risk premium; 1% debt spread proxies credit cost.


**Five-year margin**, 368 issuer-years, 39 families, leave-one-family-out ([panel](data/margin_scale_panel.csv), survivor-biased):

| Hold | Mean | **Linear** | Convergence | Ridge | GBM | GP | MLP |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 11.14 | 15.35 | **9.24** | 9.56 | 10.03 | 10.48 | 12.39 | 11.38 |

MAE pp. No ML beats linear ⇒ none promoted. Linear: $m_{t+5}=.60\,m_t+.108$ ⇒ long run 27.1%, half-life 6.8 y.

**Steady margin**

```math
m^\ast_i=\tfrac13\textstyle\sum_{t=T-2}^{T}\mathrm{OI}_{it}/R_{it},\quad i\in\{\text{platforms},\ R\ge20\},\qquad (c^\ast,o^\ast)=(1-m^\ast)(s,\,1-s)
```

$m^\ast$: MSFT 45.7, MS Intelligent Cloud 42.2, Meta 39.4, Adobe 34.1, AWS 33.2, Alphabet 30.5, Oracle 30.1, Netflix 25.6, Intuit 25.3, Salesforce 17.8, Google Cloud 14.3% ⇒ P10/P50/P90 = 17.8/30.5/42.2%. $s$ = MS Intelligent Cloud COGS/(COGS+opex) FY24–26 = 59.6/65.1/71.6%.

**Discount rate**

```math
\beta_u=\frac{\beta_L}{1+(1-t)D/E},\qquad W=\tfrac{E}{D+E}\big[r_f+\beta_u(1+(1-t)\tfrac DE)\,\mathrm{ERP}\big]+\tfrac{D}{D+E}(r_f+1\%)(1-t)
```

$r_f$=5.0%, ERP=4.14% (Damodaran, Sep 2026), 13 peer betas ([inputs](data/wacc_inputs.csv)), $D/E$=0.09 ⇒ $W$ = 9.38/8.86/7.68% at $\beta_u$ P75/P50/P25. ERP 3.56/6.05% ⇒ 8.31/10.65%.

| Base $V$ | |
|---|---:|
| Old hand-set ($c^\ast$ .48, $o^\ast$ .25, $W$ 12%) | 249.22 |
| + estimated costs | 292.5 |
| + estimated $W$ only | 421.1 |
| Both | 494.63 |
| Revenue recentred to comparable median $R_5/R_1$=1.80 (not adopted) | 293.1 |

Bull fix: blocks at their own P90 give 904.6 (revenue), 755.4 (margin), 643.7 ($W$), 608.3 (lifecycle); all at once 2,905; independent block draws give P90 1,043.01.

## 4. Reproduce

```bash
pip install numpy scipy scikit-learn
python -m unittest discover -s evaluation -p 'test_*.py'   # 136 tests
python -m evaluation.validation_gate --audit
python -m models.joint_customer_states
python -m evaluation.reverse_dcf --equity 1200
python -m evaluation.margin_scale
python -m evaluation.margin_path --verify
python -m evaluation.cloud_equity
```

[data/README.md](data/README.md) · [MODEL_VALIDATION_PROTOCOL.md](MODEL_VALIDATION_PROTOCOL.md) · [AGENTS.md](AGENTS.md)
