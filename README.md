# Anthropic Valuation — Joint-State Lifecycle DCF

**English** · [简体中文](README.zh-CN.md)

Research snapshot: 2026-11-19. All amounts are USD billions unless noted.

## 1. Conclusion

**Conditional mean equity residual: $164.04B (0.164T).** This is the average of 1,024 macro paths under base structural assumptions, not a fitted fair-value target.

| Statistic | Equity residual |
|---|---:|
| P5 | 110.00 |
| Median | 171.62 |
| Mean | 164.04 |
| P95 | 187.11 |

| Normal-regime structural scenario | Year 1 revenue | Year 5 | Year 10 | EV | Equity residual |
|---|---:|---:|---:|---:|---:|
| Bear | 50.67 | 24.88 | 21.68 | -305.36 | -203.55 |
| Base | 98.80 | 195.31 | 254.21 | 85.24 | 187.05 |
| Bull | 115.69 | 396.70 | 734.42 | 910.53 | 1012.34 |

Negative residuals denote funding distress, not negative share prices. Percentiles describe conditional macro-path uncertainty, not confidence intervals. Capital structure, refinancing, restructuring and parameter estimation remain unresolved.

## 2. Overarching valuation model

The primary model is an open joint Markov revenue process with duration dependence, latent financial health, common macro regimes, vendor choice, personal demand and finite-horizon DCF. Calculation order: revenue baseline → demand ceilings and customer states → transitions and acquisition → revenue → cash flow → lifecycle continuation → equity.

Enterprise invoices are tracked in three separate ledgers (pilot, live and employer seats). The state tensor X indexes enterprise lifecycle i, dwell d, health h and vendor v, conditional on common regime Z.

```math
\widetilde X_t^{(b)}=\mathcal K_{Z_t}\big(\mathcal G_t^{(b)}(X_{t-1})M_{Z_t}\big)+A_t^{(b)}
```

```math
E_t=\sum_{b,i,d,h,v}\widetilde X_{idhv,t}^{(b)}r_v,\qquad R_t=\min(E_t,C_t)+B_t^{\mathrm{personal}}
```

```math
V^{(\ell)}_{\mathrm{equity}}=\sum_{t=1}^{10}\frac{FCF^{(\ell)}_t}{(1+W)^t}+\sum_{t=11}^{30}\frac{\mathbb E[FCF_t\mid R_{10}^{(\ell)}]}{(1+W)^t}+Cash-Debt
```

```math
\widehat V_{\mathrm{equity}}=\frac{1}{1024}\sum_{\ell=1}^{1024} V^{(\ell)}_{\mathrm{equity}}
```
Here G is ledger preprocessing for pilot conversion, growth and spending (see 5.6), b is the invoice ledger, K the reward-weighted lifecycle operator, M the conditional vendor transition, A new invoices and C the industry ceiling. Pilot conversion and price-volume factors are specified below. Cash flow is evaluated on each path before averaging.

## 3. Revenue baseline

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

## 4. Demand and industry spending constraints

### 4.1 Consumer demand and Netflix calibration

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

2024 regional paid memberships (millions) and monthly revenue per membership: US/Canada 89.625 / $17.20; EMEA 101.133 / $10.96; LATAM 53.327 / $8.24; APAC 57.541 / $7.29. Assume the same geographic account mix and relative price index; $20 is a North American price assumption. This does not establish actual Claude regional pricing. Paid account ratios 5%, 15%, 30% are illustrative, equivalent to approximately 1.63%, 4.88%, 9.75% of Netflix's audience. The personal ceiling phases any personal revenue reduction in over five years and leaves employer invoices untouched. Valuations below are reduced-model comparisons, not the main results. No cap is asserted in the lifecycle tail; personal payers are net of employer substitution in the forecast.

| Scenario | k | Paid accounts (M) | Revenue ceiling ($B) | Stress EV ($B) | Stress equity ($B) |
|---|---:|---:|---:|---:|---:|
| Bear | 5% | 16.25 | 2.64 | -286.94 | -185.13 |
| Base | 15% | 48.75 | 7.91 | 78.46 | 180.27 |
| Bull | 30% | 97.50 | 15.83 | 679.23 | 781.04 |

