# Anthropic Valuation — Lifecycle DCF (v2)

**English** · [简体中文](README.zh-CN.md)

Research snapshot: 2026-11-19. Units: USD billions unless specified. Exploratory conditional stress tests, not fair-value targets.

## Results

| Scenario | Year 1 revenue | Year 5 revenue | Year 10 revenue | PV years 1–10 | PV years 11–30 | Enterprise value | Equity residual |
|---|---:|---:|---:|---:|---:|---:|---:|
| Bear | 57.15 | 36.66 | 31.40 | -255.00 | -21.68 | -276.68 | -174.87 |
| Base | 105.30 | 202.50 | 221.34 | 45.56 | 33.10 | 78.66 | 180.47 |
| Bull | 137.70 | 364.50 | 467.21 | 516.03 | 163.20 | 679.23 | 781.04 |

Negative equity residual means funding distress, not a negative stock price. No financing or restructuring path is modeled. The earlier unconstrained Gordon-growth scenario gave 5,446.15; v2 changes revenue constraints and the terminal methodology jointly, so the difference cannot be attributed solely to Gordon growth. None of these are statistically calibrated forecasts.

## Mathematical valuation methodology

All monetary variables are in **USD billions**, except unit prices. Time $t$ is measured in annual steps from the October 2026 run-rate snapshot. Quantities identified as assumptions are scenario inputs, not estimated facts.

### Step 1 — Establish the revenue baseline

**Observed inputs**

| Input | Value | Definition |
|---|---:|---|
| $R_0$ | 81.000 | October annualized run rate |
| $R_{9m}$ | 33.242 | Nine-month realized revenue |
| $C_{9m}$ | 26.300 | Nine-month consumption revenue |

**Consumption share:**

```math
\omega=\frac{C_{9m}}{R_{9m}}=\frac{26.300}{33.242}\approx79.12\%
```

**Initialize consumption and subscription revenue:**

```math
A_0=R_0\omega\approx64.085
```

```math
B_0=R_0(1-\omega)\approx16.915
```

