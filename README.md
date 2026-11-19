# Anthropic valuation — an exploratory research project

> just a exploratory project for fun. I just really want to calculate if it is overvalued.

**Research snapshot: 2026-11-19.** All monetary outputs are USD billions unless otherwise specified. This is an exploratory stress model, not a price target or investment recommendation.

## Preliminary conclusion

The October $81B revenue run rate is not equivalent to contracted or realized annual sales. 79% of the first nine months' revenue was consumption-based; five customers contributed roughly 25%. Disclosed cash and short-term investments were $131.845B as of September, compared with $110.735B in nine-month financing inflows and $6.569B of operating cash flow. The updated prospectus reports $900.9B of aggregate compute-related purchase/lease commitments, including $70.7B in the next twelve months. This creates material operating leverage if demand disappoints.

The current scenario engine produces these **conditional stresses**, not an empirically fitted fair-value range:

| Scenario | Year 1 revenue | Year 5 revenue | Operating EV | Illustrative equity bridge |
|---|---:|---:|---:|---:|
| Bear | 57.56 | 39.54 | -227.63 | -125.82 |
| Base | 105.66 | 239.05 | 256.78 | 358.59 |
| Extreme upside stress | 164.10 | 1230.83 | 5344.34 | 5446.15 |

Negative residual equity signals funding distress, not a negative tradable share price. The extreme upside outcome exposes how extreme compounding of successful projects and new demand changes the output; it is not a supported forecast. A $2T equity benchmark is therefore not justified merely by current adoption or annualized revenue; it requires assumptions about durable demand, prices and margins that remain unverified. At a 12% discount rate, 3% perpetual growth and 25% FCFF margin, a steady-state $2T EV requires $720B next-year revenue (reverse DCF, ignoring interim cash flows). The $2T reference is hypothetical, not a verified current market cap.

## Why the extreme upside scenario is so large

The previous Bull label should be understood as an **uncalibrated extreme upside stress**, not a reasonable forecast or target. The model has no validated addressable-demand ceiling, and its optimistic inputs compound together.

In year 1, the existing consumption-revenue multiplier is:

$
K_1=1.85\times0.88\times1.00=1.628
$

Successful pilot deployment doubles the previous trial cohort before the common multiplier:

$
p\times m=0.50\times4=2.00
$

$
G_1\times K_1=2.00L_0\times1.628=3.256L_0
$

Additionally, new consumption revenue is assumed to be 30% of the preceding year's consumption revenue at the start of the forecast. This can overlap economically with the assumed volume expansion if the underlying customer acquisition and spending inputs are not carefully separated.

| Forecast year | Revenue (USD B) | Cash-flow proxy (USD B) |
|---|---:|---:|
| 1 | 164.10 | 39.28 |
| 2 | 299.69 | 80.68 |
| 3 | 519.74 | 155.92 |
| 4 | 836.62 | 250.98 |
| 5 | 1,230.83 | 369.25 |
| 6 | 1,628.33 | 488.50 |
| 7 | 1,901.18 | 570.35 |
| 8 | 1,913.42 | 574.02 |
| 9 | 1,887.34 | 566.20 |
| 10 | 1,863.60 | 559.08 |

The year-10 revenue is around 23 times the initial annualized run rate. This is an output of the assumptions rather than evidence of market demand.

The optimistic cost assumptions produce a normalized cash-flow margin of:

$
\mu=0.75(1-0.35-0.20-0.05)=30\%
$

With a 10% discount rate and 3.5% perpetual growth:

$
PV(TV)=\frac{559.08\times1.035}{(0.10-0.035)(1.10)^{10}}\approx3432.21
$

$
EV=1912.12+3432.21=5344.33
$

$
\frac{PV(TV)}{EV}\approx64.2\%
$

The illustrative equity bridge then adds 101.811 billion, giving approximately 5.446 trillion.

### One-at-a-time sensitivity (all other extreme upside inputs unchanged)

| Changed assumption | Equity residual (USD B) |
|---|---:|
| Original extreme stress | 5,446.15 |
| Annual initial price multiplier: 0.88 to 0.65 | 2,348.34 |
| Annual initial volume multiplier: 1.85 to 1.45 | 2,365.07 |
| Successful pilot rollout: 4x to 2x | 3,307.08 |
| Initial new revenue rate: 30% to 10% | 2,915.76 |
| Cost ratios changed to base case | 2,916.34 |
| WACC 12%, terminal growth 3% | 3,860.84 |

