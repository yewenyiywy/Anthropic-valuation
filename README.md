# Anthropic Valuation — Joint-State Lifecycle DCF

**English** · [简体中文](README.zh-CN.md)

Snapshot 2026-11-19. USD billions unless noted. **Research model: the [release gate](MODEL_VALIDATION_PROTOCOL.md) is BLOCKED, so no number here is a validated valuation.**

## Results

**Conditional equity residual**: 1,024 joint draws of macro paths and scenario parameters (§1.5).

| Mean | Median | P5 | P95 | P(equity < 0) |
|---:|---:|---:|---:|---:|
| 252.85 | 184.49 | −103.42 | 904.48 | 25.6% |

**Structural scenarios**, normal macro regime:

| Scenario | Revenue y1 | y5 | y10 | EV | Equity |
|---|---:|---:|---:|---:|---:|
| Bear | 50.67 | 24.88 | 21.68 | −306.95 | −205.14 |
| Base | 100.12 | 221.47 | 328.27 | 147.41 | 249.22 |
| Bull | 115.69 | 396.70 | 734.42 | 1718.48 | 1820.30 |

**Reverse DCF** (`python -m evaluation.reverse_dcf --equity 1200`): what one lever must become for equity to equal about $1.2T, the IPO-terms market cap. Diagnostic only.

| Lever, others at base | Base | Needed |
|---|---:|---:|
| All parameters toward bull (factor z) | 0 | 0.75 |
| WACC | 12% | 5.3% |
| Survivor terminal growth g | 3% | 10.7% |
| Capture, demand growth, acquisition or volume alone | — | not reachable (max ≈ 249–263) |

At z = 0.75 the steady-state after-tax margin is 26.4%, the 89th percentile of 18 cloud-software SBC-adjusted outcomes (§3.2); the base 15.75% is the 67th.

## 1. Valuation model

```math
V^{(\ell)}=\sum_{t=1}^{10}\frac{FCF^{(\ell)}_t}{(1+W)^t}+\sum_{t=11}^{\infty}\frac{\mathbb E[FCF_t\mid R^{(\ell)}_{10}]}{(1+W)^t}+Cash-Debt,\qquad \widehat V=\frac1L\sum_{\ell=1}^{L}V^{(\ell)}
```

| Symbol | Meaning | Section |
|---|---|---|
| $V^{(\ell)}$ | equity residual on draw $\ell$ (macro path and parameters) | §1.5 |
| $FCF_t$ | free cash flow, forecast years 1–10 | §1.2 |
| $R_t$ | revenue | §1.1 |
| $\mathbb E[FCF_t\mid R_{10}]$ | expected cash flow of the lifecycle continuation | §1.3 |
| $W$ | discount rate (WACC) | §2 |
| $Cash-Debt$ | pro forma bridge | §1.4 |
| $L$ | number of draws, 1,024 | |

### 1.1 Revenue

```math
R_t=s_t\,\mathcal R(L_t+T_t+S_t)+B^{\mathrm{pers}}_t,\qquad s_t=\min\Big(1,\frac{C_t}{\mathcal R(L_t+T_t+S_t)}\Big),\qquad \mathcal R(X)=\sum_{i,d,h,v}X_{idhv}\,r_v
```

| Symbol | Meaning |
|---|---|
| $L_t,T_t,S_t$ | live-API, pilot and employer-seat invoice tensors (§1.1.2) |
| $r_v$ | revenue share Claude earns in vendor state $v$: $r=(1,0.6,0,0,0,0,0)$ |
| $C_t$ | enterprise demand ceiling (§1.1.5) |
| $s_t$ | ceiling scale, applied to all three tensors |
| $B^{\mathrm{pers}}_t$ | personal subscriptions (§1.1.6) |

#### 1.1.1 Starting point

```math
\omega=\frac{C_{9m}}{R_{9m}}=\frac{26.300}{33.242}=79.12\%,\qquad A_0=R_0\,\omega=64.085,\qquad B_0=R_0(1-\omega)=16.915
```