[Netflix 2024 SEC 10-K](https://www.sec.gov/Archives/edgar/data/1065280/000106528025000044/nflx-20241231.htm) · [2025 Q4 shareholder letter](https://www.sec.gov/Archives/edgar/data/1065280/000106528026000033/ex991_q425.htm) · [Netflix supported markets](https://help.netflix.com/en/node/14164/).

Reproduce: `python -m models.netflix_benchmark`.

### 4.2 Employer access and personal substitution

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

Actual separate invoices both count; only conditional demand is adjusted. Let employer coverage interpolate from e0 to e10. Personal revenue is scaled relative to baseline overlap; enterprise subscription dynamics are specified in Section 5.6.

```math
e_t=e_0+(e_{10}-e_0)\min(t/10,1)
```

```math
B^{raw}_t=B^{raw}_{t-1}(1+bd_t)
```

```math
B_t^{personal}=\min\left(B_t^{raw}\frac{1-\kappa e_t}{1-\kappa e_0},R_C+\max(0,B_0^{personal}-R_C)\max(0,1-t/5)\right)
```

Reset raw personal revenue to capped personal revenue divided by the overlap ratio each year.

### 4.3 Enterprise demand and industry ceiling

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

The combined Netflix/industry/lifecycle stress is reproducible with `python -m models.industry_calibration`. IDC's broad AI spending estimates by industry are in [industry_spending.csv](data/industry_spending.csv); the 2024 and 2028 totals are 234.6 and 631.4. They are analyst estimates/forecasts, not realized foundation-model invoices. Menlo estimates 176.8 of 2026 deployment spending, including 94.2 model/inference; its sample comprises US decision makers and Menlo is an Anthropic investor. Use IDC sector weights and growth rates to extrapolate the Menlo proxy, not to add the two totals. 2026 sector weights interpolate IDC's 2024–2028 endpoints.

```math
g_i=(B_{i,2028}/B_{i,2024})^{1/4}-1,\quad w_i=\frac{\sqrt{B_{i,2024}B_{i,2028}}}{\sum_j\sqrt{B_{j,2024}B_{j,2028}}}
```

```math
D_{i,0}=176.8w_i,\quad D_{i,t}=D_{i,t-1}[1+0.03+(m g_i-0.03)\max(0,1-\max(0,t-2)/8)]
```

```math
C_t=\left[c_0+(c_{10}-c_0)\min(t/10,1)\right]\sum_iD_{i,t},\quad c_0=\frac{81-B_0/2}{176.8}
```

The effective capture c includes geography, vendor share, application/infrastructure overlap and downstream leakage; it is not observed. The starting ratio implicitly assumes 50% of subscription revenue is personal. The three growth multipliers m are 0.7, 1, 1.5 and terminal effective captures are 15%, 30%, 50%, all explicit assumptions. The enterprise ceiling replaces rather than stacks with the arbitrary aggregate ceiling; it includes all consumption as a proxy and excludes personal invoices. No sector-level Claude invoice share or exact supported-country denominator is identified. The lifetime tail carries forward year-10 total revenue without an additional cap.

## 5. Joint enterprise revenue state model

### 5.1 Customer groups, closure and commercial churn

BLS establishment survival gives annual closure proxies (early information 15.03%, age 5–10 information 8.06%, age 5–10 general 7.27%); large-company distress proxy 0.132% is described in Section 7. PitchBook funding-stage eventual failure is documented but not annualized without a horizon. Ramp January 2026 reports ~4% monthly customer-count cancellation, not revenue loss; annualizing is a constant-rate sensitivity. Base revenue weights early/scale-up/SME/large are 15/25/30/30%, churn transfer factors f are 0.8/0.55/0.45/0.20. They are unknown, assumed. Conditional commercial loss q removes overlap with closure h. The resulting annual retention is 69.0/78.7/82.6/92.3%. The prior market-share multiplier is omitted to avoid counting cancellation twice.

```math
p_L=1-(1-0.04)^{12}=0.38729
```

```math
q_i=\max\left(0,\frac{f_i p_L-h_i}{1-h_i}\right),\qquad s_i=(1-h_i)(1-q_i)
```

Initial invoices are allocated by customer group; seed tenure weights are 30/25/20/15/10% within the early group; pilot shares are scenario inputs. [Official customer examples](https://www.anthropic.com/customers) are not representative of actual revenue weights.

**Capital recycling diagnostic (not identified):**

```math
\phi_{\mathrm{VC}}=\frac{\sum_i R_i f_i}{\sum_i R_i}
```

Here $R_i$ is customer revenue and $f_i$ is its fraction funded by venture capital. Invoice-level funding attribution is missing. Ramp's spend concentration and JPMorgan's VC-backed firm-count share cannot be multiplied to identify this parameter.

### 5.2 Open lifecycle and seed birth budget

Seed tenure states 0,1,2,3,4+, scaleup, mature SME, large, and permanent closure. New seed entrants are external; closure is absorbing. Dealroom's European 2016–18 seed cohort (3,075) reached Series A at 6/18/27/31% cumulatively after 1/2/3/4 years. Carta US cohorts reached 12.9% in one year (2024 Q3) and 32.7% in two years (2021 Q1), different vintages. Base incidence 10/22/31/36% interpolates scenario anchors, not an estimated cohort. The competing-risk conversion uses remaining seed risk mass (not 1 minus cumulative financing alone).

```math
g_k=\frac{F_k-F_{k-1}}{U_{k-1}},\quad U_k=U_{k-1}(1-g_k-b_k-h_k)
```

```math
\mathbf n_{t+1}=\mathbf n_tP_t+B_t\mathbf e_0,\quad \sum_j P_{ij}=1
```

Base seed→scaleup hazards by tenure are 10/16.91/19.79/17.97/3.5%; seed→SME 4%; closure 15.03%. Scaleup→SME/large 12/2%, SME→large 0.5%, large→SME 0.5%, all operational transitions assumed. Census high-growth share (under 8% among young continuing firms in 2020) is a reality check, not a maturation probability. 1,000 newly seed-funded firms in base year 10: 37.9 remain seed, 64.3 scaleup, 193.0 SME, 34.4 large, 670.4 closed. Not an observed cohort.

NVCA 2025 US pre-seed/seed: 5,049 deals, $22.3B. Base assumes global eligible multiplier 2, unique-company factor .75, Claude capture .25, 5% of average round spent annually on Claude. Potential newly paying firms 1,893 and revenue ceiling $0.418B/year. Deals are not unique births and ARPA is not observed. Non-VC births, customer reacquisition, M&A and correlations remain unresolved.

```math
B_t=D_{US}G u c,\quad A=\frac{K_{US}}{D_{US}}f,\quad R_{birth,t}=\min(0.2J_t,B_tA)
```

Revenue migration assumes transition independent of invoice size within each state; baseline upgrade spend multiplier 1.35 and downgrade 0.75.

The joint tensor has 8 live lifecycle states × 3 dwell buckets × 3 latent health states × 7 vendor states (504 customer combinations); there are 3 common macro regimes.

### 5.3 Latent health and duration dependence

```math
\pi_{0,h|y}=\frac{\pi_{0,h}P(y|h)}{\sum_k\pi_{0,k}P(y|k)},\qquad P(y=1|h)=(.15,.75,.25)
```

Normal health transition rows: (.67,.23,.10), (.18,.62,.20), (.04,.10,.86). Winter tilts toward distress, boom away. Conditional health death multipliers 1.6/1/.55 and spending .75/1/1.10 are assumptions applied annually. Non-seed duration buckets 0/1/2+ multiply promotion by .55/1/1.20; seed duration already represented in prior chain, no second seed duration multiplier. All current/new invoice cohorts start at dwell zero for non-seed (unknown actual tenure); reset on group change.

### 5.4 Macro regime and correlated risk

```math
P_Z=\begin{pmatrix}.60&.35&.05\\.18&.67&.15\\.08&.42&.50\end{pmatrix}
```

Regime order winter/normal/boom; death multipliers 1.5/1/.75, promotion and new-sales/birth multipliers .65/1/1.25. Not estimated: Carta 2023 funding fell 50%, deal count 24%; Q1 2024 closure count rose 58%, seed 102%, A 61%, B 133%, not closure hazards. Shared regime induces correlation; no additional idiosyncratic firm risk or parameter uncertainty simulated.

### 5.5 Vendor competition, token pricing and deployment

Vendor states Claude-only, multi-with-Claude, OpenAI, Google, self-hosted, other, none; reward (1,.60,0,0,0,0,0). Ramp January 2026 79% of Claude payer accounts also pay OpenAI, used as equal gross budget initialization proxy normalized to actual Claude mass; not observed spend fraction. September 8% monthly firms changed top provider (not cancellation). Menlo 2026 estimates API spend shares 55/31/9% Claude/OpenAI/Google; not transition probabilities. Existing conditional commercial churn is routed to other providers/dormancy once, never additionally multiplied. Exit destination shares .35/.25/.15/.10/.15; reacquisition .06 annually from rivals and .035 from none (normal regime). Multi↔single conditional switches .12/.04, all assumptions. Rival states are aggregate competing destinations, not exclusive real-world vendor portfolios. Initial rival mass zero; new acquisitions and reactivation coexist, no finite outside market measured and possible overlap cannot be empirically resolved.

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
G(L,p,m,r)=L\left[pm+(1-p)r\right]
```

| Symbol | Definition |
|---|---|
| $L$ | Existing pilot revenue |
| $p$ | Successful deployment fraction, assumed revenue-weighted |
| $m$ | Spend expansion conditional on success |
| $r$ | Residual spend of unsuccessful projects |

The implemented forecast sets $r=0$ and transfers successful pilots into the live deployment ledger (not the mature firm state):

```math
G_t=p\,m\,L_{t-1}
```

Break-even example:

```math
G(100,0.25,4,0)=100
```

Evidence: [Gartner project abandonment](https://www.gartner.com/en/articles/genai-project-failure), [McKinsey enterprise AI impact](https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai-2025), [ChartMogul downstream retention](https://chartmogul.com/reports/saas-retention-the-ai-churn-wave/). Project-count abandonment, EBIT impact and software NRR measure different outcomes; none directly identifies the revenue-weighted $p$.

### 5.6 Revenue recursion and new customer acquisition

Let d denote growth fade, n acquisition growth, rho maturity replacement. L, T and B are live, pilot and employer-seat tensors; r is the vendor reward and ℛ its weighted sum. Planned loss uses group retention s; macro growth multiplier x scales new sales.

```math
\mathcal R(X)=\sum_{i,d,h,v}X_{idhv}r_v,\qquad \mathcal L(X)=\sum_{i,d,h,v} X_{idhv}r_v(1-s_i)
```

```math
J_t^{API}=x_{Z_t}[nd_t\mathcal R(L+T)+\rho(1-d_t)\mathcal L(L+T)]
```

```math
J_t^{seat}=x_{Z_t}[nd_t\mathcal R(B)+\rho(1-d_t)\mathcal L(B)]
```

```math
J_t^{birth}=\min(0.2J_t^{API},\mathrm{BirthBudget}_t),\qquad J_t^{existing}=0.8J_t^{API}
```

```math
\alpha_t=0.1+0.5d_t,\quad F_{i,t}=1+(f-1)d_t\;\;(i\in \mathrm{startup/scaleup})
```

```math
K_t=[1+(v-1)d_t][1-(1-q)d_t]
```

```math
L_t=\mathcal K_{Z_t}([(L_{t-1}+pmT_{t-1})F_t K_t H]M_{Z_t})+(1-\alpha_t)A_t
```

```math
T_t=\alpha_t A_t,\quad B_t=\mathcal K_{Z_t}([B_{t-1}F_t(1+bd_t)H]M_{Z_t})+A_t^{seat}
```
A allocates existing-firm acquisition by group and new seed revenue only to Seed0. H is latent-state spend multiplier; F=1 for other firms. Seats and API invoices are not unique customer counts. If the industry ceiling binds, scale all three tensors proportionally (including zero-reward opportunity mass). Vendor transitions already include commercial churn; no additional share fade.

## 6. Compute commitments and free cash flow

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

## 7. Anthropic lifecycle continuation value

```math
p_D=1-(1-0.08)^{1/5}=0.01654,\quad p_{\mathrm{distress,proxy}}=p_D(0.045+0.035)=0.001323
```

BCG's 30,000+ US-listed firms show 8% all-cause five-year delisting for revenue over 3.5B. Daepp et al. report 4.5% bankruptcy and 3.5% liquidation among recorded exits across a different historical population. Their product is a cross-sample distress proxy, not an estimated Anthropic-specific hazard. Historical large-US outright failure was 0.09% per year, an independent order-of-magnitude check. The bear case treats all delistings as zero recovery (deliberately severe), not a claim that acquisitions destroy value. Decline/renewal rates remain uncalibrated and exit applies only after year ten; no M&A recovery is credited. These are bounds/sensitivities, not statistical confidence intervals.

Sources: [IDC 2024 AI primer](https://info.idc.com/rs/081-ATC-910/images/DA-Market-Primer-AI-and-GenAI.pdf), [Menlo 2026](https://menlovc.com/perspective/2026-the-state-of-enterprise-ai/), [BCG 1975–2025](https://www.bcg.com/publications/2026/why-do-companies-fail-us-failure-rates), [Daepp et al. 2015](https://doi.org/10.1098/rsif.2015.0120), [large UK listed corporations study (also reports historical large-US benchmark)](https://doi.org/10.1080/00076791.2021.1893696).

### 7.1 Why replace the Gordon Growth Model?

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

## 8. Validation and sensitivity analysis

| Comparison / ablation | Equity residual |
|---|---:|
| Base, normal regime | 187.05 |
| Without latent health | 155.27 |
| Without additional duration | 187.04 |
| Without explicit vendor transitions | 184.23 |
| All disabled (open lifecycle) | 134.40 |
| Constant winter | 70.06 |
| Constant boom | 187.11 |

Reduced-model references: lifecycle DCF 180.47; Netflix constraint 180.27; industry and exit 172.04; customer cohorts 150.07; open lifecycle 134.40. Structural differences are not single-factor causal effects. In the cohort comparison, closure only 187.11, with commercial churn 150.07; additional top-five cuts of 25/50/100% yield 125.33/100.59/51.10. Open lifecycle without migration 112.04, without new seed entrants 129.88.

### 8.1 Structural scenario inputs (assumptions)

| Parameter | Bear | Base | Bull |
|---|---:|---:|---:|
| Early/scaleup/SME/large weights | 30/30/25/15% | 15/25/30/30% | 5/15/30/50% |
| Pilot fraction | 25% | 30% | 20% |
| GTM success/rollout | .20/2 | .35/3 | .50/4 |
| Initial volume/price multipliers | 1.45/.65 | 1.65/.78 | 1.85/.88 |
| Acquisition rate/maturity replacement | .10/.50 | .20/1 | .30/1.25 |
| Subscription growth | 3% | 12% | 22% |
| Compute/other/capex | .65/.35/.06 | .48/.25/.06 | .35/.20/.05 |
| Tail exit/decline/renewal | .01654/.30/.03 | .001323/.20/.08 | .0009/.10/.15 |
| WACC | 15% | 12% | 10% |

### 8.2 Point-in-time company-specific validation

Freeze the universe at the [September 8, 1999 top-ten market-cap ranking](https://www.internetnews.com/it-management/new-internet-giants-roam-the-street/), including the bankrupt and acquired issuers. [Vintage inputs](data/dotcom_vintage.csv) contain estimates from the [September 1999 Bear Stearns report, Exhibit 2](https://people.duke.edu/~charvey/Teaching/BA491_2000/Cc/Cc_BS.pdf) and separately identified SEC holdout outcomes. Blank cells are missing, not zero. The five available comparable CY2000 analyst forecasts have mean absolute percentage error 24.87%; this is an **external benchmark**, not validation of our joint-state model. Five lack comparable external forecasts. Acquisition/merger and fiscal-year scope must be reconciled before longer-horizon scoring.

```math
\operatorname{MAPE}=\frac1n\sum_i\left|\frac{\widehat R_i-R_i}{R_i}\right|
```

The same joint transition engine now accepts an explicit company profile (initial ledgers, customer weights and retention, transition and vendor kernels, reward, births, market limits, costs and lifecycle tail). Missing profiles fail rather than borrowing Claude parameters. The formerly proposed normalized transfer is not a company-specific forecast and must not be counted as validation. Firm-level bankruptcy and acquisition need separately estimated absorbing states; the present customer-exit process is not such an estimator.

The [ten-company fiscal-year panel](data/dotcom_fy_panel.csv) and [executable evaluation](evaluation/company_oos.py) now run a reduced-state ablation of the actual joint transition operator. With each issuer's own FY1998–99 revenue and identical 50% log-growth shrinkage and seven-year fade:

```math
\widehat R_{i,t}=\widehat R_{i,t-1}\exp\left[0.5\log(R_{i,1999}/R_{i,1998})\max(0,1-(t-1)/7)\right]
```

| Test | n | MAPE | WAPE | Within 20% |
|---|---:|---:|---:|---:|
| FY2000 nowcast | 10 | 21.54% | 19.41% | 50% |
| FY2001–04 future holdouts | 23 | 304.61% | 64.35% | 13.04% |
| One-year half-life stress, FY2001–04 | 23 | 87.72% | 33.48% | 26.09% |

FY2000 flat-revenue and unattenuated-growth baselines have MAPE 50.23% and 129.32%. Seven original/reconciled input vintages yield 21.35% MAPE; three are retrospectively reconstructed. FY2000 overlaps the information-release dates, so it is a nowcast, not a fully prospective test. Missing post-merger or post-bankruptcy observations are censored, not treated as zero. The post-hoc half-life stress is not an independently validated calibration. Leave-one-company-out persistence fitted on FY1997–99 only yields 121.83% FY2000 MAPE and 88,714.78% FY2001–04 MAPE; boom-period growth persistence is not transferable.

This is **not** a full customer-state or equity valuation backtest: aggregate revenue cannot identify customer-level acquisition, churn, pricing, costs or firm failure. Recall cannot be computed without defined and predicted failure labels. The long-horizon result rejects the aggregate growth extrapolation.

#### Five-year endpoint (FY1999 to FY2004)

[Supplemental SEC financial statements](data/dotcom_five_year.csv) provide eight comparable reported endpoints; AOL merger and Excite bankruptcy remain censored. No failure prediction is scored. The original fixed-fade MAPE/WAPE are 1,106.82%/230.14%; one-year half-life 120.15%/49.06%; flat 73.03%/61.19%.

The reduced-state calibration caps the initial log growth and then decays it:

```math
g_{i,0}=\operatorname{clip}(\alpha\ln(R_{i,1999}/R_{i,1998}),-c,c),\quad g_{i,t}=g_{i,0}2^{-(t-1)/h}
```
```math
\widehat R_{i,t}=\widehat R_{i,t-1}\exp(g_{i,t})
```

Leave out the target issuer entirely and minimize mean absolute log error over other issuers' FY2000–03 outcomes; no FY2004 outcome enters the fit. Five-year MAPE/WAPE 76.48%/41.08%. This is retrospective cross-company transfer and a terminal-year holdout, NOT a 1999-vintage calibration. A mature-growth extension worsens MAPE to 94.52%. The flat baseline remains better on MAPE. [Executable evaluation](evaluation/five_year.py).

#### Alternative growth models

The [model comparison](evaluation/growth_comparison.py) refits each candidate excluding the target issuer and every FY2004 outcome. The previous calibrated model underestimated six of eight issuers. A structural reason is the forced convergence to zero revenue growth, which cannot represent post-bubble demand recovery. Partial-year FY1998 sales and acquisitions further limit comparability. The alternative pooled recovery model uses:

```math
\ln(\widehat R_{i,t}/R_{i,0})=a(1-2^{-t})+bt
```

Ridge extensions use initial growth (neutralized for partial-year observations), log size and business-type indicators; Huber IRLS limits outliers. The fixed equal-weight geometric blend of the previous saturation and pooled recovery forecasts is:

```math
\widehat R_{i,t}^{blend}=\sqrt{\widehat R_{i,t}^{sat}\widehat R_{i,t}^{rec}}
```

| Model | MAPE | WAPE | Underpredicted |
|---|---:|---:|---:|
| Previous saturation | 76.48% | 41.08% | 6/8 |
| Pooled trend | 110.80% | 191.72% | 2/8 |
| Pooled recovery | 54.85% | 78.74% | 5/8 |
| Ridge growth | 123.98% | 60.57% | 2/8 |
| Ridge sector | 156.61% | 99.96% | 2/8 |
| Ridge partial-year | 128.08% | 49.61% | 3/8 |
| Huber recovery | 54.59% | 72.15% | 6/8 |
| Huber size | 108.82% | 68.02% | 2/8 |
| Geometric ensemble | 85.18% | 78.11% | 3/8 |
| Saturation/recovery blend | 59.69% | 39.72% | 5/8 |

Model selection on these same eight endpoints is exploratory; another cohort is required for an unbiased performance estimate. The pooled recovery model is not a company-specific lifecycle calibration and the blend is not a validated valuation model. Do not transplant its coefficients into Anthropic; separately estimate industry adoption, market share, monetization and margins from company-specific evidence.

#### Company fundamentals and six-year validation

[Company fundamentals and FY2005 outcomes](data/dotcom_fundamentals.csv) add nine sourced FY1999 gross margins, eight FY2005 revenues, and an explicitly missing Excite margin (training-fold median only). Some FY1999 accounting inputs are retrospective; ICG's FY2005 continuing-operation scope differs. No target issuer outcome, FY2004 or FY2005 outcome enters fitting. In each fold, the recovery regression adds log FY1999 revenue and/or gross margin to the sustained growth term. The size blend is a geometric average of the size forecast and the prior saturation/recovery blend.

| Candidate | FY2004 MAPE | FY2005 MAPE | FY2004 WAPE | FY2005 WAPE |
|---|---:|---:|---:|---:|
| Fixed fade | 1106.82% | 1413.94% | 230.14% | 286.64% |
| Flat | 73.03% | 76.05% | 61.19% | 67.81% |
| Saturation | 76.48% | 82.39% | 41.08% | 51.12% |
| Recovery | 54.85% | 59.36% | 78.74% | 72.98% |
| Gross margin | 55.29% | 60.39% | 89.16% | 83.43% |
| Size | 73.09% | 97.83% | 21.66% | 39.01% |
| Margin and size | 72.95% | 95.18% | 26.87% | 34.27% |
| Saturation/recovery blend | 59.69% | 63.89% | 39.72% | 39.22% |
| Size blend | 62.04% | 71.47% | 29.98% | 31.82% |

This new terminal year tests horizon robustness, not an independent issuer cohort. Gross margin does not consistently improve revenue predictions and should instead be tested in the cash-flow layer. Size improves dollar-weighted error but does not reliably improve relative error. No fitted Anthropic valuation change is justified. [Reproduction](evaluation/fundamental_growth.py).

#### Independent issuer cohort (five-year endpoint)

Eight additional issuers were identified from the contemporary December 1999 article *Internet Stocks, Naughty And Nice*: BroadVision, CMGI, DoubleClick, Exodus, Go2Net, InfoSpace, RealNetworks and VeriSign. The original ten issuers alone fit parameters using FY2000–03; prior WAPE selected the size blend as primary. Six standalone FY2004 endpoints are available; Exodus bankruptcy and Go2Net acquisition are censored, not treated as zero revenue. Retrospective accounting restatements and acquisitions mean this is issuer-external, not strict time-external validation.

| Model | MAPE | WAPE | Within 20% |
|---|---:|---:|---:|
| Flat | 57.35% | 69.97% | 16.67% |
| Original | 161.72% | 94.95% | 0% |
| Saturation | 71.75% | 60.21% | 33.33% |
| Recovery | 145.28% | 95.77% | 0% |
| Size | 206.95% | 115.68% | 16.67% |
| Blend | 102.22% | 74.16% | 0% |
| Size blend (primary) | 146.96% | 92.10% | 0% |

The primary model fails to generalize; saturation improves weighted error but flat wins MAPE. Do not promote a new winner from this holdout. These are revenue errors conditional on standalone survival, not equity-value errors. The next validation must address competing exit states, organic versus acquired revenue and independent calendar windows.

[Data and filing links](data/dotcom_external_cohort.csv) · [Reproduction](evaluation/external_validation.py)

#### Competing exits and acquisition scope

Estimate separate standalone, bankruptcy and merger endpoint probabilities from the original ten issuers (8/1/1) with a symmetric Dirichlet(0.5) prior. The annual constant-hazard matrix reproduces the five-year cumulative probabilities. Recovery or merger consideration is not assumed zero. The valuation expression is an extension specification, not an identified Anthropic hazard or implemented change to base DCF.

$
\widehat p_k=\frac{n_k+1/2}{N+3/2},\quad s=\widehat p_S^{1/5},\quad q_k=(1-s)\frac{\widehat p_k}{1-\widehat p_S}
$

$
P=\begin{pmatrix}s&q_B&q_M\\0&1&0\\0&0&1\end{pmatrix}
$

$
V_0=\mathbb E\left[\sum_{t=1}^{\min(T,\tau)}\frac{FCFF_t}{(1+r)^t}+\frac{L_\tau\mathbf1_{\tau\le T}}{(1+r)^\tau}\right]
$

$
R_t=R_t^{organic}+R_t^{acquired}-R_t^{disposed}
$

$
\Delta NPV=p_{close}\left(\sum_{t=1}^{H}\frac{\Delta FCFF_t}{(1+r)^t}-C_{deal}\right)
$

| Five-year state | Posterior mean | External observed |
|---|---:|---:|
| Standalone | 73.91% | 75% |
| Bankruptcy | 13.04% | 12.5% |
| Merger | 13.04% | 12.5% |

External multiclass Brier score 0.406 versus 0.500 always standalone and 0.667 uniform; log loss 0.736 versus 1.099 uniform. Marginal 95% posterior intervals for both exits around 1–37%; the external cohort was previously inspected, so this is retrospective, not a fresh independent test. The model is pooled, not issuer-specific.

Revenue scope audit: PayPal accounted for 20.21% of eBay's 2003 revenue; Jamba accounted for 15.50% of VeriSign's 2004 revenue. Removing Jamba alone reduces VeriSign saturation APE from 84.19% to 81.28%, so acquisitions explain only part of the miss. Yahoo's US incremental acquisition revenues are a different metric and are not pooled with segment revenue. Ex-component revenue is not complete organic revenue. Future deal probabilities, prices and costs must be estimated separately; disclosed realized acquisitions cannot be fed into an earlier forecast. Negative NPV deals reduce value. No validated equity estimate change.

[Exit evidence](data/dotcom_exit_events.csv) · [Acquisition evidence](data/dotcom_acquisition_components.csv) · [Model](evaluation/competing_risk.py)

#### Financial factors and covariance regularization

Features: 1999 log revenue, clipped 1998–99 log growth, gross margin, operating cash flow/revenue. Coverage among 16 inputs: 16/14/11/8. Missing/partial-year values are training-fold median-imputed; annualized liquidity is not used because comparable cash-only values are insufficient. Retrospective restatements remain. Correlations in the imputed original cohort: size/growth −0.825, gross/CFO margin +0.671. VIF 3.41/3.55/1.88/1.98. Covariance is not itself a defect: compare Ridge, shrink-whitening, PCA regression and ordered residualization; projection is training-only and orthogonal in training, not necessarily in new regimes. Hyperparameters and method selection use nested issuer folds on 2000–03 only, with equal issuer weights. No 2004 endpoint training. Prior external cohort was inspected; these are retrospective diagnostic comparisons.

$
z_{ij}=(x_{ij}-\mu_j)/\sigma_j,\qquad C=Z^\top Z/n
$

$
C_\alpha=(1-\alpha)C+\alpha I,\qquad \widetilde Z=Z C_\alpha^{-1/2}
$

$
z_j^\perp=z_j-Z_{<j}(Z_{<j}^\top Z_{<j})^+Z_{<j}^\top z_j
$

$
\widehat\beta=\arg\min_\beta\sum_i w_i(y_i-X_i\beta)^2+\lambda\|\beta_F\|_2^2
$

$
\widehat R_{it}=R^{sat}_{it}\exp\left[(1-2^{-t})(b_0+z_i^\perp b)\right]
$

| Model | Original MAPE | Original WAPE | External MAPE | External WAPE |
|---|---:|---:|---:|---:|
| OLS | 63.62% | 63.95% | 643.21% | 317.98% |
| Ridge | 67.68% | 62.00% | 289.60% | 138.37% |
| Covariance shrinkage | 57.85% | 32.65% | 213.92% | 116.94% |
| PCR | 67.05% | 35.08% | 147.66% | 89.91% |
| Orthogonal residuals | 52.27% | 18.62% | 227.48% | 123.28% |
| Saturation | 76.48% | 41.08% | 71.75% | 60.21% |
| Anchored residual correction | 78.41% | 50.96% | 84.68% | 63.45% |
| Nested method selection | 64.77% | 36.41% | 227.48% | 123.28% |

Orthogonal residuals improve original WAPE but fail externally; anchored correction is less unstable but does not beat uncorrected saturation. Do not deploy factor coefficients to Anthropic. Cash runway, debt maturity, concentration, share and price need comparable historical and Anthropic-specific inputs before estimation. No change to valuation. [Financial data](data/dotcom_cash_factors.csv) · [Code](evaluation/covariance_factors.py)

#### Capital intensity, development expenditure and liquidity

Add historical capex/revenue, development/revenue (not measured R&D efficiency), cash equivalents/revenue and inverse runway proxy. Coverage 10/10/8/8 of 16; CFO coverage now 10. Four issuers disclose whether a customer is at least 10%; record but do not fit due to insufficient coverage. No inferred debt, market share or elasticity. Amazon technology/content is broader than R&D; accounting scopes differ. Group ablation uses training-only median-free observed mean scaling, missing standardized signals zero, covariance shrink whitening and coverage weights; nested issuer folds choose ridge and whitening parameters using 2000–03 only. The one-standard-error rule is a conservative heuristic, not a formal confidence interval. Previously inspected external cohort is diagnostic.

$
x_{\mathrm{capex}}=\frac{Capex}{R},\quad x_{\mathrm{dev}}=\frac{Development}{R},\quad x_{\mathrm{cash}}=\log(1+Cash/R)
$

$
x_{\mathrm{burn}}=\log\left(1+\frac{\max(0,Capex-CFO)}{Cash}\right)
$

$
Z^*=Z[(1-\alpha)C+\alpha I]^{-1/2}D,\quad D_{jj}=\sqrt{coverage_j}\mathbf1_{coverage_j\ge0.5}
$

$
\widehat R_{it}=R^{sat}_{it}\exp\left[\operatorname{clip}((1-2^{-t})Z_i^*\widehat\beta,-1,1)\right]
$

$
\widehat M=\arg\min_{M: L_M\le L_{best}+SE_{best}}d_M
$

| Model | Original WAPE | External WAPE |
|---|---:|---:|
| Saturation | 41.08% | 60.21% |
| Baseline factors | 47.72% | 72.14% |
| Investment | 41.25% | 60.18% |
| Liquidity | 48.58% | 66.40% |
| All factors | 53.33% | 60.21% |
| No liquidity | 51.26% | 60.16% |
| No investment | 51.86% | 63.82% |
| Nested selection | 51.57% | 66.40% |
| One-standard-error rule | 39.96% | 60.21% |

No meaningful external improvement; conservative selection recovers saturation externally, while original WAPE improves 1.12 percentage points. No fitted coefficient transfer or valuation change. Anthropic stored filing inputs imply 9m CFO margin 19.76%, capex ratio 2.78%, CFO minus capex $5.644B, cash/investments versus next-12-month gross commitments 1.86x, through-2030 commitments/cash 3.43x, financing/CFO 16.86x, top-five direct customer share 25% and HHI lower bound 0.0125. Gross commitment coverage is not runway or a net cash forecast; cash includes investments and does not match historical cash equivalents. CFO less capex is not FCFF, and compute leases/commitments require separate cash timing without double counting. [Data](data/dotcom_structural_factors.csv) · [Code](evaluation/structural_factors.py)


#### Cross-cycle cloud validation (FY2020–FY2025)

The [Bessemer State of Cloud 2020](https://www.bvp.com/atlas/state-of-the-cloud-2020) identified five public cloud companies above $50B market cap: Adobe, Salesforce, PayPal, ServiceNow, Shopify. Select all five, not later winners. FY2019/20 SEC filings are inputs; FY2025 SEC filings are outcomes. Forecast origin is after FY2020 reporting, not January 2020. See [data](data/cloud_cycle_cohort.csv).

The previous size blend is frozen before this test:

```math
\widehat R_5=\widehat R_{size}^{1/2}(\widehat R_{sat}\widehat R_{recovery})^{1/4}
```

An endpoint prior fits the original and independent 1999 issuers with observed 2004 endpoints, minimizing mean absolute log error plus a fixed mature-growth penalty:

```math
L(\theta)=\frac1n\sum_i|\log(\widehat R_{i,5}(\theta)/R_{i,5})|+0.5|g_{\infty}|
```

| Model | WAPE | MAPE | Signed bias |
|---|---:|---:|---:|
| Flat | 50.81% | 55.34% | -50.81% |
| Original | 25.16% | 27.52% | -25.16% |
| Saturation | 38.12% | 42.01% | -38.12% |
| Endpoint prior | 31.02% | 34.18% | -31.02% |
| Size | 20.74% | 23.36% | -20.74% |
| Blend | 18.61% | 21.70% | +2.84% |
| Frozen size blend | 16.25% | 19.58% | -9.86% |
| Fixed 15% log growth diagnostic | 15.94% | 17.10% | +7.28% |

The 15% floor is an exploratory sensitivity, not a validated winner or a perpetual terminal growth rate. The frozen blend remains the benchmark; no Anthropic valuation adjustment is justified by these five surviving, large and heterogeneous issuers. This validates consolidated revenue only, not cash flow or equity value. Historical inputs may include retrospective restatements; cloud data have FY-specific cutoffs and M&A effects. No cloud outcomes enter the forecast fit (tested). Run `python -m evaluation.cloud_cycle`.

### 8.3 Anthropic-specific filing calibration and accounting sensitivity

The [final prospectus](https://www.sec.gov/Archives/edgar/data/2130357/000162828026074944/anthropicpbc-424b4.htm) and [operating expense table](https://www.sec.gov/Archives/edgar/data/2130357/000162828026073045/anthropicpbc-fwpjapanamend.htm) support the [company-specific anchors](data/company_specific_anchors.csv): 11,900+ customers above $100k TTM, 1,900+ above $1m, about 250 above $10m, and $26.1B TTM revenue from the first group. Thresholds are nested, not customer life stages. 900% NRR compares corresponding quarterly revenue from existing qualified customers, excluding fixed-price personal plans; it does not identify gross retention or a future growth rate.

```math
c_{\mathrm{compute}}=18.808/33.242=56.58\%,\quad c_{\mathrm{other}}=15.694/33.242=47.21\%
```

```math
\Delta V_{\mathrm{bridge}}=(232.351-109.742)-(212.684-110.873)=20.798\ \mathrm{B}
```

| Base 1,024 paths, seed 42 | Mean equity residual ($B) |
|---|---:|
| Original assumptions, updated pro forma as-adjusted bridge | 184.83 |
| Observed compute expense ratio held constant | 149.22 |
| Both reported expense ratios held constant | -41.19 |

These are sensitivities only: accrual expense includes noncash items, and treating it as a cash ratio indefinitely is not a calibrated FCFF forecast. The updated bridge is a conditional accounting figure, not proof of completed financing or settlement. Customer life-stage weights, cohort transition probabilities, consumer conversion, and sustainable marginal cost are still unidentified. Do not replace the main conditional scenario with a claim of empirically validated fair value.

#### Growth-decay transfer sensitivity

The original joint model's common fade can be replaced with exponential half-life 0.5–2 years. These are stress scenarios informed by the historical folds, not identified Anthropic transition probabilities. Using 128 common macro paths, seed 42, adjusted balance sheet:

| Growth fade | Original cost | Reported compute ratio | Both reported expense ratios |
|---|---:|---:|---:|
| Original | 183.48 | 148.12 | -41.36 |
| 0.5 year | 94.58 | 72.88 | -64.19 |
| 1 year | 127.53 | 101.57 | -53.32 |
| 2 years | 170.41 | 137.33 | -43.42 |

These are mean equity residuals ($B), not validated fair-value estimates. Expense ratios are accrual proxies; no validated equity backtest.

## 9. Reproduction and data

54 local tests pass, including baseline nesting, probability sums, cumulative graduation, population conservation, budget bounds, initial invoices and reproducibility. Reduced-state historical backtest completed; full valuation backtest remains open. Key unidentified inputs: country paid conversion, customer revenue mix, funding provenance, financial transition, market capture and vendor migration.

```bash
python -m models.joint_customer_states
python -m evaluation.company_oos
python -m evaluation.five_year
python -m evaluation.growth_comparison
python -m evaluation.fundamental_growth
python -m evaluation.external_validation
python -m evaluation.competing_risk
python -m evaluation.covariance_factors
python -m evaluation.structural_factors
python -m unittest discover -s evaluation -v
```

- [Main model](models/joint_customer_states.py)
- [Open lifecycle model](models/customer_markov.py)
- [Customer cohorts](models/customer_cohorts.py)
- [Industry calibration](models/industry_calibration.py)
- [Financial observations](data/observations.csv)
- [Industry data](data/industry_spending.csv)
- [Customer risk data](data/customer_risk.csv)
- [Lifecycle data](data/markov_anchors.csv)
- [Joint-state data](data/joint_state_anchors.csv)
- [Data definitions](data/README.md)
- [Tests](evaluation/test_joint_customer_states.py)
