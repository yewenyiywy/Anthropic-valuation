"""Transparent scenario engine. Currency: USD billions, unless specified."""
import csv
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def observations():
    with (ROOT / "data/observations.csv").open() as file:
        return {r["id"]: float(r["value"]) for r in csv.DictReader(file)}

def consumer_revenue(population, internet, adoption, paid, market_share, monthly_price):
    """Population in billions, probabilities conditional on previous stage."""
    return population * internet * adoption * paid * market_share * monthly_price * 12

def enterprise_revenue(employees, adoption, monthly_spend, market_share):
    """Employees in billions; spend must be mean, not sample median."""
    return employees * adoption * monthly_spend * 12 * market_share

def survival(s5, years):
    return s5 ** (years / 5)

def cohort(start, survival_probability, expansion, price_factor, share_factor):
    return start * survival_probability * expansion * price_factor * share_factor

def pilot(start, conversion, expansion, residual=0):
    return start * (conversion * expansion + (1-conversion) * residual)

def reverse_dcf(ev, wacc, growth, margin):
    """Steady-state next-year revenue needed to support EV, no interim years."""
    return ev * (wacc-growth) / margin

# All entries here are illustrative stresses, not measured customer mix or forecasts.
SCENARIOS = {
    "bear": dict(startup=.55, trial=.25, s5=.40, funding=.70, conversion=.20,
                 rollout=2, volume=1.45, price=.65, share=.90, new=.10,
                 subscription_growth=.03, cost_ratio=.65, other_ratio=.35, capex=.06,
                 wacc=.15, terminal_growth=.025),
    "base": dict(startup=.40, trial=.30, s5=.54, funding=.90, conversion=.35,
                 rollout=3, volume=1.65, price=.78, share=.96, new=.20,
                 subscription_growth=.12, cost_ratio=.48, other_ratio=.25, capex=.06,
                 wacc=.12, terminal_growth=.03),
    "bull": dict(startup=.25, trial=.20, s5=.65, funding=1.05, conversion=.50,
                 rollout=4, volume=1.85, price=.88, share=1.0, new=.30,
                 subscription_growth=.22, cost_ratio=.35, other_ratio=.20, capex=.05,
                 wacc=.10, terminal_growth=.035),
}

def forecast(p, o=None, years=10):
    o = observations() if o is None else o
    # October run rate is a starting intensity; segment split is September historical proxy.
    api = o["run_rate"] * o["consumption_9m26"] / o["revenue_9m26"]
    sub = o["run_rate"] - api
    startup, trial = api*p["startup"], api*p["trial"]
    mature = api-startup-trial
    rows = []
    for t in range(1, years+1):
        # Fade net growth drivers toward maturity rather than compound hypergrowth indefinitely.
        fade = max(0, 1-(t-1)/7)
        price = 1-(1-p["price"])*fade
        share = 1-(1-p["share"])*fade
        volume = 1+(p["volume"]-1)*fade
        multiplier = price*share*volume
        previous_api = startup+trial+mature
        startup = startup * survival(p["s5"], 1) * (1+(p["funding"]-1)*fade) * multiplier
        # Successful pilots move into mature cohort, unsuccessful ones are extinguished.
        mature = (mature + pilot(trial,p["conversion"],p["rollout"])) * multiplier
        new = previous_api * p["new"] * fade
        startup += new*.4
        trial = new*.6
        sub *= 1+p["subscription_growth"]*fade + p["terminal_growth"]*(1-fade)
        revenue = startup+trial+mature+sub
        # Cash expense model: commitments are a floor, not added atop variable compute.
        # This allocates aggregate commitments evenly in two buckets (timing proxy).
        floor = (o["commit_next12m"] if t==1 else
                 (o["commit_to_2030"]-o["commit_next12m"])/3.25 if t<=4 else
                 (o["commit_total"]-o["commit_to_2030"])/15)
        compute = max(floor, revenue*p["cost_ratio"])
        other = revenue*p["other_ratio"]
        capex = revenue*p["capex"]
        pretax = revenue-compute-other-capex
        # Simplified cash-tax proxy; no tax benefit for loss; no separate WC forecast.
        fcf = pretax - max(0,pretax)*.25
        rows.append(dict(year=t,revenue=revenue,startup=startup,trial=trial,mature=mature,
                         subscription=sub,compute=compute,commitment_floor=floor,
                         other=other,capex=capex,fcf=fcf))
    w,g = p["wacc"],p["terminal_growth"]
    if w<=g: raise ValueError("WACC must exceed terminal growth")
    # Terminal cap is normalized rather than perpetuating the temporary commitment floor.
    terminal_fcf = rows[-1]["revenue"]*max(0,1-p["cost_ratio"]-p["other_ratio"]-p["capex"])*.75
    tv = terminal_fcf*(1+g)/(w-g)
    ev = sum(r["fcf"]/(1+w)**r["year"] for r in rows)+tv/(1+w)**years
    # Convertible liability treatment is illustrative (carrying value, not payoff),
    # do not add IPO cash twice or report a per-share value without a diluted cap table.
    bridge = o["proforma_cash"]-o["proforma_convertibles"]
    return rows, ev, ev+bridge

def monte_carlo(n=2000, seed=42):
    """Common-factor scenario interpolation; not a statistically estimated distribution."""
    rng=random.Random(seed)
    values=[]
    for _ in range(n):
        z=rng.triangular(-1,1,0)
        side=SCENARIOS["bull" if z>=0 else "bear"]
        p={k:v+(side[k]-v)*abs(z) for k,v in SCENARIOS["base"].items()}
        values.append(forecast(p)[2])
    return sorted(values)

if __name__ == "__main__":
    for name,p in SCENARIOS.items():
        rows,ev,equity=forecast(p)
        print(f"{name}: year 1 revenue {rows[0]['revenue']:.2f}, year 5 {rows[4]['revenue']:.2f}, EV {ev:.2f}, illustrative equity {equity:.2f}")
    v=monte_carlo()
    print("Scenario simulation quantiles P10/P50/P90:",*[round(v[int(q*(len(v)-1))],2) for q in (.1,.5,.9)])