Source: [SEC prospectus](https://www.sec.gov/Archives/edgar/data/2130357/000162828026074338/anthropicpbc-sx1ax3.htm), [October run-rate disclosure](https://www.sec.gov/Archives/edgar/data/2130357/000162828026074628/anthropicpbc-fwpjapanprospa.htm). Applying the historical mix to October is a proxy, not an observed October mix. Consumption does not mean strictly API revenue; subscription does not mean strictly consumer revenue.

### Step 2 — Bottom-up consumer demand (independent cross-check)

For country $c$, age group $a$, and household-income group $h$, define:

```math
R_{\mathrm{consumer},t}
=12\sum_{c,a,h}N_{cah,t}I_{cah,t}U_{cah,t}P_{cah,t}M_{cah,t}F_{cah,t}
```

| Symbol | Definition |
|---|---|
| $N$ | Population in billions |
| $I$ | Internet access probability |
| $U$ | AI adoption conditional on access |
| $P$ | Paid conversion conditional on adoption |
| $M$ | Anthropic share among paying users |
| $F$ | Monthly realized price in USD per paying user |

**Evidence:** [Pew age-group survey](https://www.pewresearch.org/chart/majorities-of-adults-under-50-now-use-chatgpt/), [ITU connectivity](https://www.itu.int/itu-d/reports/statistics/facts-figures-2025/), [World Bank income groups](https://databank.worldbank.org/metadataglossary/world-development-indicators/country/HIC).

US chatbot ever-use rates are not global paid conversion rates. Country GNI groups are not household-income groups. Unsupported markets must be excluded. The bottom-up function is implemented, but its missing country-level paid demand inputs prevent calibration; it is not added to the run-rate forecast.

#### Netflix account-level calibration stress

Netflix crossed 325M paid memberships in 2025 and reported an audience approaching 1B. An account is not a person: roughly three viewers share each paid membership. Define $N_N$ as paid accounts in billions, $A_N$ as viewers in billions, $q$ as viewers per account, and $k$ as assumed Claude individual paid accounts relative to Netflix paid accounts. The implied viewer-equivalent conversion is $k/q$, not $k$. This is a benchmark, not an identified AI conversion rate. China is excluded from Netflix; other service boundaries differ. Do not use global population as the denominator.

```math
N_C=N_N k=A_N\frac{k}{q},\qquad q=\frac{A_N}{N_N}\approx3.08
```

```math
F_C=20\sum_r\frac{N_{N,r}}{\sum_j N_{N,j}}\frac{F_{N,r}}{17.20}\approx13.53
```

```math
R_C=12N_CF_C
```

2024 regional paid memberships (millions) and monthly revenue per membership: US/Canada 89.625 / $17.20; EMEA 101.133 / $10.96; LATAM 53.327 / $8.24; APAC 57.541 / $7.29. Assume the same geographic account mix and relative price index; $20 is a North American price assumption. This does not establish actual Claude regional pricing. Paid account ratios 5%, 15%, 30% are illustrative, equivalent to approximately 1.63%, 4.88%, 9.75% of Netflix's audience. The optional DCF stress phases any personal revenue reduction in over five years and leaves employer invoices untouched. The original results above remain the uncapped baseline. No cap is asserted in the lifecycle tail; personal payers are net of employer substitution in the forecast.

| Scenario | k | Paid accounts (M) | Revenue ceiling ($B) | Stress EV ($B) | Stress equity ($B) |
|---|---:|---:|---:|---:|---:|
| Bear | 5% | 16.25 | 2.64 | -286.94 | -185.13 |
| Base | 15% | 48.75 | 7.91 | 78.46 | 180.27 |
| Bull | 30% | 97.50 | 15.83 | 679.23 | 781.04 |

[Netflix 2024 SEC 10-K](https://www.sec.gov/Archives/edgar/data/1065280/000106528025000044/nflx-20241231.htm) · [2025 Q4 shareholder letter](https://www.sec.gov/Archives/edgar/data/1065280/000106528026000033/ex991_q425.htm) · [Netflix supported markets](https://help.netflix.com/en/node/14164/).

Reproduce: `python -m models.netflix_benchmark`.


### Step 3 — Bottom-up enterprise demand (independent cross-check)

For country $c$, industry $j$, and firm-size group $k$:

```math
R_{\mathrm{enterprise},t}
=12\sum_{c,j,k}E_{cjk,t}D_{cjk,t}X_{cjk,t}M_{cjk,t}
```

| Symbol | Definition |
|---|---|
| $E$ | Employees in billions |
| $D$ | Fraction of employees in adopting firms (employee-weighted) |
| $X$ | Mean monthly AI spend per employee in adopting firms |
| $M$ | Anthropic share of that spending |

Source: [Ramp AI Index](https://ramp.com/data/ai-index?stream=top). Ramp firm-level adoption and median spending cannot substitute for employee-weighted adoption and mean spending without additional weighting data. This check is not yet calibrated and is not added to the forecast.

### Step 4 — Split existing consumption revenue into risk cohorts

```math
S_0=A_0w_S,\qquad L_0=A_0w_L
```

```math
H_0=A_0(1-w_S-w_L)
```

| Symbol | Definition |
|---|---|
| $S_t$ | Startup cohort revenue |
| $L_t$ | Trial/pilot cohort revenue |
| $H_t$ | Mature deployment cohort revenue |
| $w_S,w_L$ | Assumed starting cohort shares |

Base case: $w_S=0.40$, $w_L=0.30$. These are unobserved allocation assumptions, not measured customer mix.

**Capital recycling diagnostic (not identified):**

```math
\phi_{\mathrm{VC}}=\frac{\sum_i R_i f_i}{\sum_i R_i}
```

Here $R_i$ is customer revenue and $f_i$ is its fraction funded by venture capital. Invoice-level funding attribution is missing. Ramp's spend concentration and JPMorgan's VC-backed firm-count share cannot be multiplied to identify this parameter.

### Step 5 — Startup survival and funding risk

Use a constant-hazard survival approximation:

```math
\lambda=-\frac{\ln s_5}{5}
```

```math
s(t)=e^{-\lambda t}=s_5^{t/5}
```

```math
s_1=0.54^{1/5}\approx0.884
```

The base five-year survival of 54% is a rounded scenario anchor from [BLS historical establishment cohorts](https://www.bls.gov/spotlight/2024/business-employment-dynamics-twentieth-anniversary/), not measured AI startup survival.

Existing startup revenue after survival, funding and usage effects:

```math
S_t^{\mathrm{existing}}
=S_{t-1}s_1F_tK_t
```

```math
F_t=1+(f-1)d_t
```

$f$ is the conditional funding/spending multiplier, $d_t$ is the fade factor defined below, and $K_t$ is the common price-volume-share multiplier.

### Step 6 — GTM conversion and project rollout

```math
G(L,p,m,r)=L\left[pm+(1-p)r\right]
```

| Symbol | Definition |
|---|---|
| $L$ | Existing pilot revenue |
| $p$ | Successful deployment fraction, assumed revenue-weighted |
| $m$ | Spend expansion conditional on success |
| $r$ | Residual spend of unsuccessful projects |

The implemented forecast sets $r=0$ and transfers successful pilots into the mature cohort:

```math
G_t=p\,m\,L_{t-1}
```

Break-even example:

```math
G(100,0.25,4,0)=100
```

Evidence: [Gartner project abandonment](https://www.gartner.com/en/articles/genai-project-failure), [McKinsey enterprise AI impact](https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai-2025), [ChartMogul downstream retention](https://chartmogul.com/reports/saas-retention-the-ai-churn-wave/). Project-count abandonment, EBIT impact and software NRR measure different outcomes; none directly identifies the revenue-weighted $p$.

### Step 7 — Token pricing, competition, and growth fade

The fundamental identity:

```math
R_{\mathrm{token},t}=Q_t P_t M_t
```

$Q_t$ is total token volume, $P_t$ is realized USD per token, and $M_t$ is provider volume share under a consistent price convention.

At unchanged share, the volume growth required to offset a price decline $\delta$ is:

```math
g_Q=\frac{1}{1-\delta}-1
```

```math
\delta=50\%\quad\Longrightarrow\quad g_Q=100\%
```

In the forecast, annual multipliers fade toward one:

```math
d_t=\max\left(0,1-\frac{t-1}{7}\right)
```

```math
K_t=\left[1+(v-1)d_t\right]\left[1-(1-q)d_t\right]\left[1-(1-m_s)d_t\right]
```

$v$, $q$, and $m_s$ are initial annual volume, price and market-share multipliers. Source for directional price pressure: [Ramp September 2026](https://ramp.com/data/ai-index-sept-2026).

### Step 8 — Revenue recursion with overlapping personal and employer demand

```math
J_t=n d_t(S_{t-1}+L_{t-1}+H_{t-1})
```

```math
S_t=S_{t-1}s_1F_tK_t+0.4J_t,\qquad L_t=0.6J_t
```

```math
H_t=(H_{t-1}+pmL_{t-1})K_t
```


Consumption and subscription are invoice categories, not unique people. Split subscriptions into personal and enterprise invoices (initial personal fraction 50% assumption). Let A denote personal payment and B employer access.

```math
\Pr(A\cup B)=\Pr(A)+\Pr(B)-\Pr(A\cap B)
```

```math
\Pr(A)=\Pr(A\mid B)\Pr(B)+\Pr(A\mid B^c)(1-\Pr(B))
```

```math
\kappa=1-\frac{\Pr(A\mid B)}{\Pr(A\mid B^c)},\qquad \Pr(A)=\Pr(A\mid B^c)(1-\kappa\Pr(B))
```


Actual separate invoices both count; only conditional demand is adjusted. Let employer coverage interpolate from e0 to e10. Personal revenue is scaled relative to baseline overlap; enterprise subscriptions grow independently at the assumed rate b.

```math
e_t=e_0+(e_{10}-e_0)\min(t/10,1)
```

```math
B^{raw}_t=B^{raw}_{t-1}(1+bd_t)
```

```math
B^{personal}_t=B^{raw}_t\frac{1-\kappa e_t}{1-\kappa e_0}
```

```math
B^{enterprise}_t=B^{enterprise}_{t-1}(1+bd_t)
```

```math
R_t^{raw}=S_t+L_t+H_t+B^{personal}_t+B^{enterprise}_t
```


A conditional effective revenue ceiling limits the forecast, not a measured TAM:

```math
D_t=81[1+(d_{\max}-1)\min(t/10,1)]
```

```math
R_t=\min(R_t^{raw},D_t)
```


Every cohort and the raw personal accumulator is scaled by the same ratio if the ceiling binds. The ceiling is an explicit stress input, not a substitute for actual country and industry demand calibration.

### Step 9 — Compute commitments and cash flow

[SEC prospectus](https://www.sec.gov/Archives/edgar/data/2130357/000162828026074338/anthropicpbc-sx1ax3.htm): aggregate commitments 900.9, including 70.7 in next 12 months and 451.6 by end of 2030. Approximate annual buckets reconcile total; actual calendar maturity schedule is unknown.

```math
K^{floor}_1=70.7,\qquad K^{floor}_{2:4}=(451.6-70.7)/3
```

```math
K^{floor}_{5:19}=(900.9-451.6)/15,\qquad K^{floor}_{20:30}=0
```

```math
C_t=\max(K^{floor}_t,cR_t),\qquad O_t=oR_t,\qquad X_t=xR_t
```

```math
Y_t=R_t-C_t-O_t-X_t,\qquad FCF_t=Y_t-0.25\max(Y_t,0)
```


Cash tax proxy, no working capital forecast. Commitments are a floor, not additional spend on top of variable compute. Historical CFO less PPE purchases is 5.644, or 3.689 after lease prepayments; neither is normalized FCFF.

### Step 10 — Lifecycle continuation (replaces Gordon terminal value)

#### Why replace the Gordon Growth Model?

The Gordon model assumes a normalized cash flow grows at a fixed rate indefinitely, conditional on a continuing business:

```math
TV_T=\frac{FCF_T(1+g)}{W-g}
```


It is mathematically valid when the cash-flow assumptions hold and the discount rate exceeds growth. It is not a reliable default for a young model provider facing commoditization, price competition and business-model displacement. A zero or negative growth rate is possible even in Gordon; the issue is imposing one permanent regime.

- [Chan, Karceski and Lakonishok (2003)](https://www.nber.org/papers/w8282) find weak persistence and limited predictability of long-run firm earnings growth.
- [BLS 2013 cohort](https://www.bls.gov/opub/ted/2024/34-7-percent-of-business-establishments-born-in-2013-were-still-operating-in-2023.htm): 34.7% of business establishments survived ten years.
- [BLS 2000 cohort](https://www.bls.gov/opub/ted/2026/outlast-state-establishment-survival-rates-from-2000-to-2026.htm): 15.7% survived 26 years. These are establishments, not matched public technology firms; neither number calibrates Anthropic's hazard.

A growing industry does not guarantee a particular company's cash flows grow. Industry gains may accrue to customers and competitors. The new model permits contraction, renewal, and absorbing exit. It uses a finite 30-year horizon, zero residual value thereafter, explicitly a conservative truncation assumption rather than proof the company will cease to exist.


Start year 10 in Mature. States in order: Mature, Declining, Renewed, Exited. Exit is absorbing. Annual exit probability e, decline probability d, renewal probability u are assumed, not fitted.

```math
P=\begin{pmatrix}1-e-d-u&d&u&e\\0.10&1-e-0.10-u&u&e\\0.40&d&1-e-0.40-d&e\\0&0&0&1\end{pmatrix}
```

```math
\pi_{10}=(1,0,0,0),\qquad \pi_t=\pi_{t-1}P
```


Expected revenue mass by state, not merely probability times a fixed revenue, preserves path-dependent growth.

```math
a_{10}=(R_{10},0,0,0),\qquad a_t=a_{t-1}P\,\mathrm{diag}(1,0.85,1.08,0)
```

```math
E[R_t]=\sum_j a_{t,j}
```


Assumed normalized after-tax cash margins by state: 15%, 3%, 20%, 0%. These include ordinary variable compute, other expenses and capex. No new revenue ceiling is applied in the tail. Charge remaining commitments even after exit in this no-contract-release stress; actual resolution or recovery is not modeled.

```math
E[FCF_t]\approx \sum_j a_{t,j}\mu_j-\max(0,K^{floor}_t-cE[R_t])
```


The aggregate commitment shortfall is a lower bound by convexity, not exact expected shortfall.

```math
EV_0=\sum_{t=1}^{10}\frac{FCF_t}{(1+W)^t}+\sum_{t=11}^{30}\frac{E[FCF_t]}{(1+W)^t}
```

```math
V_{\mathrm{equity}}=EV_0+212.684-110.873
```


Pro forma cash and convertible carrying value are illustrative; actual final capitalization, debt repayment terms and dilution remain unresolved. No terminal sale price or post-year-30 cash flows are assumed. Exit probabilities should not double-count credit risk in WACC.

### Step 11 — Scenario simulation

2,000 seeded triangular draws interpolate between bear/base/bull parameters using one common factor. Quantiles of equity residual: -70.70 / 185.39 / 455.97. Not statistical confidence intervals.

## Scenario inputs

| Input | Bear | Base | Bull |
|---|---:|---:|---:|
| Startup / trial starting weights | 55% / 25% | 40% / 30% | 25% / 20% |
| Five-year startup survival | 40% | 54% | 65% |
| Funding multiplier | .70 | .90 | 1.05 |
| GTM success / rollout | .20 / 2 | .35 / 3 | .50 / 4 |
| Initial volume / price / share multipliers | 1.45 / .65 / .90 | 1.65 / .78 / .96 | 1.85 / .88 / 1.00 |
| New consumption rate | 10% | 20% | 30% |
| Subscription growth | 3% | 12% | 22% |
| Compute / other / capex ratios | .65 / .35 / .06 | .48 / .25 / .06 | .35 / .20 / .05 |
| Year-10 revenue ceiling multiple of 81 | 2 | 4 | 8 |
| Initial employer coverage | 40% | 40% | 40% |
| Year-10 employer coverage | 80% | 70% | 60% |
| Cannibalization | 80% | 50% | 20% |
| Annual lifecycle exit / decline / renewal | 12% / 30% / 3% | 6% / 20% / 8% | 3% / 10% / 15% |
| Discount rate | 15% | 12% | 10% |

These are scenario assumptions, not measured values. Base implied probability of surviving years 11–30 conditional on reaching year 10 is 29.0%; bear 7.8%, bull 54.4%.

## Reproduce and evaluate

```bash
python -m models.valuation
python -m unittest discover -s evaluation -v
```


Ten tests pass: source integrity, historical reconciliation, BLS leave-one-cohort-out, project conversion, price-volume identity, scenario ordering, reproducibility, commitment sum, overlap and revenue ceiling, lifecycle exit. Historical proxy validation is not a calibrated Anthropic out-of-sample backtest.

- [Data register](data/observations.csv)
- [Data definitions](data/README.md)
- [Model](models/valuation.py)
- [Tests](evaluation/test_models.py)

Next: estimate country-age paid conversion and employer overlap; customer funding provenance; enterprise budgets; lifecycle transitions from comparable public technology companies; actual commitment schedule. Until then, no precise intrinsic value claim.