These are recomputed counterfactuals, not confidence intervals; the effects are non-additive. The current upside case is useful only as a diagnostic showing how unsupported growth and margin assumptions can inflate valuation. A defensible upside forecast requires a calibrated bottom-up paid demand ceiling, mutually exclusive customer acquisition and expansion drivers, and long-run competitive price and cost estimates. Do not interpret the extreme scenario as fair value.

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

### Step 8 — Consolidated annual revenue recursion

New consumption revenue:

```math
J_t=n\,d_t(S_{t-1}+L_{t-1}+H_{t-1})
```

```math
S_t=S_{t-1}s_1F_tK_t+0.4J_t
```

```math
L_t=0.6J_t
```

```math
H_t=(H_{t-1}+pmL_{t-1})K_t
```

The 40/60 startup/pilot split of new revenue is an assumption.

Subscription revenue:

```math
B_t=B_{t-1}\left[1+b\,d_t+g(1-d_t)\right]
```

**Total modeled annual revenue:**

```math
R_t=S_t+L_t+H_t+B_t
```

$n$ is the new-consumption-revenue rate, $b$ is initial subscription growth, and $g$ is terminal growth. No independent bottom-up demand ceiling has been calibrated, which makes the upside scenario particularly speculative.

### Step 9 — Compute commitments, operating costs & cash flow