$R_0$ = 81, the October run rate. $A_0$ is consumption (API) revenue and $B_0$ subscription revenue; 50% of $B_0$ is assumed personal. Applying the nine-month mix to October is a proxy. Sources: [S-1](https://www.sec.gov/Archives/edgar/data/2130357/000162828026074338/anthropicpbc-sx1ax3.htm), [run-rate disclosure](https://www.sec.gov/Archives/edgar/data/2130357/000162828026074628/anthropicpbc-fwpjapanprospa.htm).

#### 1.1.2 Customer-state tensor

```math
X_t=\mathcal K_{Z_t}\big(\mathcal G_t(X_{t-1})\,M_{Z_t}\big)+A_t,\qquad X\in\mathbb R^{8\times3\times3\times7}
```

| Symbol | Meaning |
|---|---|
| $X_{idhv}$ | invoice mass by lifecycle $i$ (seed 0–4+, scale-up, SME, large), dwell $d$ (0/1/2+), health $h$, vendor $v$ |
| $Z_t$ | macro regime: winter, normal or boom (§1.1.2.3) |
| $M_{Z}$ | vendor transition matrix (§1.1.2.4) |
| $\mathcal K_Z$ | lifecycle and health kernel, sub-stochastic; the residual is closure (§1.1.2.1) |
| $\mathcal G_t$ | growth operator (§1.1.3) |
| $A_t$ | new invoices (§1.1.4) |

##### 1.1.2.1 Lifecycle kernel

```math
g_k=\frac{F_k-F_{k-1}}{U_{k-1}},\qquad U_k=U_{k-1}(1-g_k-b_k-h_k),\qquad h^{\mathrm{eff}}_{i}=\min\big(0.95,\;h_i\,m^{Z}_{\mathrm{death}}\,m^{H}_{\mathrm{death}}\big)
```

| Symbol | Value / meaning |
|---|---|
| $F_k$ | cumulative seed→Series A incidence after $k$ years: 10/22/31/36% (base) |
| $g_k,b_k,h_k$ | graduation, bootstrap and closure hazards of the seed tenure states |
| $h_i$ | annual closure by group: early 15.03%, scale-up 8.06%, SME 7.27%, large 0.132% (BLS establishments; large = distress proxy) |
| $m^{Z}_{\mathrm{death}}$ | 1.5 / 1 / 0.75 for winter / normal / boom |
| $m^{H}_{\mathrm{death}}$ | 1.6 / 1 / 0.55 for distressed / funded / self-sustaining |
| Promotion | × $m^Z_{\mathrm{grow}}$ = 0.65 / 1 / 1.25; dwell multiplier 0.55 / 1 / 1.20; spending jump 1.35 up, 0.75 down |

##### 1.1.2.2 Latent health

```math
\pi_{0,h\mid y}=\frac{\pi_{0,h}P(y\mid h)}{\sum_k\pi_{0,k}P(y\mid k)},\qquad P(y=1\mid h)=(0.15,\,0.75,\,0.25)
```

$y$ = recent funding observed. Normal-regime rows are (.67, .23, .10), (.18, .62, .20) and (.04, .10, .86); winter tilts toward distress and boom away from it. Health also scales spending by 0.75 / 1 / 1.10.

##### 1.1.2.3 Macro regime

```math
P_Z=\begin{pmatrix}0.60&0.35&0.05\\0.18&0.67&0.15\\0.08&0.42&0.50\end{pmatrix}\quad(\text{winter, normal, boom})
```

##### 1.1.2.4 Vendor transitions

```math
M_{i\to w}=\begin{cases}c\,\delta_w & w\in\{\mathrm{OpenAI,Google,self,other,none}\}\\(1-c)\,\sigma & \text{single}\leftrightarrow\text{multi}\\(1-c)(1-\sigma)&\text{stay}\end{cases},\qquad c=\Big(1-\frac{s_g}{1-h_g}\Big)m^Z_c
```

| Symbol | Value / meaning |
|---|---|
| $s_g$ | annual revenue retention by group: 69.0 / 78.7 / 82.6 / 92.3% |
| $\delta$ | exit destination shares: .35 / .25 / .15 / .10 / .15 |
| $\sigma$ | switch probability: 0.12 single→multi, 0.04 multi→single |
| $m^Z_c$ | 1.3 winter, 0.85 boom |
| Regain | 0.06/yr from rivals, 0.035/yr from none, × $m^Z_{\mathrm{grow}}$ |

#### 1.1.3 Growth operator

```math
d_t=\max\Big(0,1-\frac{t-1}{7}\Big),\qquad \mu_t=[1-(1-p)d_t]\,[1+(q-1)d_t],\qquad \alpha_t=0.1+0.5\,d_t
```

```math
L_t=\mathcal K\big([(L_{t-1}+\phi\,\rho\,T_{t-1})\,F_t\,\mu_t\,H]\,M\big)+(1-\alpha_t)A_t,\qquad T_t=\alpha_tA_t,\qquad S_t=\mathcal K\big([S_{t-1}F_t(1+b\,d_t)H]\,M\big)+A^{\mathrm{seat}}_t
```

| Symbol | Meaning (base) |
|---|---|
| $d_t$ | growth fade (§3.3 tests this shape) |
| $p,q$ | initial price and volume multipliers: 0.78, 1.65 |
| $\phi,\rho$ | pilot success and rollout: 0.35, 3 |
| $F_t$ | funding multiplier for early and scale-up firms: $1+(f-1)d_t$ |
| $H$ | health spend multiplier |
| $b$ | subscription growth: 12% |

#### 1.1.4 New customers

```math
J_t=x_{Z_t}\big[n\,d_t\,\mathcal R(X_{t-1})+\eta(1-d_t)\,\mathcal L(X_{t-1})\big],\qquad \mathcal L(X)=\sum X_{idhv}r_v(1-s_i),\qquad J^{\mathrm{birth}}_t=\min(0.2J_t,\;\mathrm{Budget}_t)
```

$n$ = 0.20 is the acquisition rate, $\eta$ = 1 the maturity replacement and $x_Z$ the macro sales multiplier. Budget = US seed deals 5,049 × global 2 × unique 0.75 × capture 0.25 × 5% of the average round, giving 0.418 per year.

#### 1.1.5 Enterprise ceiling

```math
C_t=c_t\sum_i D_{i,t},\qquad D_{i,t}=D_{i,t-1}\big[1+0.03+(m\,g_i-0.03)\max\Big(0,1-\frac{\max(0,t-2)}{8}\Big)\big],\qquad c_t=c_0+(c_{10}-c_0)\min(t/10,1)
```

| Symbol | Meaning |
|---|---|
| $D_{i,0}$ | Menlo 2026 deployment spend 176.8 × IDC sector weight $w_i$ |
| $g_i$ | IDC 2024–28 sector CAGR; $m$ = 0.7 / 1 / 1.5 |
| $c_0$ | $(81-B_0/2)/176.8$ = 41%, the observed starting capture |
| $c_{10}$ | 15% bear, $c_0$ base (held), 50% bull |

Sources: [IDC](https://info.idc.com/rs/081-ATC-910/images/DA-Market-Primer-AI-and-GenAI.pdf), [Menlo 2026](https://menlovc.com/perspective/2026-the-state-of-enterprise-ai/).

#### 1.1.6 Personal subscriptions

```math
B^{\mathrm{pers}}_t=\min\Big(B^{\mathrm{raw}}_t\frac{1-\kappa e_t}{1-\kappa e_0},\;R_C+\max(0,B^{\mathrm{pers}}_0-R_C)\max(0,1-t/5)\Big),\qquad R_C=12\,N_N\,k\,F_C
```

| Symbol | Meaning |
|---|---|
| $\kappa$ | cannibalization of personal plans by employer access: .8 / .5 / .2 |
| $e_t$ | employer coverage, linear from 0.4 to 0.8 / 0.7 / 0.6 |
| $N_N$ | Netflix paid accounts, 0.325B |
| $k$ | Claude-to-Netflix account ratio: 5 / 15 / 30% |
| $F_C$ | region-weighted price, $13.53/month |

Source: [Netflix 10-K](https://www.sec.gov/Archives/edgar/data/1065280/000106528025000044/nflx-20241231.htm).

### 1.2 Free cash flow (years 1–10)

```math
Y_t=R_t-\max\big(K^{\mathrm{floor}}_t,\;c_tR_t\big)-(o_t+x_t)R_t,\qquad FCF_t=Y_t-0.25\max(Y_t,0)
```

#### 1.2.1 Cost path

```math
\theta_t=\theta^\ast+(\theta_0-\theta^\ast)\,2^{-t/H},\qquad \theta=(c,o,x),\qquad H=3
```

$\theta_0$ = (56.6%, 47.2%, 2.8%) is reported nine-month compute, other opex and capex. $\theta^\ast$ is the scenario steady state, (48%, 25%, 6%) in the base case. $H$ = 3 years is the development estimate from 18 cloud-software margin paths (§3.2). `cost_half_life=None` jumps to $\theta^\ast$ at $t=1$.

#### 1.2.2 Compute commitments

```math
K^{\mathrm{floor}}_1=70.7,\qquad K^{\mathrm{floor}}_{2..4}=\frac{451.6-70.7}{3},\qquad K^{\mathrm{floor}}_{5..19}=\frac{900.9-451.6}{15},\qquad K^{\mathrm{floor}}_{20+}=0
```

Commitments are a cash floor and create no revenue. The trace reports `commitment_implied_revenue` = $K/c$ and `idle_commitment_cost`; base idle cost is 15.8 / 60.7 / 46.9 / 31.1 in years 1–4.

### 1.3 Continuation value (t > 10)

```math
a_{10}=(R_{10},0,0,0),\qquad a_t=a_{t-1}A,\qquad A=P\,\mathrm{diag}\big(k(1+g),\,0.85k,\,1.08k(1+g),\,0\big)
```

```math
\mathbb E[FCF_t]=a_t\,\mu-S_t\max\Big(0,\;K^{\mathrm{floor}}_t-\frac{c\,\mathbf 1^\top a_t}{S_t}\Big),\qquad \sum_{t>30}\frac{\mathbb E[FCF_t]}{(1+W)^t}=\frac{a_{30}B(I-B)^{-1}\mu}{(1+W)^{30}},\quad B=\frac{A}{1+W}
```

| Symbol | Meaning |
|---|---|
| $a_t$ | expected revenue mass in states (mature, declining, renewed, exited) |
| $k$ | rescales growth so the survivor long-run growth equals $g$: $\rho\big(P_{1:3,1:3}\,\mathrm{diag}(1+g,\,0.85,\,1.08(1+g))\big)\,k=(1+g)(1-e)$ |
| $g$ | terminal growth: 2.5 / 3 / 3.5% |
| $S_t$ | survival probability; equity bears no commitments after exit |
| $\mu$ | state margins (§1.3.2) |

#### 1.3.1 Lifecycle chain and exit hazard

```math
P=\begin{pmatrix}1-e-\delta-u&\delta&u&e\\0.10&0.90-e-u&u&e\\0.40&\delta&0.60-e-\delta&e\\0&0&0&1\end{pmatrix},\qquad e=\big[1-(1-0.08)^{1/5}\big]\,\varsigma
```

$e$ counts only zero-recovery **distress** exits; acquisitions pay shareholders (§3.4). $\varsigma$ is the distress share of large-firm delistings: 8% in base ([Daepp et al.](https://doi.org/10.1098/rsif.2015.0120)) and 50% in bear (dot-com bankruptcies over all exits, 2/4). Bull uses $e$ = 0.09%/yr, the historical large-US failure rate. Decline $\delta$ = .30 / .20 / .10 and renewal $u$ = .03 / .08 / .15. Source for the 8%/5y delisting rate: [BCG](https://www.bcg.com/publications/2026/why-do-companies-fail-us-failure-rates).

#### 1.3.2 State margins

```math
\mu=\big(m,\;0.2m,\;\min\Big(0.6,\frac{4m}{3}\Big),\;0\big),\qquad m=(1-c^\ast-o^\ast-x^\ast)(1-0.25)
```

Base $m$ = 15.75%. Bear's own cost ratios are loss-making, so its tail is negative.

### 1.4 Equity bridge

```math
Cash-Debt=212.684-110.873
```

Pro forma cash and the convertible carrying value are illustrative. The updated as-adjusted bridge (232.351 − 109.742) adds 20.80. Dilution and final capitalization are unresolved.

### 1.5 Uncertainty

```math
Z_{t}\sim P_Z,\qquad z\sim\mathrm{Tri}(-1,0,1),\qquad \theta(z)=\theta_{\mathrm{base}}+|z|\,(\theta_{\mathrm{side}(z)}-\theta_{\mathrm{base}})
```

One common factor moves every scenario parameter together toward bear ($z<0$) or bull ($z>0$). This is a wide comonotone stress band, not an estimated posterior. Macro paths alone give mean 199.72 and P5–P95 of 109.24–262.33.

## 2. Scenario parameters (assumptions)

| Parameter | Bear | Base | Bull |
|---|---:|---:|---:|
| Early / scale-up / SME / large weights | 30/30/25/15% | 15/25/30/30% | 5/15/30/50% |
| Pilot fraction | 25% | 30% | 20% |
| Pilot success / rollout | .20 / 2 | .35 / 3 | .50 / 4 |
| Initial volume / price | 1.45 / .65 | 1.65 / .78 | 1.85 / .88 |
| Acquisition / replacement | .10 / .50 | .20 / 1 | .30 / 1.25 |
| Subscription growth | 3% | 12% | 22% |
| Steady compute / other / capex | .65 / .35 / .06 | .48 / .25 / .06 | .35 / .20 / .05 |
| Terminal capture $c_{10}$ | 15% | 41% (held) | 50% |
| Distress exit $e$ / decline / renewal | .00827 / .30 / .03 | .00132 / .20 / .08 | .0009 / .10 / .15 |
| Terminal growth $g$ | 2.5% | 3% | 3.5% |
| WACC | 15% | 12% | 10% |

## 3. Evidence and validation

### 3.0 Data provenance

Every SEC figure used in §3.2–3.4 has two sources: original-vintage XBRL, and the figure printed in the filed document. That is 205 values from 41 filings, all matching exactly ([record](data/sec_reconciliation.csv); 34 are reported in USD millions and reconcile only to that rounding). Each acquisition has two independent sources ([events](data/stage4_exit_events.csv)); NetSuite's equity value rests on one. A test fails if any of these figures is unreconciled.

### 3.1 Release gate

`python -m evaluation.validation_gate --audit` → **BLOCKED**. To release: at least 10 unexposed issuer families across 2 technology cycles, five-year equity WAPE ≤ 30%, absolute bias ≤ 15%, beat flat market cap and constant P/S, full company profiles, frozen predictions and an independent reviewer. The [acquisition endpoint policy](evaluation/acquisition_endpoint_policy.md) was **approved** on 2026-11-19 and is enforced by the gate. An acquired issuer is scored on the equity value paid at close against model equity at the matched horizon $k=\max(1,\mathrm{round}(\tau))$, never as zero.

### 3.2 Margin path: stage-4 test, scored once

```math
m=\frac{CFO-\mathrm{capex}-\mathrm{cap.\ software}}{\mathrm{revenue}}
```

Preregistered and frozen before labels were opened ([prereg](evaluation/stage4_margin_preregistration.md), [score](evaluation/stage4_margin_score.json)). 11 of 17 issuers scored; the 6 acquired issuers are unlabelled.

| Model (MAE, pp) | Dev LOO | Stage-4 all | 2015 | 2020 |
|---|---:|---:|---:|---:|
| Hold origin margin | 9.64 | 23.44 | 18.60 | 25.26 |
| Fade to 15% | 11.12 | 15.07 | 13.39 | 15.69 |
| Pooled mean | 9.28 | 8.63 | 11.45 | 7.57 |
| Converge, 3-year half-life | 8.56 | 6.77 | 10.10 | 5.52 |
| **Leverage (preregistered pick)** | **4.94** | **8.87** | 5.99 | 9.94 |

The pick was not promoted because it did not beat the pooled mean. The roster is now development data. On all 18 observations (`margin_development`), SBC-adjusted margins five to six years out have median 11.1% and P90 24.4%. A 3-year half-life converging to 18.1% (SBC-adjusted) has LOO MAE 7.26 pp, against 16.56 for holding the origin margin. The modeler was not blind to these firms' history.

### 3.3 Revenue growth persistence (development)

```math
g_t=g_\infty+(g_0-g_\infty)\,2^{-t/H_g},\qquad g_0=\ln\frac{R_0}{R_{-1}},\qquad \ln\frac{R_h}{R_0}=\sum_{t\le h}g_t
```

| Model (LOO MAE, log revenue) | 18 obs |
|---|---:|
| Flat | 1.436 |
| Hold $g_0$ | 0.660 |
| Engine-style linear 7-year fade from $g_0$ | 0.242 |
| Fitted decay ($H_g$ = 4, $g_\infty$ = 6.5%) | 0.221 |

The engine's fade shape fits about as well as the fitted decay. Its base path from 81 equals a SaaS issuer with $g_0\approx$ 0.24–0.29, the 17th–33rd percentile of the panel. Anthropic's observed $g_0\approx$ 2.57 is far above the panel maximum of 0.63, so this evidence cannot adjudicate the starting point. No default was changed.

### 3.4 Exits (development)

| Roster (5 years) | n | Acquired | Bankrupt | Acquisitions per year |
|---|---:|---:|---:|---:|
| Cloud 2015 | 10 | 5 | 0 | ≈12% |
| Cloud 2020 | 14 | 1 | 0 | ≈2% |
| Dot-com 1999 | 18 | 2 | 2 | — |

Acquired cloud issuers were $3–26B; the five 2015 deals paid 1.0–2.2x the May-2015 market cap ([events](data/stage4_exit_events.csv)). Hence exit hazard $e$ is distress-only (§1.3.1).

### 3.5 Five-year equity backtest, exposed cloud cohort (diagnostic)

Five Bessemer 2020 issuers, FY2020 inputs, end-2025 market cap. Margins converge to a family-excluded $m^\ast$ (§3.2).

| Metric | Model | Flat cap | Constant P/S |
|---|---:|---:|---:|
| Equity WAPE | 70.98% | 58.82% | 124.89% |
| Equity bias | −49.20% | +17.73% | +124.89% |
| Equity Spearman | −0.3 | −0.6 | −0.6 |
| Revenue / FCF WAPE | 16.25% / 37.91% | — | — |
| Revenue / FCF Spearman | 0.9 / 0.7 | — | — |

The model ranks fundamentals well but not market caps; equity error is mostly multiple dispersion (10x–104x 2025 FCF). Variants: hold margin 69.09%; old shared 15% margin 77.21%; WACC 8% 61.37%.

### 3.6 Earlier experiments (all retrospective, none promoted)

| Experiment | Result | Script |
|---|---|---|
| 1999 top-10 FY2000 nowcast | MAPE 21.54% (flat 50.23%) | `company_oos` |
| FY2001–04 fixed fade | MAPE 304.61%; rejected | `company_oos` |
| Five-year saturation, leave-issuer-out | WAPE 41.08% (flat 61.19%) | `five_year` |
| External 1999 cohort | saturation WAPE 60.21% (flat 69.97%) | `external_validation` |
| Financial factors / covariance | no external improvement | `covariance_factors`, `structural_factors` |
| Cloud 2020 revenue, frozen size blend | WAPE 16.25% (flat 50.81%) | `cloud_cycle` |
| Joint engine, aggregate restriction | equity WAPE 86.07% | `joint_model_audit` |
| Equity-loss training transfer | 88.48 / 61.40 / 65.63% (flat 58.82%) | `equity_training` |
| Dot-com competing exits | standalone / bankrupt / merger 74 / 13 / 13% | `competing_risk` |

### 3.7 Sensitivities (base, normal regime)

| Variant | Equity |
|---|---:|
| Base | 249.22 |
| No latent health | 152.68 |
| No extra duration | 252.08 |
| No vendor transitions | 204.25 |
| All disabled (open lifecycle) | 123.62 |
| Constant winter / boom | 54.35 / 266.22 |
| Costs jump to steady state at t = 1 | 322.58 |
| 1,024-path mean, as-adjusted bridge: original / reported compute ratio held / both ratios held | 220.52 / 135.26 / −153.05 |

## 4. Reproduce

```bash
pip install numpy scipy
python -m unittest discover -s evaluation -p 'test_*.py'   # 127 tests
python -m evaluation.validation_gate --audit
python -m models.joint_customer_states
python -m evaluation.reverse_dcf --equity 1200
python -m evaluation.margin_path --verify
python -m evaluation.margin_development
python -m evaluation.growth_persistence
python -m evaluation.saas_exit
python -m evaluation.cloud_equity
```

Data definitions: [data/README.md](data/README.md). Protocol: [MODEL_VALIDATION_PROTOCOL.md](MODEL_VALIDATION_PROTOCOL.md), [AGENTS.md](AGENTS.md).
