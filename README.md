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
| Bull | 164.10 | 1230.83 | 5344.34 | 5446.15 |

Negative residual equity signals funding distress, not a negative tradable share price. The bull outcome exposes how extreme compounding of successful projects and new demand changes the output; it is not a supported forecast. A $2T equity benchmark is therefore not justified merely by current adoption or annualized revenue; it requires assumptions about durable demand, prices and margins that remain unverified. At a 12% discount rate, 3% perpetual growth and 25% FCFF margin, a steady-state $2T EV requires $720B next-year revenue (reverse DCF, ignoring interim cash flows). The $2T reference is hypothetical, not a verified current market cap.

## How the valuation works

1. **Separate observations from assumptions.** [Data register](data/observations.csv) records source, period, unit and scope. [Data notes](data/README.md) explain identification limits.
2. **Consumer demand.** For each country × age × income cohort, revenue = population × internet access × conditional AI adoption × paid conversion × Claude share × monthly price × 12. Pew US age-group usage and ITU connectivity are proxies, not paid rates. Exclude unsupported markets; never treat free use as paid demand. The function is implemented, but global paid conversion and country population cohorts are not calibrated yet.
3. **Enterprise demand.** Sum employee counts × adoption × mean per-employee monthly spend × model share × 12 across industries. Ramp's median is not a mean and cannot be multiplied by the global workforce. Keep the bottom-up model separate from the run-rate model until data reconcile.
4. **Startup survival and capital recycling.** Separate startup, trial and mature consumption cohorts. Startup retained spend = prior spend × revenue-weighted survival × conditional funding/spend multiplier × volume × price × share. BLS survival is a historical establishment proxy; actual AI customer survival is unobserved. Ramp shows top-1% concentration and JPMorgan shows VC-backed company counts; multiplying these two statistics is invalid. External customer cash, not gross cross-investment, is the relevant ultimate funding source.
5. **GTM conversion.** Trial spend is transferred to mature deployment only if successful, multiplied by rollout expansion; failed trials can have residual spend in the standalone formula. Gartner abandonment and McKinsey EBIT survey measure different outcomes and cannot be multiplied. ChartMogul downstream NRR is a warning indicator, not Anthropic NRR.
6. **Price and competition.** Consumption revenue = token quantity × realized price × provider share. A 50% price decline requires 100% quantity growth just to hold revenue fixed. Model switching, open models and custom hardware can drive correlated share and pricing pressure.
7. **Costs and cash flow.** Compute cost is the maximum of a commitment floor and variable usage cost; other cash opex and capex are separate assumptions. Commitments are allocated approximately across disclosed time buckets, not a contractual annual payment schedule; treat cloud leases/prepayments carefully to avoid double counting. Simplified cash tax 25%, no tax benefit during losses, no explicit working capital or financing schedule. Historical CFO less PPE purchases = $5.644B for nine months; subtracting lease prepayments gives $3.689B as a separate cash measure, neither is normalized FCFF.
8. **DCF.** Discount ten years of modeled cash flow and a normalized Gordon terminal value. The illustrative equity bridge uses pro forma cash less convertible carrying value; the final IPO proceeds, conversion/payoff terms, leases, minority claims and diluted shares need further reconciliation. No per-share estimate.
9. **Correlated uncertainty.** Seeded simulation shares a common scenario factor across funding, price, competition and cost inputs; it is a scenario interpolation, not a fitted probability distribution. Its P10/P50/P90 residual equity values are -34.36 / 372.06 / 1664.25; do not interpret as statistical confidence intervals.

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