The disclosed commitments are $70.7B over the next 12 months, $451.6B before the end of 2030 and $900.9B in aggregate. Source: [SEC S-1/A](https://www.sec.gov/Archives/edgar/data/2130357/000162828026074338/anthropicpbc-sx1ax3.htm).

The **implemented approximate annual allocation**, not a verified contractual payment schedule:

```math
K_t^{\mathrm{floor}}=
\begin{cases}
70.7 & t=1\\
(451.6-70.7)/3.25 & 2\le t\le4\\
(900.9-451.6)/15 & t\ge5
\end{cases}
```

```math
C_t=\max(K_t^{\mathrm{floor}},cR_t)
```

```math
O_t=oR_t,\qquad X_t=xR_t
```

$c,o,x$ are variable compute, other cash operating expense and incremental capex ratios. The floor is not added again to variable compute. The allocation does not exactly reconcile calendar-year maturities; this is a stress approximation.

**Simplified pretax cash surplus:**

```math
Y_t=R_t-C_t-O_t-X_t
```

**Simplified unlevered cash-flow proxy:**

```math
FCF_t=Y_t-0.25\max(Y_t,0)
```

The 25% cash tax, no loss tax benefit, no explicit working-capital schedule and cash expense classification are simplifications. This is not a full accounting FCFF reconstruction.

Historical sanity checks (nine months ending September 2026):

```math
CFO-CapEx=6.569-0.925=5.644
```

```math
CFO-CapEx-LeasePrepayments=5.644-1.955=3.689
```

Neither historical measure is normalized FCFF.

### Step 10 — Discounted cash flow and equity bridge

Forecast horizon $T=10$; assumed discount rate $W$ must exceed terminal growth $g$.

```math
m_{\infty}=0.75\max(0,1-c-o-x)
```

```math
FCF_{\infty}=R_Tm_{\infty}
```

```math
TV_T=\frac{FCF_{\infty}(1+g)}{W-g}
```

```math
EV_0=\sum_{t=1}^{T}\frac{FCF_t}{(1+W)^t}+\frac{TV_T}{(1+W)^T}
```

Illustrative equity bridge:

```math
V_{\mathrm{equity}}=EV_0+212.684-110.873=EV_0+101.811
```

The cash figure is illustrative pro forma cash and short-term investments; the convertible carrying value is not a confirmed payoff amount. Final IPO proceeds, leases, minority claims and dilution remain to be reconciled. Negative residual equity indicates distress, not a negative stock price.

### Step 11 — Reverse DCF: what does a $2 trillion valuation require?

For a hypothetical steady-state $2{,}000B enterprise value with normalized cash-flow margin $\mu$:

```math
EV=\frac{\mu R_1}{W-g}
```

```math
R_1=\frac{EV(W-g)}{\mu}
```

```math
R_1=\frac{2{,}000(0.12-0.03)}{0.25}=720
```

That is $720B of next-year annual revenue under these assumptions, ignoring interim growth and cash flows. It is an EV benchmark, not a verified equity market cap.

### Step 12 — Correlated scenario simulation

A common scenario factor is drawn using a triangular distribution:

```math
Z\sim\mathrm{Triangular}(-1,0,1)
```

```math
\theta(Z)=
\begin{cases}
\theta_{\mathrm{base}}+\lvert Z\rvert(\theta_{\mathrm{bear}}-\theta_{\mathrm{base}}),&Z<0\\
\theta_{\mathrm{base}}+\lvert Z\rvert(\theta_{\mathrm{bull}}-\theta_{\mathrm{base}}),&Z\ge0
\end{cases}
```

```math
V^{(i)}=\mathrm{DCF}(\theta(Z_i)),\qquad i=1,\ldots,2000
```

Seed = 42. This is a single-factor stress interpolation, not a fitted joint probability distribution. Its P10/P50/P90 equity residuals are -34.36 / 372.06 / 1664.25 (USD billions).

## Scenario parameter register

All values below are assumptions used in the existing code, except where a proxy anchor is noted.

| Parameter | Symbol | Bear | Base | Bull |
|---|---|---:|---:|---:|
| Startup revenue mix | $w_S$ | 55% | 40% | 25% |
| Pilot revenue mix | $w_L$ | 25% | 30% | 20% |
| Five-year survival (BLS proxy) | $s_5$ | 40% | 54% | 65% |
| Funding multiplier | $f$ | 0.70 | 0.90 | 1.05 |
| Pilot conversion | $p$ | 20% | 35% | 50% |
| Successful rollout multiplier | $m$ | 2 | 3 | 4 |
| Token volume multiplier | $v$ | 1.45 | 1.65 | 1.85 |
| Token price multiplier | $q$ | 0.65 | 0.78 | 0.88 |
| Market share multiplier | $m_s$ | 0.90 | 0.96 | 1.00 |
| New consumption revenue rate | $n$ | 10% | 20% | 30% |
| Subscription growth | $b$ | 3% | 12% | 22% |
| Compute cost ratio | $c$ | 65% | 48% | 35% |
| Other operating expense ratio | $o$ | 35% | 25% | 20% |
| Capex ratio | $x$ | 6% | 6% | 5% |
| Discount rate | $W$ | 15% | 12% | 10% |
| Terminal growth | $g$ | 2.5% | 3% | 3.5% |

## Evaluation methodology

Historical survival leave-one-cohort-out prediction:

```math
\widehat{s}_{5,-i}=\frac{1}{N-1}\sum_{j\ne i}s_{5,j}
```

```math
MAE=\frac{1}{N}\sum_{i=1}^{N}\lvert s_{5,i}-\widehat{s}_{5,-i}\rvert
```

This evaluates a historical establishment-survival proxy only. It is not an out-of-sample Anthropic forecast. The seven automated checks also test source integrity, accounting reconciliation, price-volume and conversion identities, scenario ordering and simulation reproducibility. Independent source validation remains incomplete for several key inputs.

## Reproduce

Python 3.10+; standard library only.

```bash
python -m models.valuation
python -m unittest discover -s evaluation -v
```

## Repository layout

- `data/`: source-linked observations and definitions.
- `models/`: executable cohort, GTM, demand, pricing, cash-flow, DCF and correlated scenario functions.
- `evaluation/`: source integrity checks, filing reconciliation, historical proxy holdout tests, stress identities and reproducibility.
- `research/`: methodology and open data requirements.

## Evaluation and next priorities

Seven automated checks pass. The BLS holdout error tests only the historical survival baseline; there is insufficient Anthropic time-series evidence for a valid forward revenue backtest. Source links are traceable; independent confirmation is strongest for distinct measures, not for repeated reports of the same dataset. For the next iteration, collect country population and income distribution, paid AI usage, token mix, actual customer cohorts, quarterly revenue and commitment maturity schedules. Refit on historical periods and evaluate on held-out future dates. Do not publish a precise intrinsic value until that evidence is available.
